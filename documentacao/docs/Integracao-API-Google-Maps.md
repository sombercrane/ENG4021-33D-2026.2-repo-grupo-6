# Integração com o Google Routes

O mapa do campus usa Leaflet e OpenStreetMap. O Google Routes calcula os trajetos a pé a partir da localização autorizada pelo usuário ou de uma entrada escolhida como referência.

## Configuração do serviço de rotas

Ative a Routes API no projeto Google Cloud e configure a variável `GOOGLE_ROUTES_API_KEY` no ambiente do processo Django. A chave é usada pelo servidor. Ao iniciar pelo PowerShell, atribua a variável na mesma sessão em que executará `manage.py runserver`. [Documentação da Routes API](https://developers.google.com/maps/documentation/routes/compute_route_directions)

No admin, cadastre o acesso externo com latitude, longitude e o ponto interno correspondente. No mapa, escolha uma origem, abra um marcador e selecione **Partir da origem no mapa**. Depois de escolher a chegada e o destino, use **Calcular trajeto** para enviar as coordenadas ao Google.

O trecho interno é combinado com o externo quando a chegada calculada está a até 30 m do acesso. A disponibilidade de um percurso interno acessível depende da configuração e da verificação das conexões do prédio. As condições de acessibilidade do trecho a pé devem ser verificadas separadamente.
