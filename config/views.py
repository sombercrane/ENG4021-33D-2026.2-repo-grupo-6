from django.shortcuts import render
from django.core.paginator import Paginator
from dados.models import Predio

def home(request):
    return render(request, 'home.html')

def pesquisa(request):
    return render(request, 'Pesquisa-Sala-HTML.html')
def search(request):
    return render(request, 'search.html')

def predios(request):
    lista = Predio.objects.all().order_by('nome')
    paginas = Paginator(lista, 5)
    predios = paginas.get_page(request.GET.get('page'))

    return render(request, 'pesquisa_predio.html', {'predios': predios})

def leme(request):
    return render(request, 'HTML Tela Prédio Leme.html')
