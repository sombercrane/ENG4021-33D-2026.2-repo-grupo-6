from django.contrib import admin
from .models import Predio, Andar, TipoEspaco, Espaco

# Register your models here.


@admin.register(Predio)
class PredioAdmin(admin.ModelAdmin):
    list_display = ("sigla", "nome", "endereco")
    search_fields = ("nome", "sigla", "endereco")


@admin.register(Andar)
class AndarAdmin(admin.ModelAdmin):
    list_display = ("predio", "numero", "nome")
    list_filter = ("predio",)
    search_fields = ("nome", "predio__nome", "predio__sigla")


@admin.register(TipoEspaco)
class TipoEspacoAdmin(admin.ModelAdmin):
    list_display = ("nome", "cor")
    search_fields = ("nome",)


@admin.register(Espaco)
class EspacoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nome", "andar", "tipo", "acessivel")
    list_filter = ("tipo", "acessivel", "andar__predio")
    search_fields = (
        "nome",
        "codigo",
        "andar__nome",
        "andar__predio__nome",
        "andar__predio__sigla",
    )
