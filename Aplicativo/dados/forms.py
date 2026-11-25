from django import forms

from .models import AcessoExterno, Andar, Espaco, Ponto, Predio

CATEGORIAS = [
    ("todos", "Todos"),
    ("sala", "Salas"),
    ("laboratorio", "Laboratórios"),
    ("auditorio", "Auditórios"),
    ("predio", "Prédios"),
]


class PesquisaForm(forms.Form):
    busca = forms.CharField(
        required=False,
        max_length=150,
        label="Pesquisar",
        widget=forms.TextInput(attrs={
            "placeholder":
                "Buscar sala, prédio ou código",
            "class": "campo-busca",
        }),
    )
    categoria = forms.ChoiceField(
        choices=CATEGORIAS,
        required=False,
        initial="todos",
    )

    def clean_busca(self):
        busca = self.cleaned_data["busca"]
        busca = busca.strip()
        if busca and len(busca) < 2:
            raise forms.ValidationError(
                "Digite pelo menos 2 letras."
            )
        return busca

    def clean_categoria(self):
        cat = self.cleaned_data["categoria"]
        return cat or "todos"


class PesquisaMapaForm(PesquisaForm):
    """Formulario da tela do mapa: busca e categoria (herdados de
    PesquisaForm) mais prédio e andar, vindos do banco."""

    predio = forms.ModelChoiceField(
        queryset=Predio.objects.none(),
        required=False,
        empty_label="Todos os prédios",
        label="Prédio",
    )
    andar = forms.ModelChoiceField(
        queryset=Andar.objects.none(),
        required=False,
        empty_label="Todos os andares",
        label="Andar",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["busca"].widget.attrs["class"] = "campo"
        for nome in ("categoria", "predio", "andar"):
            self.fields[nome].widget.attrs["class"] = "campo"

        self.fields["predio"].queryset = Predio.objects.order_by("nome")
        self.fields["predio"].label_from_instance = lambda p: p.nome
        self.fields["andar"].label_from_instance = (
            lambda a: f"{a.predio.nome} — {a.nome}"
        )
        self.fields["andar"].queryset = (
            Andar.objects.select_related("predio")
            .order_by("predio__nome", "numero")
        )


PesquisaEspacoForm = PesquisaForm
PesquisaAuditorioForm = PesquisaForm
PesquisaPredioForm = PesquisaForm
PesquisaLaboratorioForm = PesquisaForm


class DestinoRotaForm(forms.Form):
    destino = forms.ChoiceField(label="Destino", widget=forms.Select(attrs={"class": "campo"}))
    acessivel = forms.BooleanField(label="Usar percurso interno acessível", required=False)

    def __init__(self, predio, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pontos = (
            Ponto.objects.filter(andar__predio=predio)
            .select_related("andar")
            .order_by("andar__numero", "nome", "pk")
        )
        espacos = (
            Espaco.objects.filter(andar__predio=predio)
            .select_related("andar", "ponto_acesso__andar")
            .order_by("andar__numero", "nome", "pk")
        )
        por_espaco = {f"espaco-{espaco.pk}": espaco for espaco in espacos}
        por_ponto = {f"ponto-{ponto.pk}": ponto for ponto in self.pontos}
        self.destinos = por_espaco | por_ponto
        self.fields["destino"].choices = [
            ("", "Escolha o destino"),
            ("Espaços", [(chave, self.rotulo_local(local)) for chave, local in por_espaco.items()]),
            ("Pontos de interesse", [(chave, self.rotulo_local(local)) for chave, local in por_ponto.items()]),
        ]

    @staticmethod
    def rotulo_local(local):
        nome = f"{local.codigo} · {local.nome}" if isinstance(local, Espaco) and local.codigo else local.nome
        return f"{nome} — {local.andar.nome}"

    def clean_destino(self):
        return self.destinos[self.cleaned_data["destino"]]


class RotaInternaForm(DestinoRotaForm):
    field_order = ("origem", "destino", "acessivel")
    origem = forms.ModelChoiceField(
        queryset=Ponto.objects.none(),
        label="Ponto de partida",
        empty_label="Escolha um ponto",
        widget=forms.Select(attrs={"class": "campo"}),
    )

    def __init__(self, predio, *args, **kwargs):
        super().__init__(predio, *args, **kwargs)
        self.fields["origem"].queryset = self.pontos
        self.fields["origem"].label_from_instance = self.rotulo_local


class RotaExternaForm(DestinoRotaForm):
    field_order = ("chegada", "destino", "acessivel")
    origem_latitude = forms.FloatField(min_value=-90, max_value=90, widget=forms.HiddenInput)
    origem_longitude = forms.FloatField(min_value=-180, max_value=180, widget=forms.HiddenInput)
    chegada = forms.ModelChoiceField(
        queryset=AcessoExterno.objects.none(),
        label="Chegada no prédio",
        empty_label="Escolha um acesso",
        widget=forms.Select(attrs={"class": "campo"}),
    )

    def __init__(self, predio, *args, **kwargs):
        super().__init__(predio, *args, **kwargs)
        acessos = (
            AcessoExterno.objects.filter(ponto__andar__predio=predio)
            .select_related("ponto__andar__predio")
            .order_by("ponto__andar__numero", "ponto__nome", "pk")
        )
        campo = self.fields["chegada"]
        campo.queryset = acessos
        campo.label_from_instance = lambda acesso: self.rotulo_local(acesso.ponto)
        primeiro_acesso = acessos.first()
        if primeiro_acesso:
            self.initial["chegada"] = primeiro_acesso.pk
        else:
            campo.required = False
            campo.empty_label = "Referência do prédio"
