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


#Formulário Auditórios 
class PesquisaAuditorioForm(forms.Form):
    busca = forms.CharField(
        required=False,
        max_length=150,
        label="Pesquisar auditório",
        widget=forms.TextInput(attrs={
            "placeholder": "Auditórios",
            "class": "campo-busca"
        })
    )


class PesquisaLaboratorioForm(forms.Form):
    busca = forms.CharField(
        required=False,
        max_length=150,
        label="Pesquisar laboratório",
        widget=forms.TextInput(attrs={
            "placeholder": "Digite o nome ou código do laboratório",
            "class": "campo-busca"
        })
    )