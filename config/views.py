from django.shortcuts import render
from dados.forms import PesquisaEspacoForm


def home(request):
    return render(request, 'home.html')

def search(request):
    formulario = PesquisaEspacoForm(request.GET)

    return render(request, 'search.html', {
        'formulario': formulario
    })

