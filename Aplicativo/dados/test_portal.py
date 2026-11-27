from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Andar, Espaco, Ponto, Predio


class PortalTests(TestCase):
    def test_busca_restringe_resultados_e_marcadores_ao_codigo(self):
        sala = Espaco.objects.get(codigo="K117")
        resposta = self.client.get(reverse("mapa"), {
            "busca": sala.codigo, "predio": sala.andar.predio_id, "andar": sala.andar_id,
        })
        paginas = resposta.context["pagina"]
        marcadores = resposta.context["predios_mapa"]
        self.assertEqual([item["id"] for item in paginas], [f"espaco-{sala.pk}"])
        self.assertEqual([item["id"] for item in marcadores], [sala.andar.predio_id])
        self.assertEqual(marcadores[0]["locais"][0]["url"], reverse("detalhe_espaco", args=[sala.pk]))

    def test_busca_ponto_com_acentos_e_retorna_estado_vazio(self):
        resposta = self.client.get(reverse("mapa"), {"busca": "elevador", "categoria": "elevador"})
        self.assertTrue(resposta.context["predios_mapa"])
        sugestoes = self.client.get(reverse("sugestoes_pesquisa"), {"q": "entrada principal", "categoria": "entrada"})
        dados = sugestoes.json()["sugestoes"]
        self.assertTrue(dados)
        self.assertTrue(all(local["id"].startswith("ponto-") and "#ponto-" in local["url"] for local in dados))

        vazio = self.client.get(reverse("mapa"), {"busca": "local sem correspondência"})
        self.assertContains(vazio, "Nenhum local encontrado")
        self.assertEqual(vazio.context["predios_mapa"], [])

    def test_rota_legada_da_busca_preserva_o_termo(self):
        resposta = self.client.get(reverse("pesquisa_sala"), {"busca": "K117"})
        self.assertRedirects(resposta, reverse("mapa") + "?busca=K117&categoria=sala")

    def test_login_retorna_para_a_grade(self):
        senha = "Senha-ficticia-de-teste-87"
        usuario = get_user_model().objects.create_user(username="revisao", password=senha)
        grade = reverse("minha_grade")
        login = self.client.get(grade).headers["Location"]
        self.assertContains(self.client.get(login), 'name="next" value="/grade/"')
        resposta = self.client.post(login, {"username": usuario.username, "password": senha, "next": grade})
        self.assertRedirects(resposta, grade)

    def test_demonstracao_calcula_as_duas_rotas_e_exibe_as_plantas(self):
        with TemporaryDirectory() as media, override_settings(MEDIA_ROOT=media):
            call_command("preparar_demonstracao", verbosity=0)
            predio = Predio.objects.get(sigla="DEMO")
            andares = Andar.objects.filter(predio=predio).order_by("numero")
            self.assertEqual(len(andares), 2)
            self.assertTrue(all(andar.imagem_mapa.storage.exists(andar.imagem_mapa.name) for andar in andares))
            entrada = Ponto.objects.get(andar=andares[0], nome="Entrada de demonstração")
            sala = Espaco.objects.get(codigo="DEMO101")
            dados = {"origem": f"ponto-{entrada.pk}", "destino": f"espaco-{sala.pk}"}
            url = reverse("buscar_rota")
            comum = self.client.get(url, dados).json()
            acessivel = self.client.get(url, dados | {"acessivel": "on"}).json()
            self.assertEqual(comum["custo"], 22)
            self.assertEqual(acessivel["custo"], 43)
            self.assertIn("Escada", [trecho.get("conexao") for trecho in comum["caminho"]])
            self.assertIn("Elevador", [trecho.get("conexao") for trecho in acessivel["caminho"]])

            sala.acessivel = False
            sala.save(update_fields=["acessivel"])
            negada = self.client.get(url, dados | {"acessivel": "on"})
            self.assertEqual(negada.status_code, 404)
