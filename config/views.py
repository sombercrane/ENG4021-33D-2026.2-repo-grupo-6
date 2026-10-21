
from django.shortcuts import render
from dados.forms import PesquisaEspacoForm

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


def leme(request):
    return render(request, 'HTML Tela Prédio Leme.html')


def iag(request):
    return render(request, 'HTML Tela Prédio IAG.html')


def kennedy(request):
    return render(request, 'kennedy.html')


def rdc(request):
    return render(request, 'rdc.html')


def auditorios(request):
    return render(request, 'Pesquisa-auditorios.html')


def laboratorios(request):
    return render(request, 'pesquisa_laboratorio.html')


def predios(request):
    return render(request, 'pesquisa_predio.html')
