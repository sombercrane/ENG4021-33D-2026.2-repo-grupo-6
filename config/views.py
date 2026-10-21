from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

def pesquisa(request):
    return render(request, 'Pesquisa-Sala-HTML.html')