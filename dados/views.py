from django.shortcuts import render

# Create your views here.

#Formulario de pesquisa de auditórios
from .forms import PesquisaAuditorioForm  

def pesquisa_auditorios(request):
    form = PesquisaAuditorioForm(request.GET or None)
    return render(request, 'pesquisa-auditorios.html', {'form': form})

#Formulario de pesquisa de salas
from .forms import PesquisaSalaForm 

def pesquisa_sala(request):
    form = PesquisaSalaForm(request.GET or None)
    return render(request, 'Pesquisa-Sala-HTML.html', {'form': form})
