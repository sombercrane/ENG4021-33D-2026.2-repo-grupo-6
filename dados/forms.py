from django import forms


class PesquisaEspacoForm(forms.Form):
    busca = forms.CharField(
        required=False,
        max_length=150,
        label="Pesquisar espaço",
        widget=forms.TextInput(attrs={
            "placeholder": "Buscar sala, prédio ou código",
            "class": "campo-busca"
        })
    )