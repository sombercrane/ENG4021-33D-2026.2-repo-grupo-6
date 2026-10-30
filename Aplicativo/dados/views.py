from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Predio, Espaco
from .forms import PesquisaEspacoForm, PesquisaAuditorioForm
from .models import Espaco
from .models import Predio
from .forms import (
    PesquisaEspacoForm,
    PesquisaAuditorioForm,
    PesquisaPredioForm,
    PesquisaLaboratorioForm
)



def home(request):
    return render(request, 'home.html')



def mapa(request):
    return render(request, 'Mapa-HTML.html')


def search(request):
    formulario = PesquisaEspacoForm(request.GET)
    return render(request, 'search.html', {
        'formulario': formulario
    })



def predios(request):
    formulario = PesquisaPredioForm(request.GET or None)

    lista = Predio.objects.all().order_by('nome')

    if formulario.is_valid():
        busca = formulario.cleaned_data['busca']

        if busca:
            lista = lista.filter(
                Q(nome__icontains=busca) |
                Q(sigla__icontains=busca)
            )

    paginas = Paginator(lista, 5)
    predios = paginas.get_page(request.GET.get('page'))

    return render(request, 'pesquisa_predio.html', {
        'formulario': formulario,
        'predios': predios
    })


def iag(request):
    return render(request, 'HTML Tela Prédio IAG.html')

def leme(request):
    return render(request, 'HTML Tela Prédio Leme.html')



def laboratorios(request):
    formulario = PesquisaLaboratorioForm(request.GET or None)

    laboratorios = Espaco.objects.filter(
        tipo__nome__icontains='laboratório'
    ).select_related('andar__predio', 'tipo').order_by('nome')

    if formulario.is_valid():
        busca = formulario.cleaned_data['busca']

        if busca:
            laboratorios = laboratorios.filter(
                Q(nome__icontains=busca) |
                Q(codigo__icontains=busca)
            )

    return render(request, 'pesquisa_laboratorio.html', {
        'formulario': formulario,
        'laboratorios': laboratorios
    })


def kennedy(request):
    form = PesquisaEspacoForm(request.GET or None)
    espacos = Espaco.objects.filter(andar__predio__sigla='K')

    termo = form['busca'].value() if form.is_bound else None
    if termo:
        espacos = espacos.filter(Q(nome__icontains=termo) | Q(codigo__icontains=termo))

    return render(request, 'kennedy.html', {
        'form': form,
    'espacos': espacos,
    })


def auditorios(request):
    return render(request, 'pesquisa-auditorios.html')


def rdc(request):
    return render(request, 'rdc.html')


def laboratorio_fisica(request):
    return render(request, 'laboratorio_de_fisica.html')


def laboratorio_design(request):
    return render(request, 'laboratorio_de_design.html')


def pesquisa_auditorios(request):
    form = PesquisaAuditorioForm(request.GET or None)
    return render(request, 'pesquisa-auditorios.html', {
        'form': form
    })


def pesquisa_sala(request):
    form = PesquisaEspacoForm(request.GET or None)
    return render(request, 'Pesquisa-Sala-HTML.html', {
        'form': form
    })

def auditorio_rdc(request):
    return render(request, 'audrdc.html')


def auditorio_kennedy(request):
    return render(request, 'HTML aud kennedy')
