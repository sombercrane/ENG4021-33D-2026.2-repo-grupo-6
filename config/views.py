from django.shortcuts import render
from dados.forms import PesquisaEspacoForm


def home(request):
    return render(request, 'home.html')

def pesquisa(request):
    return render(request, 'Pesquisa-Sala-HTML.html')   

def mapa(request):
    return render(request, 'Mapa-HTML.html')
    return render(request, 'Pesquisa-Sala-HTML.html')
def search(request):
    formulario = PesquisaEspacoForm(request.GET)

    return render(request, 'search.html', {
        'formulario': formulario
    })

def rdc(request):
    return render(request, 'rdc.html')
def predios(request):
    return render(request, 'pesquisa_predio.html')
def leme(request):
    return render(request, 'HTML Tela Prédio Leme.html')
def laboratorio_fisica(request):
    return render(request, 'laboratorio_de_fisica.html')
def laboratorio_design(request):
    return render(request, 'laboratorio_de_design.html')
