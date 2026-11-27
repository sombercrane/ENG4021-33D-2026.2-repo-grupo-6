from datetime import datetime, timedelta
from unicodedata import combining, normalize

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_GET, require_POST

from .forms import CATEGORIAS, PesquisaMapaForm
from .models import Aula, Espaco, Ponto, Predio
from .rotas_externas import coordenadas_validas, distancia_entre_coordenadas


TIPOS = {chave for chave, _ in CATEGORIAS} - {"todos", "predio"}


def _normalizar(texto):
    return "".join(letra for letra in normalize("NFD", texto.casefold()) if not combining(letra))


def _tipo_pin(tipo):
    palavras = _normalizar(tipo).split()
    return palavras[0] if palavras and palavras[0] in TIPOS else "outro"


def _catalogo(dados):
    busca = _normalizar(dados.get("busca", ""))
    categoria = dados.get("categoria", "todos")
    predio = dados.get("predio")
    andar = dados.get("andar")
    predios = Predio.objects.order_by("nome", "pk")
    if andar or predio:
        predios = predios.filter(pk=andar.predio_id if andar else predio.pk)

    predios_mapa = {}
    resultados = []
    for predio in predios:
        url = reverse("detalhe_predio", args=[predio.pk])
        no_mapa = coordenadas_validas(predio.latitude, predio.longitude)
        if no_mapa:
            predios_mapa[predio.pk] = {
                "id": predio.pk, "nome": predio.nome, "url": url,
                "latitude": predio.latitude, "longitude": predio.longitude,
                "url_rota": reverse("rota_predio", args=[predio.pk]),
                "url_rota_externa": reverse("rota_externa_predio", args=[predio.pk]),
                "locais": [],
            }
        if categoria not in ("todos", "predio") or busca not in _normalizar(f"{predio.nome} {predio.sigla}"):
            continue
        if andar:
            url += f"?andar={andar.pk}"
        item = {
            "id": f"predio-{predio.pk}", "nome": predio.nome, "tipo": "Prédio",
            "pin": "predio", "detalhe": predio.sigla if predio.sigla != "-" else "",
            "url": url, "no_mapa": no_mapa,
        }
        resultados.append(item)
        if no_mapa:
            predios_mapa[predio.pk]["locais"].append(item)

    if categoria != "predio":
        espacos = Espaco.objects.filter(andar__predio__in=predios).select_related("tipo", "andar__predio")
        pontos = (
            Ponto.objects.filter(andar__predio__in=predios)
            .exclude(tipo_ponto__nome="Acesso a espaço")
            .select_related("tipo_ponto", "andar__predio")
        )
        if andar:
            espacos = espacos.filter(andar=andar)
            pontos = pontos.filter(andar=andar)
        for colecao in (espacos.order_by("nome", "pk"), pontos.order_by("nome", "pk")):
            for local in colecao:
                espaco = isinstance(local, Espaco)
                predio = local.andar.predio
                tipo = local.tipo.nome if espaco else local.tipo_ponto.nome
                pin = _tipo_pin(tipo)
                if categoria != "todos" and pin != categoria:
                    continue
                codigo = local.codigo if espaco else ""
                if busca not in _normalizar(f"{local.nome} {codigo} {tipo} {predio.sigla} {predio.nome}"):
                    continue
                destino = f"{'espaco' if espaco else 'ponto'}-{local.pk}"
                if espaco:
                    url = reverse("detalhe_espaco", args=[local.pk])
                else:
                    url = reverse("detalhe_predio", args=[predio.pk]) + f"?andar={local.andar_id}#{destino}"
                item = {
                    "id": destino, "nome": local.nome, "tipo": tipo, "pin": pin,
                    "andar": local.andar.nome, "destino": destino, "url": url,
                    "detalhe": " · ".join(item for item in (codigo, predio.nome, local.andar.nome) if item),
                    "no_mapa": predio.pk in predios_mapa,
                }
                resultados.append(item)
                if item["no_mapa"]:
                    predios_mapa[predio.pk]["locais"].append(item)

    return resultados, [predio for predio in predios_mapa.values() if predio["locais"]]


def _proxima_aula(usuario):
    agora = timezone.localtime()
    escolhida = None
    for aula in Aula.objects.filter(usuario=usuario).select_related("sala__andar__predio"):
        dia = agora.date() + timedelta(days=(aula.dia_semana - agora.weekday()) % 7)
        inicio = datetime.combine(dia, aula.horario_inicio, tzinfo=agora.tzinfo)
        fim = datetime.combine(dia, aula.horario_fim, tzinfo=agora.tzinfo)
        if fim <= agora:
            inicio += timedelta(days=7)
        if escolhida is None or inicio < escolhida[0]:
            escolhida = (inicio, aula)
    if escolhida:
        inicio, aula = escolhida
        return {"aula": aula, "inicio": inicio, "em_andamento": inicio <= agora}
    return None


@require_GET
def mapa(request):
    formulario = PesquisaMapaForm(request.GET or None, auto_id="mapa-%s")
    if not formulario.is_bound or formulario.is_valid():
        dados = formulario.cleaned_data if formulario.is_bound else {}
        resultados, predios_mapa = _catalogo(dados)
        filtrando = any(dados.get(chave) for chave in ("busca", "predio", "andar")) or dados.get("categoria", "todos") != "todos"
        pagina = Paginator(resultados, 8).get_page(request.GET.get("page"))
    else:
        pagina, predios_mapa, filtrando = None, [], True
    return render(request, "Mapa-HTML.html", {
        "formulario": formulario, "predios_mapa": predios_mapa, "pagina": pagina,
        "filtros_ativos": filtrando,
        "proxima_aula": _proxima_aula(request.user) if request.user.is_authenticated else None,
        "demo": Predio.objects.filter(sigla="DEMO", nome="Prédio de demonstração").first(),
    })


@require_GET
def redirecionar_busca(request, categoria=None, busca=None):
    filtros = request.GET.copy()
    if categoria:
        filtros.setdefault("categoria", categoria)
    if busca:
        filtros.setdefault("busca", busca)
    consulta = filtros.urlencode()
    return redirect(f"{reverse('mapa')}?{consulta}" if consulta else reverse("mapa"))


@require_GET
def sugestoes_pesquisa(request):
    filtros = request.GET.copy()
    termo = filtros.get("q", "").strip()
    if len(termo) < 2:
        return JsonResponse({"sugestoes": []})
    filtros["busca"] = termo
    formulario = PesquisaMapaForm(filtros)
    if not formulario.is_valid():
        return JsonResponse({"sugestoes": []})
    resultados, _ = _catalogo(formulario.cleaned_data)
    return JsonResponse({"sugestoes": resultados[:8]})


@sensitive_post_parameters("origem_latitude", "origem_longitude")
@require_POST
def banheiro_proximo(request):
    try:
        origem = (float(request.POST["origem_latitude"]), float(request.POST["origem_longitude"]))
    except (KeyError, ValueError):
        return JsonResponse({"estado": "invalido"}, status=400)
    if not coordenadas_validas(*origem):
        return JsonResponse({"estado": "invalido"}, status=400)
    _, predios = _catalogo({"categoria": "banheiro"})
    if not predios:
        return JsonResponse({"estado": "sem_banheiro"})
    predio = min(predios, key=lambda item: distancia_entre_coordenadas(origem, (item["latitude"], item["longitude"])))
    return JsonResponse({
        "estado": "ok",
        "predio": predio["nome"],
        "distancia_metros": round(distancia_entre_coordenadas(origem, (predio["latitude"], predio["longitude"]))),
        "locais": predio["locais"],
    })
