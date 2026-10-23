from django.contrib import admin

# Register your models here.

from .models import Predio, Andar

admin.site.register(Predio)
admin.site.register(Andar)