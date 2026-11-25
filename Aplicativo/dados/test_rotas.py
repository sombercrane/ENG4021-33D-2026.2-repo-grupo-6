from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import Andar, Conexao, Espaco, Ponto, Predio, TipoEspaco, TipoPonto
from .rotas import calcular_rota_interna


class RotasInternasTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.predio = Predio.objects.create(nome="Prédio de teste", sigla="PT")
        cls.terreo = Andar.objects.create(predio=cls.predio, nome="Térreo", numero=0)
        cls.segundo = Andar.objects.create(predio=cls.predio, nome="Segundo andar", numero=2)
        cls.tipo_ponto = TipoPonto.objects.create(nome="Acesso")
        cls.tipo_espaco = TipoEspaco.objects.create(nome="Sala")
        cls.entrada = cls.criar_ponto(cls.terreo, "Entrada leste")
        cls.hall = cls.criar_ponto(cls.terreo, "Hall principal")
        cls.porta_terreo = cls.criar_ponto(cls.terreo, "Porta da sala T01")
        cls.patamar = cls.criar_ponto(cls.segundo, "Patamar da escada")
        cls.porta_segundo = cls.criar_ponto(cls.segundo, "Porta da sala 201")
        cls.sala_terreo = cls.criar_sala(cls.terreo, "Sala do térreo", "T01", cls.porta_terreo)
        cls.sala_segundo = cls.criar_sala(cls.segundo, "Sala de estudos", "201", cls.porta_segundo)
        cls.corredor = Conexao.objects.create(
            origem=cls.entrada, destino=cls.hall, tipo=Conexao.Tipo.CORREDOR,
            nome="Corredor leste", distancia_m=8,
        )
        cls.passagem = Conexao.objects.create(
            origem=cls.hall, destino=cls.porta_terreo, tipo=Conexao.Tipo.PASSAGEM,
            distancia_m=4, bidirecional=False,
        )
        Conexao.objects.create(
            origem=cls.entrada, destino=cls.porta_terreo, tipo=Conexao.Tipo.CORREDOR,
            distancia_m=30, bidirecional=False,
        )
        cls.escada = Conexao.objects.create(
            origem=cls.hall, destino=cls.patamar, tipo=Conexao.Tipo.ESCADA,
            nome="Escada A", distancia_m=10,
        )
        cls.corredor_segundo = Conexao.objects.create(
            origem=cls.patamar, destino=cls.porta_segundo, tipo=Conexao.Tipo.CORREDOR,
            nome="Corredor do segundo", distancia_m=6,
        )
        cls.url = reverse("rota_predio", args=[cls.predio.pk])

    @classmethod
    def criar_ponto(cls, andar, nome):
        return Ponto.objects.create(
            andar=andar, nome=nome, tipo_ponto=cls.tipo_ponto, posicao_x=10, posicao_y=20,
        )

    @classmethod
    def criar_sala(cls, andar, nome, codigo, ponto_acesso=None):
        return Espaco.objects.create(
            andar=andar, tipo=cls.tipo_espaco, nome=nome, codigo=codigo, ponto_acesso=ponto_acesso,
        )

    def test_menor_distancia_no_mesmo_andar(self):
        trechos = calcular_rota_interna(self.entrada, self.sala_terreo)
        self.assertEqual([trecho.conexao for trecho in trechos], [self.corredor, self.passagem])
        self.assertEqual(sum(trecho.conexao.distancia_m for trecho in trechos), 12)

    def test_percurso_entre_andares(self):
        trechos = calcular_rota_interna(self.entrada, self.sala_segundo)
        self.assertEqual(
            [trecho.conexao for trecho in trechos], [self.corredor, self.escada, self.corredor_segundo],
        )
        self.assertEqual(trechos[1].origem.andar, self.terreo)
        self.assertEqual(trechos[1].destino.andar, self.segundo)

    def test_sentido_da_conexao_e_origem_igual_ao_destino(self):
        self.assertIsNone(calcular_rota_interna(self.porta_terreo, self.entrada))
        volta = calcular_rota_interna(self.hall, self.entrada)
        self.assertEqual([(trecho.origem, trecho.destino) for trecho in volta], [(self.hall, self.entrada)])
        self.assertEqual(calcular_rota_interna(self.entrada, self.entrada), [])

    def test_espaco_sem_acesso_e_ponto_desconectado(self):
        sala = self.criar_sala(self.segundo, "Sala sem acesso mapeado", "202")
        self.assertIsNone(calcular_rota_interna(self.entrada, sala))
        ponto = self.criar_ponto(self.terreo, "Ponto desconectado")
        self.assertIsNone(calcular_rota_interna(self.entrada, ponto))

    def test_ignora_conexao_importada_que_liga_andares_por_corredor(self):
        conexao = Conexao(
            origem=self.entrada, destino=self.porta_segundo, tipo=Conexao.Tipo.CORREDOR, distancia_m=1,
        )
        with self.assertRaises(ValidationError):
            conexao.full_clean()
        conexao.save()
        trechos = calcular_rota_interna(self.entrada, self.sala_segundo)
        self.assertEqual([trecho.conexao for trecho in trechos], [self.corredor, self.escada, self.corredor_segundo])

    def test_validacao_de_ponto_e_conexao_de_outro_predio(self):
        outro = Predio.objects.create(nome="Outro prédio", sigla="OP")
        andar = Andar.objects.create(predio=outro, nome="Térreo", numero=0)
        ponto = self.criar_ponto(andar, "Entrada de outro prédio")
        conexao = Conexao(origem=self.entrada, destino=ponto, tipo=Conexao.Tipo.RAMPA, distancia_m=1)
        with self.assertRaises(ValidationError):
            conexao.full_clean()
        self.sala_terreo.ponto_acesso = ponto
        with self.assertRaises(ValidationError):
            self.sala_terreo.full_clean()
        self.assertIsNone(calcular_rota_interna(self.entrada, ponto))

    def test_calcula_pela_pagina_do_predio(self):
        resposta = self.client.get(self.url, {"origem": self.entrada.pk, "destino": f"espaco-{self.sala_segundo.pk}"})
        self.assertContains(resposta, "24 m de percurso interno.")
        self.assertEqual(resposta.context["destino"], self.sala_segundo)

    def test_instrucoes_na_ordem_do_percurso(self):
        resposta = self.client.get(self.url, {"origem": self.entrada.pk, "destino": f"espaco-{self.sala_segundo.pk}"})
        self.assertContains(resposta, "Térreo → Segundo andar")
        html = resposta.content.decode()
        etapas = ("Início em Entrada leste", "Corredor leste", "Escada A", "Corredor do segundo", "Chegada em Sala de estudos")
        posicoes = [html.index(etapa) for etapa in etapas]
        self.assertEqual(posicoes, sorted(posicoes))

    def test_instrucao_de_descida_em_percurso_invertido(self):
        resposta = self.client.get(self.url, {"origem": self.porta_segundo.pk, "destino": f"ponto-{self.entrada.pk}"})
        self.assertContains(resposta, "Segundo andar → Térreo")

    def test_sem_cobertura_informa_andar_e_link_do_destino(self):
        sala = self.criar_sala(self.segundo, "Sala sem acesso mapeado", "202")
        resposta = self.client.get(self.url, {"origem": self.entrada.pk, "destino": f"espaco-{sala.pk}"})
        self.assertContains(resposta, "Andar do destino")
        self.assertContains(resposta, f'?andar={self.segundo.pk}')
        self.assertNotContains(resposta, 'class="rota-etapas"')

    def test_destino_pre_selecionado_e_id_invalido(self):
        destino = f"espaco-{self.sala_segundo.pk}"
        resposta = self.client.get(self.url, {"destino": destino})
        self.assertEqual(resposta.context["formulario"]["destino"].value(), destino)
        self.assertNotContains(resposta, "Percurso interno")
        resposta = self.client.get(self.url, {"origem": self.entrada.pk, "destino": "ponto-999999"})
        self.assertIn("destino", resposta.context["formulario"].errors)

    def test_rota_acessivel_prefere_rampa_e_elevador_a_escada_mais_curta(self):
        self.sala_segundo.acessivel = True
        self.sala_segundo.save(update_fields=["acessivel"])
        self.corredor.acessibilidade_verificada = True
        self.corredor.save(update_fields=["acessibilidade_verificada"])
        elevador_terreo = self.criar_ponto(self.terreo, "Elevador B no térreo")
        elevador_segundo = self.criar_ponto(self.segundo, "Elevador B no segundo")
        rampa = Conexao.objects.create(
            origem=self.hall, destino=elevador_terreo, tipo=Conexao.Tipo.RAMPA,
            nome="Rampa principal", distancia_m=20, acessibilidade_verificada=True,
        )
        elevador = Conexao.objects.create(
            origem=elevador_terreo, destino=elevador_segundo, tipo=Conexao.Tipo.ELEVADOR,
            nome="Elevador B", distancia_m=10, acessibilidade_verificada=True,
        )
        passagem = Conexao.objects.create(
            origem=elevador_segundo, destino=self.porta_segundo, tipo=Conexao.Tipo.PASSAGEM,
            distancia_m=5, acessibilidade_verificada=True,
        )
        Conexao.objects.create(
            origem=self.hall, destino=self.porta_segundo, tipo=Conexao.Tipo.ELEVADOR, distancia_m=2,
        )
        resposta = self.client.get(self.url, {
            "origem": self.entrada.pk, "destino": f"espaco-{self.sala_segundo.pk}", "acessivel": "on",
        })
        self.assertEqual(
            [trecho.conexao for trecho in resposta.context["trechos"]], [self.corredor, rampa, elevador, passagem],
        )
        self.assertContains(resposta, "Percurso interno acessível")
        self.assertContains(resposta, "Rampa principal")
        self.assertContains(resposta, "Elevador B")
        self.assertNotContains(resposta, "Escada A")

    def test_sem_trechos_verificados_informa_cobertura_insuficiente(self):
        self.sala_segundo.acessivel = True
        self.sala_segundo.save(update_fields=["acessivel"])
        resposta = self.client.get(self.url, {
            "origem": self.entrada.pk, "destino": f"espaco-{self.sala_segundo.pk}", "acessivel": "on",
        })
        self.assertContains(resposta, "não permitem confirmar um percurso interno acessível")
        self.assertContains(resposta, "Andar do destino")
        self.assertNotContains(resposta, 'class="rota-etapas"')

    def test_nao_confirma_acessibilidade_da_sala_sem_verificacao(self):
        self.passagem.acessibilidade_verificada = True
        self.passagem.save(update_fields=["acessibilidade_verificada"])
        self.assertIsNone(calcular_rota_interna(self.hall, self.sala_terreo, acessivel=True))

    def test_escada_nao_pode_ser_cadastrada_como_acessivel(self):
        self.escada.acessibilidade_verificada = True
        with self.assertRaises(ValidationError) as erro:
            self.escada.full_clean()
        self.assertIn("acessibilidade_verificada", erro.exception.message_dict)
