from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

def search(request):
    return render(request, 'search.html')

def leme(request):
    return render(request, 'HTML Tela Prédio Leme.html')