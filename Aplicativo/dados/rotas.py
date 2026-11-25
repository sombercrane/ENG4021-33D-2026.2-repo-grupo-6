from collections import defaultdict
from dataclasses import dataclass
from heapq import heappop, heappush

from django.db.models import F, Q

from .models import Conexao, Ponto


@dataclass(frozen=True)
class Trecho:
    conexao: Conexao
    origem: Ponto
    destino: Ponto


def calcular_rota_interna(origem, destino):
    """Retorna os trechos mais curtos, ou None se a cobertura for insuficiente."""
    chegada = destino if isinstance(destino, Ponto) else destino.ponto_acesso
    if chegada is None or chegada.andar_id != destino.andar_id:
        return None

    predio_id = origem.andar.predio_id
    if chegada.andar.predio_id != predio_id:
        return None
    if origem.pk == chegada.pk:
        return []

    conexoes = (
        Conexao.objects.filter(origem__andar__predio_id=predio_id, destino__andar__predio_id=predio_id)
        .filter(Q(origem__andar=F("destino__andar")) | Q(tipo__in=Conexao.TIPOS_ENTRE_ANDARES))
        .select_related("origem__andar", "destino__andar")
        .order_by("pk")
    )
    vizinhos = defaultdict(list)
    for conexao in conexoes:
        vizinhos[conexao.origem_id].append(Trecho(conexao, conexao.origem, conexao.destino))
        if conexao.bidirecional:
            vizinhos[conexao.destino_id].append(Trecho(conexao, conexao.destino, conexao.origem))

    distancias = {origem.pk: 0}
    anteriores = {}
    fila = [(0, origem.pk)]
    while fila:
        distancia, ponto_id = heappop(fila)
        if distancia != distancias[ponto_id]:
            continue
        if ponto_id == chegada.pk:
            break

        for trecho in vizinhos[ponto_id]:
            proximo_id = trecho.destino.pk
            nova_distancia = distancia + trecho.conexao.distancia_m
            if nova_distancia < distancias.get(proximo_id, float("inf")):
                distancias[proximo_id] = nova_distancia
                anteriores[proximo_id] = trecho
                heappush(fila, (nova_distancia, proximo_id))

    if chegada.pk not in anteriores:
        return None

    resultado = []
    ponto_id = chegada.pk
    while ponto_id != origem.pk:
        trecho = anteriores[ponto_id]
        resultado.append(trecho)
        ponto_id = trecho.origem.pk
    resultado.reverse()
    return resultado
