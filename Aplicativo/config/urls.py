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
from dados import views, views_mapa, views_rotas
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views_mapa.mapa, name='home'),
    path('mapa/', views_mapa.mapa, name='mapa'),
    path('pesquisa/', views_mapa.redirecionar_busca, name='pesquisa'),
    path('search/', views_mapa.redirecionar_busca, name='search'),
    path('pesquisa_auditorios/', views_mapa.redirecionar_busca, {'categoria': 'auditorio'}, name='pesquisa_auditorios'),
    path('laboratorios/', views_mapa.redirecionar_busca, {'categoria': 'laboratorio'}, name='laboratorios'),
    path('kennedy/', views.predio_por_sigla, {'sigla': 'Kennedy'}, name='kennedy'),
    path('auditorios/', views_mapa.redirecionar_busca, {'categoria': 'auditorio'}, name='auditorios'),
    path('rdc/', views.predio_por_sigla, {'sigla': 'RDC'}, name='rdc'),
    path('predios/', views_mapa.redirecionar_busca, {'categoria': 'predio'}, name='predios'),
    path('leme/', views.predio_por_sigla, {'sigla': 'L'}, name='leme'),
    path('laboratorio-fisica/', views_mapa.redirecionar_busca, {'categoria': 'laboratorio'}, name='laboratorio_fisica'),
    path('laboratorio-design/', views_mapa.redirecionar_busca, {'categoria': 'laboratorio'}, name='laboratorio_design'),
    path('iag/', views.predio_por_sigla, {'sigla': 'IAG'}, name='iag'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('pesquisa-sala/', views_mapa.redirecionar_busca, {'categoria': 'sala'}, name='pesquisa_sala'),
    path('auditorio-rdc/', views_mapa.redirecionar_busca, {'categoria': 'auditorio', 'busca': 'RDC'}, name='auditorio_rdc'),
    path('auditorio-kennedy/', views_mapa.redirecionar_busca, {'categoria': 'auditorio', 'busca': 'Kennedy'}, name='auditorio_kennedy'),
    path("espaco/<int:pk>/", views.detalhe_espaco, name="detalhe_espaco"),
    path('predio/<int:id_predio>/',views.detalhe_predio, name='detalhe_predio'),
    path('predio/<int:id_predio>/rota/', views_rotas.rota_predio, name='rota_predio'),
    path('predio/<int:id_predio>/rota-externa/', views_rotas.rota_externa_predio, name='rota_externa_predio'),
    path('buscar-rota/', views_rotas.buscar_rota, name='buscar_rota'),
    path('banheiro-proximo/', views_mapa.banheiro_proximo, name='banheiro_proximo'),
    path('teste-base/', views_mapa.redirecionar_busca, name='teste_base'),
    path('api/dados-mapa/', views.dados_mapa, name='dados_mapa'),
    path('api/sugestoes/', views_mapa.sugestoes_pesquisa, name='sugestoes_pesquisa'),
    path('grade/', views.minha_grade, name='minha_grade'),
    path('grade/nova/', views.cadastrar_aula, name='cadastrar_aula'),
    path('grade/<int:pk>/editar/', views.editar_aula, name='editar_aula'),
    path('grade/<int:pk>/remover/', views.remover_aula, name='remover_aula'),
]

# Serve as imagens cadastradas (media/) apenas em desenvolvimento.
# Em producao, isso deve ser feito pelo servidor web (nginx, etc.), nao pelo Django.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
