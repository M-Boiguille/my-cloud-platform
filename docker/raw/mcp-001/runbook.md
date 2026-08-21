# RUNBOOK d'exécution de l'application (my-web-app)

## Contexte

Procédure d'assemblage (build) et de déploiement du conteneur de l'application web `my-web-app` à partir du Dockerfile du projet.

## Informations

Toutes les commandes indiquées doivent se faire dans ce dossier du repo :

```text
my-cloud-platform/docker/raw/mcp-001/
```

## Commandes clés

### Build de l'image

```bash
docker build -t my-web-app .
```

### Lancement du conteneur

```bash
docker run -d --name my-web-app-container -p 8080:80 my-web-app
```

### Vérification de l'accessibilité

```bash
curl http://localhost:8080
```

### Vérification des conteneurs et images

```bash
docker ps
docker images
```

## Oneliner

Procédure rapide d'assemblage et de relance en une seule ligne (mode détruit/remplacé) :

```bash
docker rm -f my-web-app-container && docker build -t my-web-app . && docker run --name my-web-app-container -d -p 8080:80 my-web-app
```

## Diagnostic

Vérifier l'état du conteneur et inspecter ses journaux d'exécution :

```bash
docker ps -a --filter name=my-web-app-container
docker logs my-web-app-container
```

## Rollback

En cas d'erreur au lancement ou de besoin de réinitialiser complètement l'environnement :

```bash
docker stop my-web-app-container
docker rm my-web-app-container
```

## Leçons

- **Mode détaché (`-d`) :** À privilégier pour éviter de bloquer le terminal et garantir l'exécution continue du service.
- **Nommage explicite (`--name`) :** Facilite les commandes d'administration (`docker logs`, `docker stop`) sans chercher l'identifiant court du conteneur.
- **Mapping de ports :** La commande `docker run -p 8080:80` expose le port 8080 de la machine hôte et redirige vers le port 80 du conteneur, qui est le port d'écoute par défaut de Nginx.
