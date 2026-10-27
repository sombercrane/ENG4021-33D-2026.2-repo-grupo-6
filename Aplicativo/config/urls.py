"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from dados import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('mapa/', views.mapa, name='mapa'),
    path('pesquisa/', views.pesquisa, name='pesquisa'),
    path('search/', views.search, name='search'),
    path('pesquisa-auditorios/', views.pesquisa_auditorios, name='pesquisa-auditorios'),
    path('laboratorios/', views.laboratorios, name='laboratorios'),
    path('kennedy/', views.kennedy, name='kennedy'),
    path('auditorios/', views.auditorios, name='auditorios'),
    path('rdc/', views.rdc, name='rdc'),
    path('predios/', views.predios, name='predios'),
    path('leme/', views.leme, name='leme'),
    path('laboratorio-fisica/', views.laboratorio_fisica, name='laboratorio_fisica'),
    path('laboratorio-design/', views.laboratorio_design, name='laboratorio_design'),    
    path('iag/', views.iag, name='iag'),
]
