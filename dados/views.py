from django.shortcuts import render

# Create your views here.

#Formulario de pesquisa de auditórios

from django.shortcuts import render
from .forms import PesquisaAuditorioForm  

def pesquisa_auditorios(request):
    form = PesquisaAuditorioForm(request.GET or None)
    return render(request, 'pesquisa-auditorios.html', {'form': form})