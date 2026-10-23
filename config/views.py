from django.shortcuts import render
from dados.forms import PesquisaEspacoForm


def home(request):
    return render(request, 'home.html')

def pesquisa(request):
    return render(request, 'Pesquisa-Sala-HTML.html')
def search(request):
    formulario = PesquisaEspacoForm(request.GET)

    return render(request, 'search.html', {
        'formulario': formulario
    })

def leme(request):
    return render(request, 'HTML Tela Prédio Leme.html')