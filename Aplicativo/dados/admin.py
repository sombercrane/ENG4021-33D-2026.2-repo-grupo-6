from django.contrib import admin
from .models import AcessoExterno, Andar, Conexao, Espaco, Ponto, Predio, TipoEspaco, TipoPonto

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
    autocomplete_fields = ("ponto_acesso",)
    search_fields = (
        "nome",
        "codigo",
        "andar__nome",
        "andar__predio__nome",
        "andar__predio__sigla",
    )

@admin.register(TipoPonto)
class TipoPontoAdmin(admin.ModelAdmin):
    list_display = ("nome", "icone", "cor")
    search_fields = ("nome", "descricao")


@admin.register(Ponto)
class PontoAdmin(admin.ModelAdmin):
    list_display = ("nome", "andar", "tipo_ponto", "posicao_x", "posicao_y")
    list_filter = ("tipo_ponto", "andar__predio")
    search_fields = ("nome", "descricao", "andar__nome", "andar__predio__nome")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("andar__predio", "tipo_ponto")


@admin.register(Conexao)
class ConexaoAdmin(admin.ModelAdmin):
    list_display = ("origem", "destino", "tipo", "distancia_m", "bidirecional")
    list_filter = ("origem__andar__predio", "tipo", "bidirecional")
    list_select_related = ("origem__andar__predio", "destino__andar__predio")
    autocomplete_fields = ("origem", "destino")
    search_fields = ("nome", "origem__nome", "destino__nome")


@admin.register(AcessoExterno)
class AcessoExternoAdmin(admin.ModelAdmin):
    list_display = ("ponto", "latitude", "longitude")
    list_filter = ("ponto__andar__predio",)
    list_select_related = ("ponto__andar__predio",)
    autocomplete_fields = ("ponto",)
    search_fields = ("ponto__nome", "ponto__andar__predio__nome")
