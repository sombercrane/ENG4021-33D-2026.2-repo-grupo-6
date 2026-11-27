from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AulaForm
from .models import Aula, Espaco, Ponto, Predio


def predio_por_sigla(request, sigla):
    predio = get_object_or_404(Predio, sigla__iexact=sigla)
    return redirect('detalhe_predio', id_predio=predio.pk)


def cadastro(request):
    if request.method == 'POST':
        formulario = UserCreationForm(request.POST)

        if formulario.is_valid():
            usuario = formulario.save()
            login(request, usuario)
            return redirect('home')
    else:
        formulario = UserCreationForm()

    return render(request, 'cadastro.html', {
        'formulario': formulario
    })


login_view = LoginView.as_view(template_name="login.html", next_page="home")


def logout_view(request):
    if request.method == 'POST':
        logout(request)

    return redirect('home')


def detalhe_espaco(request, pk):
    espacos = Espaco.objects.select_related("andar__predio", "tipo")
    espaco = get_object_or_404(espacos, pk=pk)

    outros_espacos = (
        Espaco.objects.filter(andar_id=espaco.andar_id)
        .exclude(pk=espaco.pk)
        .select_related("tipo")
        .order_by("nome", "pk")[:4]
    )

    return render(request, "espaco.html", {
        "espaco": espaco,
        "outros_espacos": outros_espacos,
    })


def detalhe_predio(request, id_predio):
    predio = get_object_or_404(Predio, pk=id_predio)
    andares = list(predio.andares.order_by('numero', 'pk'))
    andar = None
    andar_id = request.GET.get('andar')
    if andar_id:
        andar = next((item for item in andares if str(item.pk) == andar_id), None)
        if andar is None:
            raise Http404('Andar não encontrado neste prédio.')
    elif andares:
        andar = next((item for item in andares if item.numero == 0), andares[0])

    espacos = pontos = ()
    if andar:
        espacos = andar.espacos.select_related('tipo').order_by('nome', 'pk')
        pontos = andar.pontos.select_related('tipo_ponto').order_by('nome', 'pk')

    return render(request, 'base_predio.html', {
        'predio': predio,
        'andares': andares,
        'andar': andar,
        'espacos': espacos,
        'pontos': pontos,
    })


def dados_mapa(request):
    espacos = Espaco.objects.select_related(
        "andar__predio", "tipo"
    ).all()

    pontos = Ponto.objects.select_related(
        "andar__predio", "tipo_ponto"
    ).all()

    dados = []

    for espaco in espacos:
        dados.append({
            "id": espaco.id_espaco,
            "nome": espaco.nome,
            "codigo": espaco.codigo,
            "tipo": espaco.tipo.nome,
            "predio": espaco.andar.predio.sigla,
            "andar": espaco.andar.nome,
            "posicao_x": espaco.posicao_x,
            "posicao_y": espaco.posicao_y,
            "acessivel": espaco.acessivel,
            "categoria": "espaco",
        })

    for ponto in pontos:
        dados.append({
            "id": ponto.id_ponto,
            "nome": ponto.nome,
            "tipo": ponto.tipo_ponto.nome,
            "predio": ponto.andar.predio.sigla,
            "andar": ponto.andar.nome,
            "posicao_x": ponto.posicao_x,
            "posicao_y": ponto.posicao_y,
            "categoria": "ponto",
        })

    return JsonResponse(dados, safe=False)

@login_required(login_url="login")
def minha_grade(request):
    aulas = (
        Aula.objects.filter(usuario=request.user)
        .select_related("sala__andar__predio", "sala__tipo")
    )
    return render(request, "grade.html", {
        "aulas": aulas,
        "formulario": AulaForm(),
        "titulo": "Cadastrar aula",
    })

@login_required(login_url="login")
def cadastrar_aula(request):
    formulario = AulaForm(
        request.POST if request.method == "POST" else None
    )

    if request.method == "POST" and formulario.is_valid():
        dados = formulario.cleaned_data

        with transaction.atomic():
            for dia in dados["dias_semana"]:
                Aula.objects.create(
                    usuario=request.user,
                    disciplina=dados["disciplina"],
                    dia_semana=dia,
                    horario_inicio=dados["horario_inicio"],
                    horario_fim=dados["horario_fim"],
                    sala=dados["sala"],
                )

        return redirect("minha_grade")

    return render(request, "grade.html", {
        "formulario": formulario,
        "titulo": "Cadastrar aula",
    })

@login_required(login_url="login")
def editar_aula(request, pk):
    aula = get_object_or_404(
        Aula, pk=pk, usuario=request.user
    )
    formulario = AulaForm(
        request.POST if request.method == "POST" else None,
        instance=aula,
    )

    if request.method == "POST" and formulario.is_valid():
        formulario.save()
        return redirect("minha_grade")

    return render(request, "grade.html", {
        "formulario": formulario,
        "titulo": "Editar aula",
    })


@login_required(login_url="login")
def remover_aula(request, pk):
    aula = get_object_or_404(
        Aula, pk=pk, usuario=request.user
    )

    if request.method == "POST":
        aula.delete()
        return redirect("minha_grade")

    return render(request, "grade.html", {
        "aula": aula,
        "confirmar_remocao": True,
    })
