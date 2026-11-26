from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET

from .forms import RotaInternaForm
from .models import Predio
from .rotas import calcular_rota_interna


@require_GET
def rota_predio(request, id_predio):
    predio = get_object_or_404(Predio, pk=id_predio)
    formulario = RotaInternaForm(
        predio,
        request.GET if "origem" in request.GET else None,
        initial={"destino": request.GET.get("destino")},
    )
    contexto = {"predio": predio, "formulario": formulario}

    if formulario.is_valid():
        origem = formulario.cleaned_data["origem"]
        destino = formulario.cleaned_data["destino"]
        trechos = calcular_rota_interna(origem, destino)
        contexto.update(
            origem=origem,
            destino=destino,
            trechos=trechos,
            distancia_m=sum(trecho.conexao.distancia_m for trecho in trechos) if trechos is not None else None,
        )

    return render(request, "predios/rota.html", contexto)
