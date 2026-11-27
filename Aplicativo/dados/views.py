import json
import unicodedata
from datetime import datetime, timedelta
from itertools import chain
from zoneinfo import ZoneInfo
from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.db.models import IntegerField, Q, Value
from django.contrib.auth.decorators import login_required
from .models import Aula
from django.db import transaction
from .forms import AulaForm
from django.shortcuts import get_object_or_404
from .models import Predio, Espaco, Ponto
from django.http import Http404, JsonResponse
from .forms import (
    PesquisaForm,
    PesquisaEspacoForm,
    PesquisaAuditorioForm,
    PesquisaPredioForm,
    PesquisaLaboratorioForm,
    PesquisaMapaForm,
)


def home(request):
    return redirect("mapa")



TIPOS_DE_PIN = {
    "predio", "banheiro", "auditorio", "sala", "laboratorio",
    "biblioteca", "restaurante", "entrada", "elevador", "escada",
}


def _tipo_do_pin(nome_do_tipo):
    """Mesma regra do mapa para escolher a categoria do pin."""
    texto = unicodedata.normalize("NFD", nome_do_tipo)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    palavras = texto.strip().lower().split()
    chave = palavras[0] if palavras else ""
    return chave if chave in TIPOS_DE_PIN else "outro"


def _proxima_aula(usuario):
    """Próxima aula da grade do usuário, contando a que está em andamento.

    Os horários da grade são o relógio de Brasília; o TIME_ZONE do
    projeto é UTC, por isso o fuso é indicado aqui.
    """
    agora = datetime.now(ZoneInfo("America/Sao_Paulo"))
    escolhida = None

    aulas = (
        Aula.objects.filter(usuario=usuario)
        .select_related("sala__andar__predio", "sala__tipo")
    )
    for aula in aulas:
        dias = (aula.dia_semana - agora.weekday()) % 7
        dia = agora.date() + timedelta(days=dias)
        inicio = datetime.combine(
            dia, aula.horario_inicio, tzinfo=agora.tzinfo
        )
        fim = datetime.combine(
            dia, aula.horario_fim, tzinfo=agora.tzinfo
        )
        if fim <= agora:
            inicio += timedelta(days=7)
            fim += timedelta(days=7)
        if escolhida is None or inicio < escolhida[0]:
            escolhida = (inicio, aula)

    if escolhida is None:
        return None

    inicio, aula = escolhida
    hoje = agora.date()
    if inicio.date() == hoje:
        quando = "hoje"
    elif inicio.date() == hoje + timedelta(days=1):
        quando = "amanhã"
    else:
        quando = aula.get_dia_semana_display().lower()

    predio = aula.sala.andar.predio
    return {
        "aula": aula,
        "sala": aula.sala,
        "predio": predio,
        "andar": aula.sala.andar,
        "quando": quando,
        "em_andamento": inicio <= agora,
        "tipo_pin": _tipo_do_pin(aula.sala.tipo.nome),
    }


def _tem_filtro(dados):
    return bool(
        dados["busca"]
        or dados["categoria"] != "todos"
        or dados["predio"]
        or dados["andar"]
    )


def _pins_filtrados(lista, categoria, dados, espacos, pontos):
    """Restringe os pins do mapa aos mesmos filtros da lista.

    Devolve os espaços, os pontos e os ids dos prédios que ficam.
    """
    if categoria == "predio":
        return [], [], set(lista.values_list("pk", flat=True))

    espacos = espacos.filter(
        pk__in=lista.values_list("pk", flat=True)
    )
    # Pontos (banheiro, entrada...) não têm nome de busca nem
    # categoria: só aparecem quando filtra por prédio ou andar.
    if dados["busca"] or categoria != "todos":
        pontos = pontos.none()
    if dados["predio"]:
        pontos = pontos.filter(andar__predio=dados["predio"])
    if dados["andar"]:
        pontos = pontos.filter(andar=dados["andar"])

    ids = set(espacos.values_list("andar__predio_id", flat=True))
    ids |= set(pontos.values_list("andar__predio_id", flat=True))
    return espacos, pontos, ids


def mapa(request):
    predios = (
        Predio.objects
        .filter(latitude__range=(-90, 90), longitude__range=(-180, 180))
        .order_by('nome')
        .values('id_predio', 'nome', 'sigla', 'latitude', 'longitude')
    )

    predios_por_id = {}

    for predio in predios:
        predio_id = predio.pop('id_predio')
        predio['locais'] = []
        predio['url'] = reverse(
            'detalhe_predio',
            kwargs={'id_predio': predio_id}
        )
        predios_por_id[predio_id] = predio

    ids_predios = list(predios_por_id)

    contexto = _contexto_pesquisa(request)
    lista = contexto["lista"]
    filtrando = lista is not None and _tem_filtro(
        contexto["formulario"].cleaned_data
    )

    espacos = (
        Espaco.objects
        .filter(andar__predio_id__in=ids_predios)
        .order_by('nome')
        .values_list(
            'andar__predio_id',
            'nome',
            'tipo__nome',
            'andar__nome',
            'posicao_x',
            'posicao_y',
            'pk'
        )
    )

    pontos = (
        Ponto.objects
        .filter(andar__predio_id__in=ids_predios)
        .order_by('nome')
        .annotate(sem_pagina=Value(None, output_field=IntegerField()))
        .values_list(
            'andar__predio_id',
            'nome',
            'tipo_ponto__nome',
            'andar__nome',
            'posicao_x',
            'posicao_y',
            'sem_pagina'
        )
    )

    if filtrando:
        espacos, pontos, ids_filtrados = _pins_filtrados(
            lista,
            contexto["categoria"],
            contexto["formulario"].cleaned_data,
            espacos,
            pontos,
        )

    for (
        predio_id, nome, tipo, andar, posicao_x, posicao_y, id_espaco
    ) in chain(espacos, pontos):
        predios_por_id[predio_id]['locais'].append({
            'nome': nome,
            'tipo': tipo,
            'andar': andar,
            'posicao_x': posicao_x,
            'posicao_y': posicao_y,
            # Só espaços têm página de detalhe (pontos não).
            'url': (
                reverse('detalhe_espaco', kwargs={'pk': id_espaco})
                if id_espaco else None
            ),
        })

    if filtrando:
        # Só ficam no mapa os prédios com algum resultado.
        predios_por_id = {
            predio_id: predio
            for predio_id, predio in predios_por_id.items()
            if predio_id in ids_filtrados
        }

    contexto.update({
        "predios_mapa": list(predios_por_id.values()),
        "filtros_ativos": filtrando,
        "proxima_aula": (
            _proxima_aula(request.user)
            if request.user.is_authenticated else None
        ),
        "formulario": PesquisaMapaForm(
            request.GET or None,
            auto_id="mapa-%s",
        ),
    })
    return render(request, "Mapa-HTML.html", contexto)


def pesquisa(request):
    predios = Predio.objects.all()

    return render(request, 'pesquisa.html', {
        'predios': predios
    })

def search(request):
    return pesquisa(request)

def _redirecionar_categoria(request, categoria):
    parametros = request.GET.copy()
    parametros["categoria"] = categoria
    destino = reverse("mapa")
    return redirect(f"{destino}?{parametros.urlencode()}")

def predios(request):
    return _redirecionar_categoria(request, "predio")


def predio_por_sigla(request, sigla):
    predio = get_object_or_404(Predio, sigla__iexact=sigla)
    return redirect('detalhe_predio', id_predio=predio.pk)

def iag(request):
    return predio_por_sigla(request, "IAG")

def leme(request):
    return predio_por_sigla(request, "L")

def laboratorios(request):
    return _redirecionar_categoria(request, "laboratorio")

def kennedy(request):
    return predio_por_sigla(request, "Kennedy")

def auditorios(request):
    return _redirecionar_categoria(request, "auditorio")


def laboratorio_fisica(request):
    parametros = request.GET.copy()
    parametros["categoria"] = "laboratorio"
    parametros["busca"] = "Física"
    return redirect(
        f'{reverse("mapa")}?{parametros.urlencode()}'
    )


def laboratorio_design(request):
    parametros = request.GET.copy()
    parametros["categoria"] = "laboratorio"
    parametros["busca"] = "Design"
    return redirect(
        f'{reverse("mapa")}?{parametros.urlencode()}'
    )

def pesquisa_auditorios(request):
    return _redirecionar_categoria(request, "auditorio")


def pesquisa_sala(request):
    return _redirecionar_categoria(request, "sala")


def cadastro(request):
    if request.method == 'POST':
        formulario = UserCreationForm(request.POST)

        if formulario.is_valid():
            usuario = formulario.save()
            login(request, usuario)
            return redirect('home')
    else:
        formulario = UserCreationForm()

    return render(request, 'cadastro.html', {
        'formulario': formulario
    })


def login_view(request):
    if request.method == 'POST':
        formulario = AuthenticationForm(
            request, data=request.POST
        )

        if formulario.is_valid():
            usuario = formulario.get_user()
            login(request, usuario)
            return redirect('home')
    else:
        formulario = AuthenticationForm()

    return render(request, 'login.html', {
        'formulario': formulario
    })


def logout_view(request):
    if request.method == 'POST':
        logout(request)

    return redirect('home')

def auditorio_rdc(request):
    return predio_por_sigla(request, "RDC")

def auditorio_kennedy(request):
    return predio_por_sigla(request, "Kennedy")

def detalhe_espaco(request, pk):
    espacos = Espaco.objects.select_related("andar__predio", "tipo")
    espaco = get_object_or_404(espacos, pk=pk)

    outros_espacos = (
        Espaco.objects.filter(andar_id=espaco.andar_id)
        .exclude(pk=espaco.pk)
        .select_related("tipo")
        .order_by("nome", "pk")[:4]
    )

    return render(request, "espaco.html", {
        "espaco": espaco,
        "outros_espacos": outros_espacos,
    })


TIPOS = {
    "sala": "sala",
    "laboratorio": "laboratório",
    "auditorio": "auditório",
}


def _contexto_pesquisa(request):
    formulario = PesquisaMapaForm(request.GET or None)
    pagina = None
    lista = None
    categoria = "todos"

    if formulario.is_valid():
        busca = formulario.cleaned_data["busca"]
        categoria = (
            formulario.cleaned_data["categoria"]
        )
        predio = formulario.cleaned_data["predio"]
        andar = formulario.cleaned_data["andar"]

        if categoria == "predio":
            lista = Predio.objects.order_by("nome")
            if predio:
                lista = lista.filter(pk=predio.pk)
            if andar:
                lista = lista.filter(pk=andar.predio_id)
            if busca:
                lista = lista.filter(
                    Q(nome__icontains=busca)
                    | Q(sigla__icontains=busca)
                )
        else:
            lista = (
                Espaco.objects
                .select_related(
                    "andar__predio", "tipo"
                )
                .order_by("nome")
            )
            tipo = TIPOS.get(categoria)
            if tipo:
                lista = lista.filter(
                    tipo__nome__icontains=tipo
                )
            if predio:
                lista = lista.filter(andar__predio=predio)
            if andar:
                lista = lista.filter(andar=andar)
            if busca:
                lista = lista.filter(
                    Q(nome__icontains=busca)
                    | Q(codigo__icontains=busca)
                    | Q(
                        andar__predio__sigla__icontains=busca
                    )
                )

        paginas = Paginator(lista, 5)
        pagina = paginas.get_page(
            request.GET.get("page")
        )

    filtros = request.GET.copy()
    filtros.pop("page", None)

    return {
        "formulario": formulario,
        "pagina": pagina,
        "lista": lista,
        "categoria": categoria,
        "filtros": filtros.urlencode(),
        "atual": request.GET.urlencode(),
    }


def pesquisa(request):
    parametros = request.GET.urlencode()
    destino = reverse("mapa")

    if parametros:
        destino = f"{destino}?{parametros}"

    return redirect(destino)


def detalhe_predio(request, id_predio):
    predio = get_object_or_404(Predio, pk=id_predio)
    andares = list(predio.andares.order_by('numero', 'pk'))
    andar = None
    andar_id = request.GET.get('andar')
    if andar_id:
        andar = next((item for item in andares if str(item.pk) == andar_id), None)
        if andar is None:
            raise Http404('Andar não encontrado neste prédio.')
    elif andares:
        andar = next((item for item in andares if item.numero == 0), andares[0])

    espacos = pontos = ()
    if andar:
        espacos = andar.espacos.select_related('tipo').order_by('nome', 'pk')
        pontos = andar.pontos.select_related('tipo_ponto').order_by('nome', 'pk')

    return render(request, 'base_predio.html', {
        'predio': predio,
        'andares': andares,
        'andar': andar,
        'espacos': espacos,
        'pontos': pontos,
    })


def teste_base(request):
    return redirect("mapa")

def dados_mapa(request):
    espacos = Espaco.objects.select_related(
        "andar__predio", "tipo"
    ).all()

    pontos = Ponto.objects.select_related(
        "andar__predio", "tipo_ponto"
    ).all()

    dados = []

    for espaco in espacos:
        dados.append({
            "id": espaco.id_espaco,
            "nome": espaco.nome,
            "codigo": espaco.codigo,
            "tipo": espaco.tipo.nome,
            "predio": espaco.andar.predio.sigla,
            "andar": espaco.andar.nome,
            "posicao_x": espaco.posicao_x,
            "posicao_y": espaco.posicao_y,
            "acessivel": espaco.acessivel,
            "categoria": "espaco",
        })

    for ponto in pontos:
        dados.append({
            "id": ponto.id_ponto,
            "nome": ponto.nome,
            "tipo": ponto.tipo_ponto.nome,
            "predio": ponto.andar.predio.sigla,
            "andar": ponto.andar.nome,
            "posicao_x": ponto.posicao_x,
            "posicao_y": ponto.posicao_y,
            "categoria": "ponto",
        })

    return JsonResponse(dados, safe=False)

def sugestoes_pesquisa(request):
    """Sugestões de locais para o campo de busca do mapa.

    Usa as mesmas regras da pesquisa (nome, código ou sigla) e só
    devolve locais cujo prédio tem coordenadas, para haver pin.
    """
    termo = request.GET.get("q", "").strip()
    if len(termo) < 2:
        return JsonResponse({"sugestoes": []})

    predios = (
        Predio.objects
        .filter(latitude__isnull=False, longitude__isnull=False)
        .filter(Q(nome__icontains=termo) | Q(sigla__icontains=termo))
        .order_by("nome")[:3]
    )
    espacos = (
        Espaco.objects
        .select_related("andar__predio", "tipo")
        .filter(
            andar__predio__latitude__isnull=False,
            andar__predio__longitude__isnull=False,
        )
        .filter(
            Q(nome__icontains=termo)
            | Q(codigo__icontains=termo)
            | Q(andar__predio__sigla__icontains=termo)
        )
        .order_by("nome")[:6]
    )

    sugestoes = [
        {
            "rotulo": predio.nome,
            "detalhe": f"Prédio · {predio.sigla}",
            "tipo_pin": "predio",
            "local": f"{predio.sigla} — {predio.nome}",
            "lat": str(predio.latitude),
            "lng": str(predio.longitude),
        }
        for predio in predios
    ] + [
        {
            "rotulo": espaco.nome,
            "detalhe": (
                f"{espaco.codigo} · {espaco.andar.predio.sigla}"
                f" · {espaco.andar.nome}"
            ),
            "tipo_pin": _tipo_do_pin(espaco.tipo.nome),
            "local": espaco.nome,
            "lat": str(espaco.andar.predio.latitude),
            "lng": str(espaco.andar.predio.longitude),
        }
        for espaco in espacos
    ]
    return JsonResponse({"sugestoes": sugestoes})


@login_required(login_url="login")
def minha_grade(request):
    aulas = (
        Aula.objects.filter(usuario=request.user)
        .select_related("sala__andar__predio", "sala__tipo")
    )
    return render(request, "grade.html", {
        "aulas": aulas,
        "formulario": AulaForm(),
        "titulo": "Cadastrar aula",
    })

@login_required(login_url="login")
def cadastrar_aula(request):
    formulario = AulaForm(
        request.POST if request.method == "POST" else None
    )

    if request.method == "POST" and formulario.is_valid():
        dados = formulario.cleaned_data

        with transaction.atomic():
            for dia in dados["dias_semana"]:
                Aula.objects.create(
                    usuario=request.user,
                    disciplina=dados["disciplina"],
                    dia_semana=dia,
                    horario_inicio=dados["horario_inicio"],
                    horario_fim=dados["horario_fim"],
                    sala=dados["sala"],
                )

        return redirect("minha_grade")

    return render(request, "grade.html", {
        "formulario": formulario,
        "titulo": "Cadastrar aula",
    })

@login_required(login_url="login")
def editar_aula(request, pk):
    aula = get_object_or_404(
        Aula, pk=pk, usuario=request.user
    )
    formulario = AulaForm(
        request.POST if request.method == "POST" else None,
        instance=aula,
    )

    if request.method == "POST" and formulario.is_valid():
        formulario.save()
        return redirect("minha_grade")

    return render(request, "grade.html", {
        "formulario": formulario,
        "titulo": "Editar aula",
    })


@login_required(login_url="login")
def remover_aula(request, pk):
    aula = get_object_or_404(
        Aula, pk=pk, usuario=request.user
    )

    if request.method == "POST":
        aula.delete()
        return redirect("minha_grade")

    return render(request, "grade.html", {
        "aula": aula,
        "confirmar_remocao": True,
    })

import json
import os
import urllib.error
import urllib.request

from django.conf import settings

ROTAS_URL = (
    "https://routes.googleapis.com/"
    "directions/v2:computeRoutes"
)


def _numero(valor, minimo, maximo):
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        return None
    if minimo <= numero <= maximo:
        return numero
    return None


def rota_a_pe(request):
    lat = _numero(
        request.GET.get("origem_lat"), -90, 90
    )
    lng = _numero(
        request.GET.get("origem_lng"), -180, 180
    )
    try:
        id_predio = int(request.GET.get("predio", ""))
    except ValueError:
        id_predio = None

    predio = (
        Predio.objects.filter(pk=id_predio).first()
        if id_predio else None
    )

    if (
        lat is None
        or lng is None
        or predio is None
        or predio.latitude is None
        or predio.longitude is None
    ):
        return JsonResponse(
            {"estado": "invalido"}, status=400
        )

    chave = (
        os.environ.get("GOOGLE_ROUTES_API_KEY")
        or getattr(settings, "GOOGLE_MAPS_API_KEY", "")
    )
    if not chave:
        return JsonResponse({"estado": "sem_chave"})

    corpo = {
        "origin": {"location": {"latLng": {
            "latitude": lat,
            "longitude": lng,
        }}},
        "destination": {"location": {"latLng": {
            "latitude": float(predio.latitude),
            "longitude": float(predio.longitude),
        }}},
        "travelMode": "WALK",
        "languageCode": "pt-BR",
        "units": "METRIC",
    }
    campos = (
        "routes.duration,"
        "routes.distanceMeters,"
        "routes.polyline.encodedPolyline"
    )
    pedido = urllib.request.Request(
        ROTAS_URL,
        data=json.dumps(corpo).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "X-Goog-Api-Key": chave,
            "X-Goog-FieldMask": campos,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(
            pedido, timeout=10
        ) as resposta:
            dados = json.loads(
                resposta.read().decode("utf-8")
            )
    except (
        urllib.error.URLError, TimeoutError, ValueError
    ):
        return JsonResponse(
            {"estado": "falha"}, status=502
        )

    rotas = dados.get("routes") or []
    if not rotas:
        return JsonResponse({"estado": "sem_rota"})

    rota = rotas[0]
    texto = str(rota.get("duration", "0s")).rstrip("s")
    try:
        segundos = round(float(texto))
    except ValueError:
        segundos = 0

    return JsonResponse({
        "estado": "ok",
        "duracao_segundos": segundos,
        "minutos": max(1, round(segundos / 60)),
        "distancia_metros": rota.get(
            "distanceMeters", 0
        ),
        "polilinha": rota.get("polyline", {}).get(
            "encodedPolyline", ""
        ),
    })

def rota_externa(request):
    try:
        id_predio = int(request.GET.get("predio", ""))
    except ValueError:
        id_predio = None

    predio = (
        Predio.objects.filter(pk=id_predio).first()
        if id_predio else None
    )
    lat = _numero(
        request.GET.get("origem_lat"), -90, 90
    )
    lng = _numero(
        request.GET.get("origem_lng"), -180, 180
    )

    pronto = bool(
        predio
        and predio.latitude is not None
        and predio.longitude is not None
        and lat is not None
        and lng is not None
    )

    dados = {
        "pronto": pronto,
        "chave": settings.GOOGLE_MAPS_API_KEY,
        "rota_url": reverse("rota_a_pe"),
    }
    if pronto:
        nome_origem = (
            request.GET.get("origem_nome", "")[:100]
            or "Origem"
        )
        dados["origem"] = {
            "lat": lat,
            "lng": lng,
            "nome": nome_origem,
        }
        dados["destino"] = {
            "id": predio.pk,
            "nome": predio.nome,
            "lat": float(predio.latitude),
            "lng": float(predio.longitude),
        }

    return render(request, "rota.html", {
        "predio": predio,
        "dados": dados,
    })

def _tempo_a_pe(chave, origem_lat, origem_lng, predio):
    corpo = {
        "origin": {"location": {"latLng": {
            "latitude": origem_lat,
            "longitude": origem_lng,
        }}},
        "destination": {"location": {"latLng": {
            "latitude": float(predio.latitude),
            "longitude": float(predio.longitude),
        }}},
        "travelMode": "WALK",
        "languageCode": "pt-BR",
        "units": "METRIC",
    }
    pedido = urllib.request.Request(
        ROTAS_URL,
        data=json.dumps(corpo).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "X-Goog-Api-Key": chave,
            "X-Goog-FieldMask": (
                "routes.duration,routes.distanceMeters"
            ),
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(
            pedido, timeout=10
        ) as resposta:
            dados = json.loads(
                resposta.read().decode("utf-8")
            )
    except (
        urllib.error.URLError, TimeoutError, ValueError
    ):
        return None

    rotas = dados.get("routes") or []
    if not rotas:
        return None
    rota = rotas[0]
    try:
        segundos = round(float(
            str(rota.get("duration", "0s")).rstrip("s")
        ))
    except ValueError:
        return None
    return {
        "segundos": segundos,
        "metros": rota.get("distanceMeters", 0),
    }


def banheiro_proximo(request):
    lat = _numero(
        request.GET.get("origem_lat"), -90, 90
    )
    lng = _numero(
        request.GET.get("origem_lng"), -180, 180
    )
    if lat is None or lng is None:
        return JsonResponse(
            {"estado": "invalido"}, status=400
        )

    chave = (
        os.environ.get("GOOGLE_ROUTES_API_KEY")
        or getattr(settings, "GOOGLE_MAPS_API_KEY", "")
    )
    if not chave:
        return JsonResponse({"estado": "sem_chave"})

    banheiros = (
        Espaco.objects
        .filter(
            tipo__nome="Banheiro",
            andar__predio__latitude__isnull=False,
            andar__predio__longitude__isnull=False,
        )
        .select_related("andar__predio")
    )
    por_predio = {}
    for banheiro in banheiros:
        por_predio.setdefault(
            banheiro.andar.predio_id, []
        ).append(banheiro)

    if not por_predio:
        return JsonResponse({"estado": "sem_banheiro"})

    candidatos = []
    for lista in por_predio.values():
        predio = lista[0].andar.predio
        distancia = (
            (float(predio.latitude) - lat) ** 2
            + (float(predio.longitude) - lng) ** 2
        )
        candidatos.append((distancia, predio, lista))
    candidatos.sort(key=lambda item: item[0])

    melhor = None
    for _, predio, lista in candidatos[:5]:
        tempo = _tempo_a_pe(chave, lat, lng, predio)
        if tempo is None:
            continue
        if (
            melhor is None
            or tempo["segundos"] < melhor["segundos"]
        ):
            banheiro = min(
                lista, key=lambda b: b.andar.numero
            )
            melhor = {
                "segundos": tempo["segundos"],
                "metros": tempo["metros"],
                "banheiro": banheiro,
                "predio": predio,
            }

    if melhor is None:
        return JsonResponse(
            {"estado": "falha"}, status=502
        )

    return JsonResponse({
        "estado": "ok",
        "banheiro": melhor["banheiro"].nome,
        "predio": melhor["predio"].nome,
        "predio_id": melhor["predio"].pk,
        "andar": melhor["banheiro"].andar.nome,
        "minutos": max(1, round(melhor["segundos"] / 60)),
        "distancia_metros": melhor["metros"],
        "aviso": (
            "Tempo estimado até a entrada do prédio, "
            "sem contar o caminho dentro dele."
        ),
    })
