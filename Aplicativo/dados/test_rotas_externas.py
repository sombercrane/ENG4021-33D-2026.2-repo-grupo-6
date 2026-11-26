import io
import json
from decimal import Decimal
from unittest.mock import patch

from django.test import Client, SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from .models import AcessoExterno, Andar, Conexao, Espaco, Ponto, Predio, TipoEspaco, TipoPonto
from .rotas_externas import RotaExterna, RotaExternaIndisponivel, calcular_rota_externa


class GoogleRoutesTests(SimpleTestCase):
    @override_settings(GOOGLE_ROUTES_API_KEY="chave-de-teste")
    @patch("dados.rotas_externas.urlopen")
    def test_consulta_a_pe_e_le_a_chegada_do_provedor(self, abrir):
        abrir.return_value = io.BytesIO(json.dumps({
            "routes": [{
                "distanceMeters": 265,
                "duration": "170s",
                "legs": [{
                    "endLocation": {"latLng": {"latitude": -22.979, "longitude": -43.232}},
                    "steps": [{"navigationInstruction": {"instructions": "Siga em frente"}}],
                }],
            }],
        }).encode())
        resultado = calcular_rota_externa((-22.978, -43.232), (-22.9791, -43.2321))
        self.assertEqual(resultado, RotaExterna(265, 3, (-22.979, -43.232), ("Siga em frente",)))
        requisicao = abrir.call_args.args[0]
        corpo = json.loads(requisicao.data)
        self.assertEqual(corpo["travelMode"], "WALK")
        self.assertEqual(corpo["destination"]["location"]["latLng"]["latitude"], -22.9791)
        self.assertIn("routes.legs.endLocation", requisicao.get_header("X-goog-fieldmask"))

    @override_settings(GOOGLE_ROUTES_API_KEY="")
    @patch("dados.rotas_externas.urlopen")
    def test_sem_chave_nao_envia_coordenadas(self, abrir):
        with self.assertRaises(RotaExternaIndisponivel):
            calcular_rota_externa((-22.978, -43.232), (-22.9791, -43.2321))
        abrir.assert_not_called()

    @override_settings(GOOGLE_ROUTES_API_KEY="chave-de-teste")
    @patch("dados.rotas_externas.urlopen", side_effect=TimeoutError)
    def test_indisponibilidade_do_provedor(self, abrir):
        with self.assertRaises(RotaExternaIndisponivel):
            calcular_rota_externa((-22.978, -43.232), (-22.9791, -43.2321))


class IntegracaoRotaExternaTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.predio = Predio.objects.create(
            nome="Prédio de teste", sigla="PT", latitude=-22.979, longitude=-43.232,
        )
        terreo = Andar.objects.create(predio=cls.predio, numero=0, nome="Térreo")
        cls.segundo = Andar.objects.create(predio=cls.predio, numero=2, nome="Segundo andar")
        tipo_ponto = TipoPonto.objects.create(nome="Acesso")
        cls.entrada = Ponto.objects.create(
            andar=terreo, tipo_ponto=tipo_ponto, nome="Entrada norte", posicao_x=0, posicao_y=0,
        )
        porta = Ponto.objects.create(
            andar=cls.segundo, tipo_ponto=tipo_ponto, nome="Porta 201", posicao_x=10, posicao_y=20,
        )
        cls.sala = Espaco.objects.create(
            andar=cls.segundo, tipo=TipoEspaco.objects.create(nome="Sala"),
            nome="Sala 201", codigo="201", ponto_acesso=porta,
        )
        cls.conexao = Conexao.objects.create(
            origem=cls.entrada, destino=porta, tipo=Conexao.Tipo.ELEVADOR, nome="Elevador norte", distancia_m=16,
        )
        cls.acesso = AcessoExterno.objects.create(
            ponto=cls.entrada, latitude=Decimal("-22.9792"), longitude=Decimal("-43.2321"),
        )
        cls.url = reverse("rota_externa_predio", args=[cls.predio.pk])
        cls.selecao = {
            "origem_latitude": "-22.978",
            "origem_longitude": "-43.232",
            "destino": f"espaco-{cls.sala.pk}",
        }
        cls.resultado_externo = RotaExterna(265, 3, (-22.9792, -43.2321), ("Siga em frente",))

    @patch("dados.views_rotas.calcular_rota_externa")
    def test_abre_do_mapa_sem_consultar_o_provedor(self, calcular):
        cliente = Client(enforce_csrf_checks=True)
        mapa = cliente.get(reverse("mapa"))
        self.assertContains(mapa, "data-rota-externa")
        predio = mapa.context["predios_mapa"][0]
        self.assertEqual(predio["url_rota_externa"], self.url)
        self.assertIn(self.selecao["destino"], {local["destino"] for local in predio["locais"]})
        resposta = cliente.post(self.url, {**self.selecao, "csrfmiddlewaretoken": cliente.cookies["csrftoken"].value})
        self.assertEqual(resposta.context["formulario"]["destino"].value(), self.selecao["destino"])
        self.assertFalse(resposta.context["formulario"].is_bound)
        calcular.assert_not_called()

    @patch("dados.views_rotas.calcular_rota_externa")
    def test_continua_do_acesso_externo_ate_a_sala(self, calcular):
        calcular.return_value = self.resultado_externo
        resposta = self.client.post(self.url, {**self.selecao, "chegada": self.acesso.pk, "calcular": "1"})
        calcular.assert_called_once_with((-22.978, -43.232), (self.acesso.latitude, self.acesso.longitude))
        self.assertEqual(resposta.context["origem"], self.acesso.ponto)
        self.assertContains(resposta, "Siga em frente")
        self.assertContains(resposta, "Elevador norte")
        self.assertContains(resposta, "Chegada em Sala 201")

    @patch("dados.views_rotas.calcular_rota_externa")
    def test_sem_conexao_interna_informa_acesso_e_andar(self, calcular):
        calcular.return_value = self.resultado_externo
        self.conexao.delete()
        resposta = self.client.post(self.url, {**self.selecao, "chegada": self.acesso.pk, "calcular": "1"})
        self.assertContains(resposta, "chega perto de Entrada norte")
        self.assertContains(resposta, "Andar do destino")
        self.assertContains(resposta, f"?andar={self.segundo.pk}")
        self.assertNotContains(resposta, "Chegada em Sala 201")

    @patch("dados.views_rotas.calcular_rota_externa")
    def test_chegada_em_outra_via_nao_e_usada_como_acesso(self, calcular):
        calcular.return_value = RotaExterna(265, 3, (-22.982, -43.232), ())
        resposta = self.client.post(self.url, {**self.selecao, "chegada": self.acesso.pk, "calcular": "1"})
        self.assertContains(resposta, "O trecho externo termina a cerca de")
        self.assertContains(resposta, "Andar do destino")
        self.assertNotContains(resposta, "Percurso interno")

    @patch("dados.views_rotas.calcular_rota_externa")
    def test_predio_sem_acesso_usa_a_coordenada_de_referencia(self, calcular):
        self.acesso.delete()
        calcular.return_value = self.resultado_externo
        resposta = self.client.post(self.url, {**self.selecao, "calcular": "1"})
        self.assertContains(resposta, "termina na região de Prédio de teste")
        self.assertContains(resposta, "Andar do destino")
        self.assertNotContains(resposta, "Percurso interno")

    @patch("dados.views_rotas.calcular_rota_externa")
    def test_rejeita_origem_invalida_antes_de_consultar(self, calcular):
        resposta = self.client.post(self.url, {
            **self.selecao, "origem_latitude": "100", "chegada": self.acesso.pk, "calcular": "1",
        })
        self.assertContains(resposta, "Origem inválida")
        calcular.assert_not_called()
