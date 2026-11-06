from django.contrib import admin
from .models import Predio, Andar, TipoEspaco, Espaco

# Register your models here.


admin.site.register(Predio)
admin.site.register(Andar)
admin.site.register(TipoEspaco)
admin.site.register(Espaco)
