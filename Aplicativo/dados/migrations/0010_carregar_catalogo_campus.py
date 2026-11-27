import json
from math import isfinite
from pathlib import Path

from django.db import migrations


def carregar_catalogo(apps, schema_editor):
    connection = schema_editor.connection
    alias = connection.alias
    fonte = Path(__file__).with_name("catalogo_campus.json")
    catalogo = json.loads(fonte.read_text(encoding="utf-8"))

    def manager(nome):
        return apps.get_model("dados", nome).objects.using(alias)

    def obter_ou_criar(colecao, busca, campos):
        encontrado = colecao.filter(**busca).order_by("pk").first()
        return encontrado if encontrado else colecao.create(**(campos | busca))

    predios = {}
    for registro in catalogo["predio"]:
        campos = registro.copy()
        identificador = campos.pop("id_predio")
        predio = obter_ou_criar(manager("Predio"), {"nome": campos["nome"]}, campos)
        coordenadas = {}
        for campo in ("latitude", "longitude"):
            if getattr(predio, campo) is None and campos[campo] is not None:
                coordenadas[campo] = campos[campo]
        if coordenadas:
            manager("Predio").filter(pk=predio.pk).update(**coordenadas)
        predios[identificador] = predio

    andares = {}
    for registro in catalogo["andar"]:
        campos = registro.copy()
        identificador = campos.pop("id_andar")
        predio = predios[campos.pop("id_predio")]
        andares[identificador] = obter_ou_criar(
            manager("Andar"), {"predio_id": predio.pk, "numero": campos["numero"]}, campos,
        )

    tipos = {}
    for nome, campo_id in (("TipoEspaco", "id_tipo"), ("TipoPonto", "id_tipo_ponto")):
        tipos[nome] = {}
        for registro in catalogo[nome.lower()]:
            campos = registro.copy()
            identificador = campos.pop(campo_id)
            tipos[nome][identificador] = obter_ou_criar(manager(nome), {"nome": campos["nome"]}, campos)

    espacos = {}
    colecao = manager("Espaco")
    for registro in catalogo["espaco"]:
        campos = registro.copy()
        identificador = campos.pop("id_espaco")
        andar = andares[campos.pop("id_andar")]
        tipo = tipos["TipoEspaco"][campos.pop("id_tipo")]
        espaco = colecao.filter(andar__predio_id=andar.predio_id, codigo=campos["codigo"]).order_by("pk").first()
        espacos[identificador] = espaco or colecao.create(andar_id=andar.pk, tipo_id=tipo.pk, **campos)

    pontos = {}
    for registro in catalogo["ponto"]:
        campos = registro.copy()
        identificador = campos.pop("id_ponto")
        andar = andares[campos.pop("id_andar")]
        tipo = tipos["TipoPonto"][campos.pop("id_tipo_ponto")]
        pontos[identificador] = obter_ou_criar(
            manager("Ponto"), {"andar_id": andar.pk, "nome": campos["nome"]}, campos | {"tipo_ponto_id": tipo.pk},
        )

    conexoes = catalogo["conexao"]
    if "dados_conexao_legada" in connection.introspection.table_names():
        # A tabela arquivada contém os IDs e os valores do banco que foi atualizado.
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM dados_conexao_legada ORDER BY id_conexao")
            colunas = [coluna[0] for coluna in cursor.description]
            conexoes = [dict(zip(colunas, registro)) for registro in cursor.fetchall()]
        espacos = manager("Espaco").in_bulk()
        pontos = manager("Ponto").in_bulk()

    tipo_acesso = obter_ou_criar(manager("TipoPonto"), {"nome": "Acesso a espaço"}, {})

    def ponto_do_trecho(conexao, lado):
        ponto = pontos.get(conexao.get(f"ponto_{lado}_id"))
        if ponto:
            return ponto
        espaco = espacos.get(conexao.get(f"espaco_{lado}_id"))
        if espaco is None:
            return None
        if espaco.ponto_acesso_id:
            return espaco.ponto_acesso
        ponto = obter_ou_criar(
            manager("Ponto"),
            {"andar_id": espaco.andar_id, "nome": f"Acesso · {espaco.nome}"[:150], "tipo_ponto_id": tipo_acesso.pk},
            {"posicao_x": espaco.posicao_x, "posicao_y": espaco.posicao_y},
        )
        manager("Espaco").filter(pk=espaco.pk).update(ponto_acesso_id=ponto.pk)
        espaco.ponto_acesso = ponto
        return ponto

    for registro in conexoes:
        origem = ponto_do_trecho(registro, "origem")
        destino = ponto_do_trecho(registro, "destino")
        if not origem or not destino or origem == destino or origem.andar.predio_id != destino.andar.predio_id:
            continue
        colecao = manager("Conexao")
        if colecao.filter(origem_id=origem.pk, destino_id=destino.pk).exists():
            continue
        descricao = registro.get("descricao") or ""
        tipos_verticais = [tipo for tipo in ("escada", "elevador", "rampa") if tipo in descricao.casefold()]
        if origem.andar_id == destino.andar_id:
            tipo = tipos_verticais[0] if len(tipos_verticais) == 1 else "passagem"
        else:
            tipo = tipos_verticais[0] if len(tipos_verticais) == 1 else "a_confirmar"
        distancia = registro.get("distancia")
        if distancia is not None and (not isfinite(distancia) or distancia <= 0):
            distancia = None
        validada = bool(registro.get("validada") and distancia is not None and tipo != "a_confirmar")
        colecao.create(
            origem_id=origem.pk, destino_id=destino.pk, tipo=tipo, distancia_m=distancia,
            observacoes=descricao, validada=validada,
            acessibilidade_verificada=validada and bool(registro.get("acessivel")) and tipo != "escada",
        )


class Migration(migrations.Migration):
    dependencies = [("dados", "0009_integrar_esquema_conexoes")]

    operations = [migrations.RunPython(carregar_catalogo, migrations.RunPython.noop)]
