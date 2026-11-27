
from collections import defaultdict
from heapq import heappop, heappush

from .models import Conexao, Espaco, Ponto


def identificar_no(objeto):
    if isinstance(objeto, Ponto):
        return ("ponto", objeto.id_ponto)

    if isinstance(objeto, Espaco):
        return ("espaco", objeto.id_espaco)

    raise ValueError("Origem ou destino inválido.")


def calcular_rota(origem, destino, acessivel=False):
    inicio = identificar_no(origem)
    fim = identificar_no(destino)

    conexoes = Conexao.objects.select_related(
        "ponto_origem",
        "espaco_origem",
        "ponto_destino",
        "espaco_destino",
    )

    grafo = defaultdict(list)
    objetos = {
        inicio: origem,
        fim: destino,
    }

    for conexao in conexoes:
        if acessivel and not conexao.acessivel:
            continue

        origem_obj = (
            conexao.ponto_origem or conexao.espaco_origem
        )

        destino_obj = (
            conexao.ponto_destino or conexao.espaco_destino
        )

        if origem_obj is None or destino_obj is None:
            continue

        no_origem = identificar_no(origem_obj)
        no_destino = identificar_no(destino_obj)

        objetos[no_origem] = origem_obj
        objetos[no_destino] = destino_obj

        peso = (
            conexao.distancia
            if conexao.distancia is not None
            else 1.0
        )

        grafo[no_origem].append((no_destino, peso))
        grafo[no_destino].append((no_origem, peso))

    fila = [(0, inicio)]
    distancias = {inicio: 0}
    anteriores = {}

    while fila:
        custo, atual = heappop(fila)

        if atual == fim:
            break

        if custo > distancias.get(atual, float("inf")):
            continue

        for vizinho, peso in grafo[atual]:
            novo_custo = custo + peso

            if novo_custo < distancias.get(
                vizinho, float("inf")
            ):
                distancias[vizinho] = novo_custo
                anteriores[vizinho] = atual
                heappush(fila, (novo_custo, vizinho))

    if fim not in distancias:
        return None

    caminho = []
    atual = fim

    while atual != inicio:
        caminho.append(objetos[atual])
        atual = anteriores[atual]

    caminho.append(origem)
    caminho.reverse()

    return {
        "caminho": caminho,
        "custo": distancias[fim],
    }
