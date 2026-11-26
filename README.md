# ENG4021-33D-2026.2-repo-grupo-6

## Navegação interna do Localiza PUC

Com o ambiente Django ativo, execute em `Aplicativo`:

```powershell
python manage.py migrate
python manage.py test dados
python manage.py runserver
```

Na página de um prédio, selecione um andar para consultar a planta, os espaços e os pontos de interesse. Abra **Planejar trajeto no prédio** para escolher os pontos de partida e de destino.

No Django Admin, cadastre os pontos nos respectivos andares e as **Conexões internas** entre eles. Informe o tipo, a distância em metros e se cada trecho pode ser percorrido nos dois sentidos. Vincule cada espaço a um **Ponto de acesso** no mesmo andar para incluí-lo nos trajetos. As rotas usam essas conexões e o cadastro pode ter cobertura parcial.
