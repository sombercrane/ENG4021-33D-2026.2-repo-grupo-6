from django.db import models


class Predio(models.Model):
    id_predio = models.BigAutoField(primary_key=True)
    nome = models.CharField(max_length=150)
    sigla = models.CharField(max_length=30)
    descricao = models.TextField(blank=True)
    endereco = models.CharField(max_length=255)
    imagem_mapa = models.ImageField(upload_to="predios/", blank=True)

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
    posicao_x = models.FloatField()
    posicao_y = models.FloatField()
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
