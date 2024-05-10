# TriTsk
Projet Gestion de Tâches pour valider le module "Langages et Paradigmes"

## Lancement et execution
Pour un environnement de travail il faut installer Python 3.11 minimum puis suivre les instruction de [Poetry](https://python-poetry.org/docs/), cloner cet espace de depôt, puis aller dans l'espace de depôt et executer 
```shell
poetry install
```

## Pour la simple utilisation
Installer [Docker](https://www.docker.com/) puis executer le docker-compose.yml de ce dossier.
```shell
cd /ton/endroit/espace/de/depot
docker compose -f "docker-compose.yml" up -d --build 
```

Puis aller à http://localhost:7890/src/login.html