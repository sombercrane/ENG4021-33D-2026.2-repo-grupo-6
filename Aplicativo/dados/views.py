from itertools import chain
from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import Predio, Espaco, Ponto
from .forms import (
    PesquisaForm,
    PesquisaEspacoForm,
    PesquisaAuditorioForm,
    PesquisaPredioForm,
    PesquisaLaboratorioForm,
)


def home(request):
    return render(request, 'home.html')


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
        predios_por_id[predio_id] = predio

    ids_predios = list(predios_por_id)

    espacos = (
        Espaco.objects.filter(andar__predio_id__in=ids_predios)
        .order_by('nome')
        .values_list('andar__predio_id', 'nome', 'tipo__nome', 'andar__nome')
    )
    pontos = (
        Ponto.objects.filter(andar__predio_id__in=ids_predios)
        .order_by('nome')
        .values_list('andar__predio_id', 'nome', 'tipo_ponto__nome', 'andar__nome')
    )

    for predio_id, nome, tipo, andar in chain(espacos, pontos):
        predios_por_id[predio_id]['locais'].append({
            'nome': nome,
            'tipo': tipo,
            'andar': andar,
        })

    return render(request, 'Mapa-HTML.html', {
        'predios_mapa': list(predios_por_id.values()),
    })

def pesquisa(request):
    predios = Predio.objects.all()

    return render(request, 'pesquisa.html', {
        'predios': predios
    })

def search(request):
    formulario = PesquisaEspacoForm(request.GET)
    return render(request, 'search.html', {
        'formulario': formulario
    })


def predios(request):
    formulario = PesquisaPredioForm(
        request.GET or None
    )

    lista = Predio.objects.all().order_by('nome')

    if formulario.is_valid():
        busca = formulario.cleaned_data['busca']

        if busca:
            lista = lista.filter(
                Q(nome__icontains=busca) |
                Q(sigla__icontains=busca)
            )

    paginas = Paginator(lista, 5)
    predios = paginas.get_page(
        request.GET.get('page')
    )

    return render(request, 'pesquisa_predio.html', {
        'formulario': formulario,
        'predios': predios
    })

def consultar_predio(request, identificador):
    predio = get_object_or_404(Predio, id_predio=identificador)

    andares = predio.andares.all()

    return render(request, 'predio.html', {
        'predio': predio,
        'andares': andares
    })


def predio_por_sigla(request, sigla):
    formulario = PesquisaEspacoForm(request.GET or None)

    predio = Predio.objects.filter(sigla__iexact=sigla).first()

    if predio is None:
        return render(request, '404.html', status=404)

    andares = predio.andares.prefetch_related('espacos__tipo').order_by('numero')

    if formulario.is_valid():
        busca = formulario.cleaned_data.get('busca')

        if busca:
            andares = andares.filter(
                espacos__nome__icontains=busca
            ).distinct()

    return render(request, 'base_predio.html', {
        'predio': predio,
        'andares': andares,
        'formulario': formulario,
    })
def iag(request):
    return render(
        request, 'HTML Tela Prédio IAG.html'
    )


def leme(request):
    return render(
        request, 'HTML Tela Prédio Leme.html'
    )


def laboratorios(request):
    formulario = PesquisaLaboratorioForm(
        request.GET or None
    )

    laboratorios = Espaco.objects.filter(
        tipo__nome__icontains='laboratório'
    ).select_related(
        'andar__predio', 'tipo'
    ).order_by('nome')

    if formulario.is_valid():
        busca = formulario.cleaned_data['busca']

        if busca:
            laboratorios = laboratorios.filter(
                Q(nome__icontains=busca) |
                Q(codigo__icontains=busca)
            )

    return render(
        request, 'pesquisa_laboratorio.html', {
            'formulario': formulario,
            'laboratorios': laboratorios
        }
    )


def kennedy(request):
    form = PesquisaEspacoForm(request.GET or None)
    espacos = Espaco.objects.filter(
        andar__predio__sigla='K'
    )

    termo = (
        form['busca'].value()
        if form.is_bound else None
    )
    if termo:
        espacos = espacos.filter(
            Q(nome__icontains=termo)
            | Q(codigo__icontains=termo)
        )

    return render(request, 'kennedy.html', {
        'form': form,
        'espacos': espacos,
    })


def auditorios(request):
    return render(
        request, 'pesquisa-auditorios.html'
    )



def laboratorio_fisica(request):
    return render(
        request, 'laboratorio_de_fisica.html'
    )


def laboratorio_design(request):
    return render(
        request, 'laboratorio_de_design.html'
    )


def pesquisa_auditorios(request):
    form = PesquisaAuditorioForm(
        request.GET or None
    )
    return render(
        request, 'pesquisa-auditorios.html', {
            'form': form
        }
    )


def pesquisa_sala(request):
    form = PesquisaEspacoForm(request.GET or None)
    return render(
        request, 'Pesquisa-Sala-HTML.html', {
            'form': form
        }
    )


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
    return render(request, 'audrdc.html')


def auditorio_kennedy(request):
    return render(request, 'HTML aud kennedy')


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


def pesquisa(request):
    formulario = PesquisaForm(request.GET or None)
    pagina = None
    categoria = "todos"

    if formulario.is_valid():
        busca = formulario.cleaned_data["busca"]
        categoria = (
            formulario.cleaned_data["categoria"]
        )

        if categoria == "predio":
            lista = Predio.objects.order_by("nome")
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

    return render(request, "pesquisa.html", {
        "formulario": formulario,
        "pagina": pagina,
        "categoria": categoria,
        "filtros": filtros.urlencode(),
        "atual": request.GET.urlencode(),
    })


def detalhe_espaco(request, id_espaco):
    espaco = get_object_or_404(
        Espaco.objects.select_related(
            "andar__predio", "tipo"
        ),
        pk=id_espaco,
    )
    return render(
        request, "detalhe_pesquisa.html", {
            "espaco": espaco,
            "voltar": request.GET.urlencode(),
        }
    )


def detalhe_predio(request, id_predio):
    predio = get_object_or_404(
        Predio, pk=id_predio
    )
    return render(
        request, "detalhe_pesquisa.html", {
            "predio": predio,
            "voltar": request.GET.urlencode(),
        }
    )
def teste_base(request):
    return render(request, 'teste_base.html')
