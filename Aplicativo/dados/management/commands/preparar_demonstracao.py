from io import BytesIO

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from PIL import Image, ImageDraw, ImageFont

from dados.models import Andar, Conexao, Espaco, Ponto, Predio, TipoEspaco, TipoPonto


class Command(BaseCommand):
    help = "Cadastra um prédio fictício com plantas e percursos para a demonstração do Localiza PUC."

    @transaction.atomic
    def handle(self, *args, **options):
        predio, _ = Predio.objects.get_or_create(
            nome="Prédio de demonstração", sigla="DEMO",
            defaults={
                "endereco": "Ambiente fictício",
                "descricao": "Simulação para demonstrar a navegação. As plantas e conexões são fictícias.",
            },
        )
        terreo, _ = Andar.objects.get_or_create(predio=predio, numero=0, defaults={"nome": "Térreo"})
        primeiro, _ = Andar.objects.get_or_create(predio=predio, numero=1, defaults={"nome": "1º andar"})
        entrada = self.ponto(terreo, "Entrada", "Entrada de demonstração")
        corredor = self.ponto(terreo, "Corredor", "Corredor do térreo")
        elevador_terreo = self.ponto(terreo, "Elevador", "Elevador no térreo")
        elevador_primeiro = self.ponto(primeiro, "Elevador", "Elevador no 1º andar")
        patamar = self.ponto(primeiro, "Corredor", "Corredor do 1º andar")
        acesso = self.ponto(primeiro, "Acesso a espaço", "Porta da sala de demonstração")
        tipo_sala, _ = TipoEspaco.objects.get_or_create(nome="Sala de aula")
        sala, _ = Espaco.objects.get_or_create(
            andar=primeiro, codigo="DEMO101",
            defaults={
                "tipo": tipo_sala, "nome": "Sala de demonstração",
                "descricao": "Destino fictício para comparar os trajetos com escada e elevador.",
                "ponto_acesso": acesso, "acessivel": True,
            },
        )
        for origem, destino, tipo, metros in (
            (entrada, corredor, Conexao.Tipo.RAMPA, 8),
            (corredor, patamar, Conexao.Tipo.ESCADA, 6),
            (corredor, elevador_terreo, Conexao.Tipo.CORREDOR, 12),
            (elevador_terreo, elevador_primeiro, Conexao.Tipo.ELEVADOR, 10),
            (elevador_primeiro, patamar, Conexao.Tipo.CORREDOR, 5),
            (patamar, acesso, Conexao.Tipo.PASSAGEM, 8),
        ):
            Conexao.objects.get_or_create(
                origem=origem, destino=destino, tipo=tipo,
                defaults={
                    "distancia_m": metros, "validada": True,
                    "acessibilidade_verificada": tipo != Conexao.Tipo.ESCADA,
                },
            )
        self.planta(terreo, "demo-terreo.png", ("Entrada", "Rampa", "Corredor", "Elevador"))
        self.planta(primeiro, "demo-primeiro.png", ("Elevador", "Corredor", "Sala DEMO101"))
        self.stdout.write(self.style.SUCCESS(
            f"Prédio fictício preparado. Para testar o percurso acessível, abra "
            f"/predio/{predio.pk}/rota/?origem={entrada.pk}&destino=espaco-{sala.pk}&acessivel=on"
        ))

    @staticmethod
    def ponto(andar, categoria, nome):
        tipo, _ = TipoPonto.objects.get_or_create(nome=categoria)
        ponto, _ = Ponto.objects.get_or_create(andar=andar, nome=nome, defaults={"tipo_ponto": tipo})
        return ponto

    @staticmethod
    def planta(andar, nome, rotulos):
        arquivo = andar.imagem_mapa
        caminho = f"andares/{nome}"
        if arquivo.name and (arquivo.name != caminho or arquivo.storage.exists(arquivo.name)):
            return
        if not arquivo.storage.exists(caminho):
            imagem = Image.new("RGB", (800, 230), "#f0f5f0")
            desenho = ImageDraw.Draw(imagem)
            fonte = ImageFont.load_default(size=23)
            desenho.text((36, 25), f"{andar.nome} · Planta fictícia", font=fonte, fill="#183123")
            largura = (720 - (len(rotulos) - 1) * 24) // len(rotulos)
            x = 40
            for indice, rotulo in enumerate(rotulos):
                desenho.rounded_rectangle((x, 85, x + largura, 176), 9, fill="#dcebdc", outline="#426f5b", width=3)
                desenho.text((x + largura // 2, 131), rotulo, font=fonte, fill="#183123", anchor="mm")
                if indice + 1 < len(rotulos):
                    desenho.line((x + largura, 131, x + largura + 24, 131), fill="#426f5b", width=4)
                x += largura + 24
            buffer = BytesIO()
            imagem.save(buffer, format="PNG")
            caminho = arquivo.storage.save(caminho, ContentFile(buffer.getvalue()))
        andar.imagem_mapa.name = caminho
        andar.save(update_fields=["imagem_mapa"])
