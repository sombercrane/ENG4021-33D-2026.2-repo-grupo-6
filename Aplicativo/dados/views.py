from django.shortcuts import render
from django.core.paginator import Paginator

from .models import Predio
from .forms import PesquisaEspacoForm, PesquisaAuditorioForm


def home(request):
    return render(request, 'home.html')


def pesquisa(request):
    return render(request, 'Pesquisa-Sala-HTML.html')


def mapa(request):
    return render(request, 'Mapa-HTML.html')


def search(request):
    formulario = PesquisaEspacoForm(request.GET)
    return render(request, 'search.html', {
        'formulario': formulario
    })


def predios(request):
    lista = Predio.objects.all().order_by('nome')
    paginas = Paginator(lista, 5)
    predios = paginas.get_page(request.GET.get('page'))

    return render(request, 'pesquisa_predio.html', {
        'predios': predios
    })


def iag(request):
    return render(request, 'iag.html')


def leme(request):
    return render(request, 'HTML Tela Prédio Leme.html')


def laboratorios(request):
    return render(request, 'pesquisa_laboratorio.html')


def kennedy(request):
    return render(request, 'kennedy.html')


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