# Integração com API externa — Google Maps

## O que é

O LocalizaPUC vai integrar a Google Maps JavaScript API para substituir a imagem estática do mapa do campus (tela "Mapa") por um mapa interativo real, com marcadores clicáveis indicando a localização de cada prédio cadastrado.

## Por que essa API

* É gratuita até um volume alto de uso (crédito mensal da Google Cloud), suficiente para um projeto acadêmico.
* Tem suporte nativo a marcadores, janelas de informação (info windows) e zoom/arraste, sem precisar implementar nada disso do zero.
* É a referência mais usada do mercado para esse tipo de funcionalidade, o que facilita encontrar documentação e exemplos.

## O que muda no sistema

* Modelo Predio: ganha dois campos novos, latitude e longitude (tipo DecimalField), para guardar a posição real de cada prédio no mapa.
* Banco de dados: migração do Django para adicionar essas duas colunas.
* Admin do Django: os campos de latitude/longitude ficam visíveis e editáveis no cadastro de cada prédio.
* View mapa: passa a buscar todos os Predio cadastrados e enviá-los para o template, em vez de só renderizar uma página estática.
* Template Mapa-HTML.html: a tag img do mapa estático é trocada pelo script da Google Maps JavaScript API, que desenha o mapa e cria um marcador para cada prédio (usando nome e sigla no texto do marcador).

## Como a chave de API é tratada

A chave da Google Maps API não é commitada no repositório. Ela fica guardada numa variável de ambiente (GOOGLE_MAPS_API_KEY), lida pelo settings.py do Django e passada para o template na hora de renderizar a página. Cada pessoa que for rodar o projeto localmente precisa:

* Criar uma chave própria no Google Cloud Console (console.cloud.google.com/google/maps-apis), ativando a "Maps JavaScript API".
* Criar um arquivo .env local (fora do controle de versão) com a linha GOOGLE_MAPS_API_KEY=sua-chave-aqui
* O .env já está (ou deve estar) listado no .gitignore, para garantir que a chave de ninguém vá parar no GitHub por engano.

## Coordenadas iniciais

As coordenadas dos prédios já cadastrados (Kennedy, IAG, Leme, RDC etc.) serão preenchidas manualmente com a localização real de cada prédio no campus da PUC-Rio (Gávea, Rio de Janeiro), usando o Google Maps como referência para pegar latitude/longitude.
