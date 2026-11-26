from django.test import TestCase
from django.urls import reverse

from .models import Andar, Espaco, Ponto, Predio, TipoEspaco, TipoPonto


class VisualizacaoAndarTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.predio = Predio.objects.create(nome="Prédio de teste", sigla="PT")
        cls.terreo = Andar.objects.create(predio=cls.predio, nome="Térreo", numero=0)
        cls.primeiro = Andar.objects.create(
            predio=cls.predio, nome="Primeiro andar", numero=1, imagem_mapa="andares/primeiro.png",
        )
        tipo = TipoEspaco.objects.create(nome="Sala")
        cls.sala = Espaco.objects.create(andar=cls.terreo, tipo=tipo, nome="Sala do térreo", codigo="T01")
        Espaco.objects.create(andar=cls.primeiro, tipo=tipo, nome="Sala de estudos", codigo="101")
        Ponto.objects.create(
            andar=cls.primeiro, tipo_ponto=TipoPonto.objects.create(nome="Elevador"),
            nome="Elevador central", posicao_x=10, posicao_y=20,
        )
        cls.url = reverse("detalhe_predio", args=[cls.predio.pk])

    def test_abre_terreo_e_exibe_estados_vazios(self):
        resposta = self.client.get(self.url)
        self.assertEqual(resposta.context["andar"], self.terreo)
        self.assertContains(resposta, "Sala do térreo")
        self.assertContains(resposta, "Planta indisponível para este andar.")
        self.assertContains(resposta, "Nenhum ponto de interesse cadastrado neste andar.")
        self.assertNotContains(resposta, "Sala de estudos")

    def test_troca_de_andar_exibe_apenas_seus_locais_e_planta(self):
        resposta = self.client.get(self.url, {"andar": self.primeiro.pk})
        self.assertEqual(resposta.context["andar"], self.primeiro)
        self.assertContains(resposta, "Sala de estudos")
        self.assertContains(resposta, "Elevador central")
        self.assertContains(resposta, self.primeiro.imagem_mapa.url)
        self.assertNotContains(resposta, "Sala do térreo")

    def test_predio_sem_andar_e_selecao_de_outro_predio(self):
        outro = Predio.objects.create(nome="Outro prédio", sigla="OP")
        url = reverse("detalhe_predio", args=[outro.pk])
        self.assertContains(self.client.get(url), "Nenhum andar cadastrado para este prédio.")
        self.assertEqual(self.client.get(url, {"andar": self.terreo.pk}).status_code, 404)

    def test_espaco_leva_ao_seu_andar(self):
        resposta = self.client.get(reverse("detalhe_espaco", args=[self.sala.pk]))
        self.assertContains(resposta, f'{self.url}?andar={self.terreo.pk}')
