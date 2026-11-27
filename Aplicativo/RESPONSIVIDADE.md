# Responsividade do LocalizaPUC

Esta entrega adapta as telas existentes para celular, tablet e computador.
Ela foi preparada sobre a main no commit `ba217c6`, em uma branch exclusiva
`feature/p4-responsividade`. O CSS da nova página de espaços continua em seu PR
próprio; a responsividade é uma entrega que abrange a aplicação atual.

## Alterações

- Novo `static/css/responsivo.css`, carregado depois do CSS de cada tela.
- Classes `tela-*` no body para aplicar ajustes específicos sem misturar os layouts.
- Viewport nas seis telas que ainda eram exibidas com largura virtual de 980 px.
- Colunas e cartões que se reorganizam em telas estreitas, inclusive no Kennedy.
- Cabeçalhos, filtros, paginação e botões com quebra de linha quando necessário.
- Formulários que acomodam os campos e as mensagens de validação.
- Altura explícita e adaptável para o div do mapa interativo; a imagem alternativa
  continua com sua proporção original.
- Referências aos CSS existentes corrigidas em Física, Design, RDC e nos dois
  auditórios. Física e Design estavam solicitando arquivos inexistentes; RDC e
  auditórios estavam carregando estilos de outras telas.
- Remoção dos rótulos soltos `#LEME` e `#IAG` anteriores ao doctype para manter
  o modo de renderização padrão dessas duas páginas.

As consultas, rotas, models, formulários Python, migrações e o SQLite do
repositório permanecem com seu conteúdo original.

## Verificações realizadas

Ambiente: Django 5.2.19 e Chromium 153, com uma cópia separada do banco para
os testes. Os registros e as contas criados pela verificação são fictícios.

| Tamanho da janela | Uso verificado |
| --- | --- |
| 320 × 740 | Celular estreito |
| 360 × 800 | Celular |
| 390 × 844 | Celular |
| 667 × 375 | Celular na horizontal |
| 768 × 1024 | Tablet |
| 1440 × 900 | Computador |

Foram conferidas as 17 telas da aplicação atual: início, pesquisa, pesquisa de
salas, auditórios, laboratórios, prédios, Kennedy, RDC, IAG, Leme, os dois
laboratórios, os dois auditórios, mapa, login e cadastro.

O contêiner do mapa interativo foi verificado separadamente, com uma chave
fictícia e a chamada externa bloqueada. Esse teste mede a área do mapa; não
valida o funcionamento ou a precisão do serviço Google Maps.

Resultado: **122 verificações sem falhas**, incluindo dimensões de página,
carregamento de arquivos estáticos, cadastro com mensagens de erro, cadastro
válido, login, logout, nome de usuário extenso, pesquisa por prédio com nome
extenso e envio do formulário de pesquisa. Nenhuma das páginas verificadas
alargou o documento para além da janela.

Antes dos ajustes, a rodada inicial encontrou 24 falhas em 72 verificações,
além dos dois arquivos CSS inexistentes dos laboratórios.

A página reutilizável de espaços também foi conferida como componente isolado
em seis tamanhos, usando sua base de teste e dados fictícios. Ela ainda precisa
da validação integrada quando sua base compartilhada e sua URL forem incorporadas
à main.

## Conferência no projeto integrado

Com o ambiente virtual ativado, execute na raiz do repositório:

```powershell
python .\Aplicativo\manage.py check
python .\Aplicativo\manage.py runserver
```

Abra a aplicação em `http://127.0.0.1:8000/`. Nas ferramentas do navegador,
use os tamanhos da tabela e confira:

1. Ausência de rolagem horizontal da página.
2. Legibilidade dos títulos, cartões, filtros e mensagens dos formulários.
3. Acesso aos campos e botões ao rolar páginas maiores que a janela.
4. Cadastro, entrada, saída e envio da pesquisa.
5. Visibilidade do mapa, tanto com a imagem alternativa quanto com a integração
   configurada. Ilustrações com deslocamento local não devem alargar a página.

Alguns links legados ainda apontam para arquivos `.html`; sua integração com as
rotas Django continua sob responsabilidade das respectivas telas. Os testes de
layout acessaram as rotas existentes diretamente.

## Integração com a base compartilhada

A main usada nesta entrega ainda não contém `base.html`. Por isso, o stylesheet
foi vinculado às telas existentes. Ao incorporar a base compartilhada, concentre
esse carregamento nela, depois dos estilos específicos:

```html
{% load static %}
<!-- Dentro de head, mantenha tambem o charset e o titulo. -->
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<!-- CSS comum da base -->
{% block css_extra %}{% endblock %}
<link rel="stylesheet" href="{% static 'css/responsivo.css' %}">
```

Para as telas herdadas que precisam dos ajustes por categoria, a base pode
oferecer este ponto de extensão:

```html
<body class="tela-puc {% block classe_body %}{% endblock %}">
```

Cada template preserva a classe correspondente, por exemplo:

```html
{% block classe_body %}tela-busca{% endblock %}
```

As regras `.espaco-*` do stylesheet já estão preparadas para o template de
espaços. Depois de integrar as bases e os templates unificados, repita a
conferência nos mesmos tamanhos para verificar a composição final.
