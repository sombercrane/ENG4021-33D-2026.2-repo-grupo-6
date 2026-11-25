# ENG4021-33D-2026.2-repo-grupo-6

## Navegação interna do Localiza PUC

Com o ambiente Django ativo, execute os comandos na pasta `Aplicativo`.

```powershell
python manage.py migrate
python manage.py test dados
python manage.py runserver
```

Na página de um prédio, selecione um andar para consultar a planta, os espaços e os pontos de interesse. Abra **Planejar trajeto no prédio** para escolher os pontos de partida e de destino.

No Django Admin, cadastre os pontos nos respectivos andares e as **Conexões internas** entre eles. Informe o tipo, a distância em metros e se cada trecho pode ser percorrido nos dois sentidos. Vincule cada espaço a um **Ponto de acesso** no mesmo andar para incluí-lo nos trajetos. As rotas usam essas conexões e o cadastro pode ter cobertura parcial.

Para conectar o mapa ao trajeto interno, cadastre os **Acessos externos** no Admin, com as coordenadas e o ponto interno correspondente. Defina `GOOGLE_ROUTES_API_KEY` no ambiente do Django com a chave da [Google Routes API](https://developers.google.com/maps/documentation/routes/compute_route_directions). No mapa, defina a origem, abra o pin do local e selecione **Partir da origem no mapa**.

O trecho externo é apresentado em texto e usado para continuar a partir do acesso cadastrado quando a chegada retornada está a até 30 m dele. Quando o prédio tem apenas uma coordenada de referência, a aplicação mostra o trajeto até a região do prédio e o andar do destino.

Para disponibilizar o percurso interno acessível, verifique as condições no local e marque **Acessibilidade verificada** em cada conexão sem degraus. Marque também **Acessível** no espaço de destino. Ao selecionar **Usar percurso interno acessível**, a aplicação procura apenas corredores, passagens, elevadores e rampas verificados. O cálculo a pé do trecho externo não confirma sua acessibilidade.
