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



# Formulario de pesquisa de predios
class PesquisaPredioForm(forms.Form):
    busca = forms.CharField(
        required=False,
        max_length=150,
        label="Pesquisar prédio",
        widget=forms.TextInput(attrs={
            "placeholder": "Digite o nome ou sigla do prédio",
            "class": "campo-busca"
        })
    )
