from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

def pesquisa(request):
    return render(request, 'Pesquisa-Sala-HTML.html')
def search(request):
    return render(request, 'search.html')

def leme(request):
    return render(request, 'HTML Tela Prédio Leme.html')
def laboratorio_fisica(request):
    return render(request, 'laboratorio_de_fisica.html')
def laboratorio_design(request):
    return render(request, 'laboratorio_de_design.html')