from django import forms

from .models import Andar, Predio, Aula, Espaco

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

class AulaForm(forms.ModelForm):
    dias_semana = forms.TypedMultipleChoiceField(
        choices=Aula.DIAS_SEMANA,
        coerce=int,
        widget=forms.CheckboxSelectMultiple,
        label="Dias da semana",
    )

    class Meta:
        model = Aula
        fields = [
            "disciplina",
            "dias_semana",
            "dia_semana",
            "horario_inicio",
            "horario_fim",
            "sala",
        ]
        labels = {
            "disciplina": "Disciplina",
            "dia_semana": "Dia da semana",
            "horario_inicio": "Horário de início",
            "horario_fim": "Horário de término",
            "sala": "Sala ou espaço da aula",
        }
        widgets = {
            "horario_inicio": forms.TimeInput(
                format="%H:%M",
                attrs={
                    "type": "text",
                    "placeholder": "Ex.: 08:00",
                    "pattern": "([01][0-9]|2[0-3]):[0-5][0-9]",
                    "maxlength": "5",
                },
            ),
            "horario_fim": forms.TimeInput(
                format="%H:%M",
                attrs={
                    "type": "text",
                    "placeholder": "Ex.: 14:30",
                    "pattern": "([01][0-9]|2[0-3]):[0-5][0-9]",
                    "maxlength": "5",
                },
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields.pop("dias_semana")
        else:
            self.fields.pop("dia_semana")

        for nome in ("horario_inicio", "horario_fim"):
            self.fields[nome].input_formats = ["%H:%M"]
            self.fields[nome].help_text = (
                "Use o formato de 24 horas: HH:MM."
            )

        for nome, campo in self.fields.items():
            if nome != "dias_semana":
                campo.widget.attrs["class"] = "campo"

        self.fields["sala"].queryset = (
            Espaco.objects.select_related("andar__predio", "tipo")
            .order_by("andar__predio__nome", "codigo", "nome")
        )
        self.fields["sala"].empty_label = "Selecione o espaço"
        self.fields["sala"].label_from_instance = (
            lambda e: (
                f"{e.codigo} — {e.nome} — "
                f"{e.andar.predio.sigla} / {e.andar.nome}"
            )
        )