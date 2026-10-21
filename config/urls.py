
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.home, name='home'),
    path('pesquisa/', views.pesquisa, name='pesquisa'),
    path('mapa/', views.mapa, name='mapa'),
    path('search/', views.search, name='search'),
    path('leme/', views.leme, name='leme'),
    path('iag/', views.iag, name='iag'),
    path('kennedy/', views.kennedy, name='kennedy'),
    path('rdc/', views.rdc, name='rdc'),
    path('auditorios/', views.auditorios, name='auditorios'),
    path('laboratorios/', views.laboratorios, name='laboratorios'),
    path('predios/', views.predios, name='predios'),
]


