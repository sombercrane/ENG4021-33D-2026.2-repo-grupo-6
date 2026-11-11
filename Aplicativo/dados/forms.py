from django import forms

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


PesquisaEspacoForm = PesquisaForm
PesquisaAuditorioForm = PesquisaForm
PesquisaPredioForm = PesquisaForm
PesquisaLaboratorioForm = PesquisaForm