from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

def pesquisa(request):
    return render(request, 'Pesquisa-Sala-HTML.html')
def search(request):
    return render(request, 'search.html')

def predios(request):
    return render(request, 'pesquisa_predio.html')
def leme(request):
    return render(request, 'HTML Tela Prédio Leme.html')
