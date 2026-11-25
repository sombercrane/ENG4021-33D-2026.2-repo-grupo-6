from django.shortcuts import get_object_or_404, render
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_GET, require_POST

from .forms import RotaExternaForm, RotaInternaForm
from .models import Predio
from .rotas import calcular_rota_interna
from .rotas_externas import (
    DISTANCIA_MAXIMA_DA_CHEGADA_M,
    RotaExternaIndisponivel,
    calcular_rota_externa,
    coordenadas_validas,
    distancia_entre_coordenadas,
)


def contexto_percurso(origem, destino):
    trechos = calcular_rota_interna(origem, destino)
    return {
        "origem": origem,
        "destino": destino,
        "trechos": trechos,
        "distancia_m": sum(trecho.conexao.distancia_m for trecho in trechos) if trechos is not None else None,
    }


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
        contexto.update(
            contexto_percurso(formulario.cleaned_data["origem"], formulario.cleaned_data["destino"])
        )

    return render(request, "predios/rota.html", contexto)


@sensitive_post_parameters("origem_latitude", "origem_longitude")
@never_cache
@require_POST
def rota_externa_predio(request, id_predio):
    predio = get_object_or_404(Predio, pk=id_predio)
    formulario = RotaExternaForm(
        predio,
        request.POST if "calcular" in request.POST else None,
        initial={nome: request.POST.get(nome) for nome in ("origem_latitude", "origem_longitude", "destino")},
    )
    contexto = {"predio": predio, "formulario": formulario, "externa": True}
    if formulario.is_valid():
        contexto.update(contexto_rota_externa(predio, formulario.cleaned_data))
    return render(request, "predios/rota.html", contexto)


def contexto_rota_externa(predio, dados):
    destino, acesso = dados["destino"], dados["chegada"]
    coordenadas = (acesso.latitude, acesso.longitude) if acesso else (predio.latitude, predio.longitude)
    contexto = {"destino": destino, "acesso": acesso}
    if not coordenadas_validas(*coordenadas):
        return {**contexto, "erro_externo": "Ainda não há coordenadas de chegada para este prédio."}

    try:
        rota = calcular_rota_externa((dados["origem_latitude"], dados["origem_longitude"]), coordenadas)
    except RotaExternaIndisponivel:
        return {**contexto, "erro_externo": "O cálculo do trajeto externo está indisponível no momento."}
    if rota is None:
        return {**contexto, "erro_externo": "O serviço não encontrou um trajeto a pé até a referência selecionada."}

    contexto["rota_externa"] = rota
    if acesso:
        separacao = distancia_entre_coordenadas(rota.chegada, coordenadas)
        if separacao > DISTANCIA_MAXIMA_DA_CHEGADA_M:
            contexto["distancia_da_chegada"] = round(separacao)
        else:
            contexto.update(contexto_percurso(acesso.ponto, destino))
    return contexto
