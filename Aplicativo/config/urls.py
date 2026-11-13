"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views.
For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:
       from my_app import views
    2. Add a URL to urlpatterns:
       path('', views.home, name='home')
Class-based views
    1. Add an import:
       from other_app.views import Home
    2. Add a URL to urlpatterns:
       path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function:
       from django.urls import include, path
    2. Add a URL to urlpatterns:
       path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from dados import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.mapa, name='home'),
    path('mapa/', views.mapa, name='mapa'),
    path('pesquisa/', views.pesquisa, name='pesquisa'),
    path('search/', views.search, name='search'),
    path('pesquisa_auditorios/', views.pesquisa_auditorios, name='pesquisa_auditorios'),
    path('laboratorios/', views.laboratorios, name='laboratorios'),
    path('kennedy/', views.predio_por_sigla, {'sigla': 'Kennedy'}, name='kennedy'),
    path('auditorios/', views.auditorios, name='auditorios'),
    path('rdc/', views.predio_por_sigla, {'sigla': 'RDC'}, name='rdc'),
    path('predios/', views.predios, name='predios'),
    path('leme/', views.predio_por_sigla, {'sigla': 'L'}, name='leme'),
    path('laboratorio-fisica/', views.laboratorio_fisica, name='laboratorio_fisica'),
    path('laboratorio-design/', views.laboratorio_design, name='laboratorio_design'),    
    path('iag/', views.predio_por_sigla, {'sigla': 'IAG'}, name='iag'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('pesquisa-sala/', views.pesquisa_sala, name='pesquisa_sala'),
    path('auditorio-rdc/', views.auditorio_rdc, name='auditorio_rdc'),
    path('auditorio-kennedy/', views.auditorio_kennedy, name='auditorio_kennedy'),
    path("espaco/<int:pk>/", views.detalhe_espaco, name="detalhe_espaco"),
    path('predio/<int:id_predio>/',views.detalhe_predio, name='detalhe_predio'),
    path('teste-base/',views.teste_base,name='teste_base'),
    path('api/dados-mapa/', views.dados_mapa, name='dados_mapa'),
]

# Serve as imagens cadastradas (media/) apenas em desenvolvimento.
# Em producao, isso deve ser feito pelo servidor web (nginx, etc.), nao pelo Django.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
