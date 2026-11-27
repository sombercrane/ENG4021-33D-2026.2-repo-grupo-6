import json
from dataclasses import dataclass
from http.client import HTTPException
from math import asin, ceil, cos, isfinite, radians, sin, sqrt
from urllib.request import Request, urlopen

from django.conf import settings


DISTANCIA_MAXIMA_DA_CHEGADA_M = 30


@dataclass(frozen=True)
class RotaExterna:
    distancia_m: int
    duracao_min: int
    chegada: tuple[float, float]
    instrucoes: tuple[str, ...]


class RotaExternaIndisponivel(Exception):
    pass


def coordenadas_validas(latitude, longitude):
    return latitude is not None and longitude is not None and -90 <= latitude <= 90 and -180 <= longitude <= 180


def distancia_entre_coordenadas(origem, destino):
    lat1, lng1 = map(radians, origem)
    lat2, lng2 = map(radians, destino)
    h = sin((lat2 - lat1) / 2) ** 2 + cos(lat1) * cos(lat2) * sin((lng2 - lng1) / 2) ** 2
    return 2 * 6371000 * asin(min(1, sqrt(h)))


def calcular_rota_externa(origem, destino):
    """Consulta um trajeto a pé e mantém o ponto de chegada informado pelo provedor."""
    if not settings.GOOGLE_ROUTES_API_KEY:
        raise RotaExternaIndisponivel

    corpo = {
        "origin": _waypoint(origem),
        "destination": _waypoint(destino),
        "travelMode": "WALK",
        "languageCode": "pt-BR",
        "units": "METRIC",
    }
    requisicao = Request(
        "https://routes.googleapis.com/directions/v2:computeRoutes",
        data=json.dumps(corpo).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "X-Goog-Api-Key": settings.GOOGLE_ROUTES_API_KEY,
            "X-Goog-FieldMask": (
                "routes.distanceMeters,routes.duration,routes.legs.endLocation,"
                "routes.legs.steps.navigationInstruction.instructions"
            ),
        },
        method="POST",
    )

    try:
        with urlopen(requisicao, timeout=5) as resposta:
            rotas = json.load(resposta).get("routes", [])
        if not rotas:
            return None
        rota = rotas[0]
        chegada = rota["legs"][-1]["endLocation"]["latLng"]
        coordenadas = float(chegada.get("latitude", 0)), float(chegada.get("longitude", 0))
        distancia_m = rota.get("distanceMeters", 0)
        duracao = rota.get("duration", "0s")
        if not duracao.endswith("s"):
            raise ValueError("Duração inválida.")
        segundos = float(duracao[:-1])
        if (
            not coordenadas_validas(*coordenadas)
            or type(distancia_m) is not int or distancia_m < 0
            or not isfinite(segundos) or segundos < 0
        ):
            raise ValueError("Trajeto inválido.")
        instrucoes = (
            passo.get("navigationInstruction", {}).get("instructions")
            for trecho in rota["legs"] for passo in trecho.get("steps", [])
        )
        return RotaExterna(distancia_m, ceil(segundos / 60), coordenadas, tuple(texto for texto in instrucoes if texto))
    except (OSError, HTTPException, ValueError, TypeError, KeyError, IndexError, AttributeError) as erro:
        raise RotaExternaIndisponivel from erro


def _waypoint(coordenadas):
    latitude, longitude = coordenadas
    return {"location": {"latLng": {"latitude": float(latitude), "longitude": float(longitude)}}}
