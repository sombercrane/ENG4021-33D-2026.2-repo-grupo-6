# Localiza PUC

O Localiza PUC reúne o mapa da PUC-Rio, a busca de prédios, espaços e pontos de interesse, a grade de aulas e o planejamento de trajetos internos.

## Executar localmente

Use Python 3.12 ou superior. Execute os comandos abaixo no PowerShell a partir da raiz do repositório.

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r Aplicativo\requirements.txt
Set-Location Aplicativo
..\.venv\Scripts\python.exe manage.py migrate
..\.venv\Scripts\python.exe manage.py preparar_demonstracao
..\.venv\Scripts\python.exe manage.py runserver
```

Abra [Localiza PUC](http://127.0.0.1:8000/). Busque por um código como `K117` ou uma categoria como **Entradas**. Em **Abrir prédio de demonstração**, escolha **Planejar trajeto no prédio**, o ponto **Entrada de demonstração** e a sala **DEMO101**. O percurso comum passa pela escada. Com **Usar percurso interno acessível**, o trajeto passa pelo elevador. O prédio e as suas plantas são fictícios.

As migrações carregam o catálogo do campus em `Aplicativo/db.local.sqlite3`, sem contas de demonstração. `preparar_demonstracao` acrescenta o prédio fictício e suas plantas. Para usar o admin, crie uma conta local com `manage.py createsuperuser`.

## Dados do campus e atualização do banco

Para atualizar um SQLite existente, aponte a variável de ambiente `DJANGO_DB_PATH` para uma cópia do arquivo e execute `manage.py migrate`. As migrações aproveitam os registros existentes e incorporam o catálogo do campus. Se o banco veio da antiga `main`, a tabela de conexões anterior fica arquivada dentro da cópia.

No admin, cadastre os pontos nos andares e vincule cada espaço a um **Ponto de acesso**. Preencha o tipo e a distância medida das conexões e marque **Validada** após conferir o trecho. Para o modo acessível, verifique as condições no local e marque **Acessibilidade verificada** em cada conexão sem degraus e **Acessível** no espaço de destino. Os percursos reais dependem dos trechos validados. Carregue a imagem de cada andar no campo **Imagem mapa**.

Para calcular um trajeto a pé, defina `GOOGLE_ROUTES_API_KEY` no ambiente do servidor e selecione uma origem no mapa. O trajeto continua no interior quando há um **Acesso externo** cadastrado com coordenadas e a chegada informada pelo Google está a até 30 m dele. [Integração com o Google Routes](documentacao/docs/Integracao-API-Google-Maps.md)

## Verificações e publicação

Execute na pasta `Aplicativo`.

```powershell
..\.venv\Scripts\python.exe manage.py check
..\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
..\.venv\Scripts\python.exe manage.py test dados
```

Configure `DJANGO_DEBUG=0`, `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS` e HTTPS para publicar. Execute `manage.py collectstatic` e sirva os diretórios de arquivos estáticos e de mídia pelo servidor web. `DJANGO_MEDIA_ROOT` permite indicar outro diretório para as imagens. A configuração de HSTS para subdomínios e preload pode ser ativada pelo operador com `DJANGO_HSTS_SECONDS`, `DJANGO_HSTS_INCLUDE_SUBDOMAINS` e `DJANGO_HSTS_PRELOAD` conforme o domínio.
