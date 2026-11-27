
# Create your models here.
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

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

    class Meta:
        verbose_name = "espaço"
        verbose_name_plural = "espaços"

    def __str__(self):
        return f"{self.codigo} - {self.nome}"


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
        return self.nome


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

class Conexao(models.Model):
    id_conexao = models.BigAutoField(primary_key=True)

    ponto_origem = models.ForeignKey(
        Ponto,
        on_delete=models.CASCADE,
        related_name="conexoes_saida",
        null=True,
        blank=True,
    )

    espaco_origem = models.ForeignKey(
        Espaco,
        on_delete=models.CASCADE,
        related_name="conexoes_saida",
        null=True,
        blank=True,
    )

    ponto_destino = models.ForeignKey(
        Ponto,
        on_delete=models.CASCADE,
        related_name="conexoes_entrada",
        null=True,
        blank=True,
    )

    espaco_destino = models.ForeignKey(
        Espaco,
        on_delete=models.CASCADE,
        related_name="conexoes_entrada",
        null=True,
        blank=True,
    )

    acessivel = models.BooleanField(default=False)
    distancia = models.FloatField(null=True, blank=True)
    descricao = models.TextField(blank=True)

    def clean(self):
        from django.core.exceptions import ValidationError

        origem = int(self.ponto_origem_id is not None) + int(
            self.espaco_origem_id is not None
        )
        destino = int(self.ponto_destino_id is not None) + int(
            self.espaco_destino_id is not None
        )

        if origem != 1:
            raise ValidationError(
                "Informe exatamente um ponto ou espaço de origem."
            )

        if destino != 1:
            raise ValidationError(
                "Informe exatamente um ponto ou espaço de destino."
            )

        if self.distancia is not None and self.distancia < 0:
            raise ValidationError("A distância não pode ser negativa.")

    def __str__(self):
        return f"Conexão {self.id_conexao}"