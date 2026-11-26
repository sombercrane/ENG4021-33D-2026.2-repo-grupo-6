
# Create your models here.
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import F, Q


class Predio(models.Model):
    id_predio = models.BigAutoField(primary_key=True)
    nome = models.CharField(max_length=150)
    sigla = models.CharField(max_length=30)
    descricao = models.TextField(blank=True)
    endereco = models.CharField(max_length=255)
    imagem_mapa = models.ImageField(upload_to="predios/", blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        verbose_name = "prédio"
        verbose_name_plural = "prédios"

    def __str__(self):
        return f"{self.sigla} — {self.nome}"


class Andar(models.Model):
    id_andar = models.BigAutoField(primary_key=True)
    predio = models.ForeignKey(
        Predio,
        on_delete=models.CASCADE,
        related_name="andares",
        db_column="id_predio",
    )
    numero = models.IntegerField()
    nome = models.CharField(max_length=100)
    imagem_mapa = models.ImageField(upload_to="andares/", blank=True)
    descricao = models.TextField(blank=True)

    def __str__(self):
        return f"{self.predio.sigla} - {self.nome}"


class TipoEspaco(models.Model):
    id_tipo = models.BigAutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    icone = models.CharField(max_length=100, blank=True)
    cor = models.CharField(max_length=7, blank=True, help_text="Ex.: #1E88E5")

    class Meta:
        verbose_name = "tipo de espaço"
        verbose_name_plural = "tipos de espaço"

    def __str__(self):
        return self.nome


class Espaco(models.Model):
    id_espaco = models.BigAutoField(primary_key=True)
    andar = models.ForeignKey(
        Andar,
        on_delete=models.CASCADE,
        related_name="espacos",
        db_column="id_andar",
    )
    tipo = models.ForeignKey(
        TipoEspaco,
        on_delete=models.PROTECT,
        related_name="espacos",
        db_column="id_tipo",
    )
    nome = models.CharField(max_length=150)
    codigo = models.CharField(max_length=50)
    descricao = models.TextField(blank=True)
    posicao_x = models.FloatField(null=True, blank=True)
    posicao_y = models.FloatField(null=True, blank=True)
    acessivel = models.BooleanField(default=False)
    observacoes = models.TextField(blank=True)
    ponto_acesso = models.ForeignKey(
        "Ponto",
        on_delete=models.SET_NULL,
        related_name="espacos_atendidos",
        null=True,
        blank=True,
        verbose_name="ponto de acesso",
        help_text="Ponto da rota que dá acesso ao espaço. Deve estar no mesmo andar.",
    )

    class Meta:
        verbose_name = "espaço"
        verbose_name_plural = "espaços"

    def __str__(self):
        return f"{self.codigo} - {self.nome}"

    def clean(self):
        super().clean()
        if self.ponto_acesso_id and not Ponto.objects.filter(
            pk=self.ponto_acesso_id, andar_id=self.andar_id,
        ).exists():
            raise ValidationError({"ponto_acesso": "Escolha um ponto no mesmo andar do espaço."})


class TipoPonto(models.Model):
    id_tipo_ponto = models.BigAutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    icone = models.CharField(max_length=100, blank=True)
    cor = models.CharField(max_length=7, blank=True, help_text="Ex.: #1E88E5")

    class Meta:
        verbose_name = "tipo de ponto"
        verbose_name_plural = "tipos de ponto"

    def __str__(self):
        return self.nome


class Ponto(models.Model):
    id_ponto = models.BigAutoField(primary_key=True)
    andar = models.ForeignKey(
        Andar,
        on_delete=models.CASCADE,
        related_name="pontos",
        db_column="id_andar",
    )
    tipo_ponto = models.ForeignKey(
        TipoPonto,
        on_delete=models.PROTECT,
        related_name="pontos",
        db_column="id_tipo_ponto",
    )
    nome = models.CharField(max_length=150)
    posicao_x = models.FloatField()
    posicao_y = models.FloatField()
    descricao = models.TextField(blank=True)

    def __str__(self):
        return f"{self.nome} — {self.andar}"


class Conexao(models.Model):
    class Tipo(models.TextChoices):
        CORREDOR = "corredor", "Corredor"
        PASSAGEM = "passagem", "Passagem"
        ESCADA = "escada", "Escada"
        ELEVADOR = "elevador", "Elevador"
        RAMPA = "rampa", "Rampa"

    TIPOS_ENTRE_ANDARES = (Tipo.ESCADA, Tipo.ELEVADOR, Tipo.RAMPA)
    TIPOS_ACESSIVEIS = (Tipo.CORREDOR, Tipo.PASSAGEM, Tipo.ELEVADOR, Tipo.RAMPA)

    origem = models.ForeignKey(Ponto, on_delete=models.CASCADE, related_name="conexoes_de_saida")
    destino = models.ForeignKey(Ponto, on_delete=models.CASCADE, related_name="conexoes_de_chegada")
    tipo = models.CharField("tipo de trecho", max_length=12, choices=Tipo.choices)
    nome = models.CharField(
        "nome do trecho", max_length=150, blank=True,
        help_text="Identifique o trecho, por exemplo Corredor leste ou Elevador B.",
    )
    distancia_m = models.PositiveIntegerField("distância em metros", validators=[MinValueValidator(1)])
    bidirecional = models.BooleanField(
        default=True,
        help_text="Quando desmarcado, o trecho só pode ser percorrido da origem ao destino.",
    )
    acessibilidade_verificada = models.BooleanField(
        default=False,
        help_text="Marque após verificar a largura, os desníveis e as condições de passagem em todo o trecho.",
    )

    class Meta:
        verbose_name = "conexão interna"
        verbose_name_plural = "conexões internas"
        constraints = [
            models.CheckConstraint(condition=~Q(origem=F("destino")), name="conexao_pontos_distintos"),
            models.CheckConstraint(condition=Q(distancia_m__gt=0), name="conexao_distancia_positiva"),
            models.CheckConstraint(
                condition=~Q(tipo="escada", acessibilidade_verificada=True),
                name="conexao_escada_sem_acessibilidade",
            ),
        ]

    def __str__(self):
        return f"{self.origem} → {self.destino}"

    def clean(self):
        super().clean()
        if self.tipo == self.Tipo.ESCADA and self.acessibilidade_verificada:
            raise ValidationError({"acessibilidade_verificada": "Uma escada não é um trecho sem degraus."})
        if not self.origem_id or not self.destino_id:
            return

        try:
            origem, destino = self.origem.andar, self.destino.andar
        except Ponto.DoesNotExist:
            return  # A validação da chave estrangeira informa o ponto inválido.

        if origem.predio_id != destino.predio_id:
            raise ValidationError({"destino": "Os dois pontos devem pertencer ao mesmo prédio."})
        if origem.pk != destino.pk and self.tipo not in self.TIPOS_ENTRE_ANDARES:
            raise ValidationError({"tipo": "Use escada, elevador ou rampa para ligar andares."})


class AcessoExterno(models.Model):
    ponto = models.OneToOneField(
        Ponto, on_delete=models.CASCADE, related_name="acesso_externo",
        help_text="Ponto interno que corresponde à chegada do trajeto externo.",
    )
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, validators=[MinValueValidator(-90), MaxValueValidator(90)],
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, validators=[MinValueValidator(-180), MaxValueValidator(180)],
    )

    class Meta:
        verbose_name = "acesso externo"
        verbose_name_plural = "acessos externos"

    def __str__(self):
        return str(self.ponto)


class Administrador(models.Model):
    id_admin = models.BigAutoField(primary_key=True)
    nome = models.CharField(max_length=150)
    email = models.EmailField()
    # Salve aqui somente uma senha criptografada (hash), nunca a senha em texto.
    senha = models.CharField(max_length=128)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome


class Aula(models.Model):
    DIAS_SEMANA = [
        (0, "Segunda-feira"),
        (1, "Terça-feira"),
        (2, "Quarta-feira"),
        (3, "Quinta-feira"),
        (4, "Sexta-feira"),
        (5, "Sábado"),
        (6, "Domingo"),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="aulas",
    )
    disciplina = models.CharField(max_length=150)
    dia_semana = models.PositiveSmallIntegerField(
        choices=DIAS_SEMANA,
    )
    horario_inicio = models.TimeField()
    horario_fim = models.TimeField()
    sala = models.ForeignKey(
        Espaco,
        on_delete=models.PROTECT,
        related_name="aulas",
    )

    class Meta:
        ordering = ["dia_semana", "horario_inicio", "pk"]
        verbose_name = "aula"
        verbose_name_plural = "aulas"

    def clean(self):
        super().clean()
        if (
            self.horario_inicio
            and self.horario_fim
            and self.horario_fim <= self.horario_inicio
        ):
            raise ValidationError({
                "horario_fim":
                    "O término deve ser depois do início da aula."
            })

    def __str__(self):
        return (
            f"{self.disciplina} — "
            f"{self.get_dia_semana_display()} "
            f"{self.horario_inicio:%H:%M}"
        )