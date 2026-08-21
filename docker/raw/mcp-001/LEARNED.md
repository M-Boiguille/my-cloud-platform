# Ce que j'ai appris — Mission mcp-001

## Objectif

Containeriser une application web statique avec Docker et rendre l'application accessible sur `http://localhost:8080`.

## Choix techniques

### Image de base

J'ai choisi `nginx:1.31-alpine` pour épingler une version précise. Le tag flottant `nginx:alpine` peut évoluer et rendre le build non reproductible.

### Architecture du Dockerfile

```dockerfile
FROM nginx:1.31-alpine
COPY index.html /usr/share/nginx/html/
EXPOSE 80
```

- `FROM` : choix de l'image Nginx officielle, version épinglée.
- `COPY` : copie du fichier statique dans le répertoire de Nginx.
- `EXPOSE 80` : documente le port d'écoute interne du conteneur.

### Mapping de ports

La commande de lancement est :

```bash
docker run -p 8080:80 my-web-app
```

- `8080` : port accessible sur la machine hôte.
- `80` : port d'écoute à l'intérieur du conteneur.

### Pourquoi pas un utilisateur non-root

J'ai testé une version non-root écoutant sur le port 8080. Cela nécessite de modifier `nginx.conf`, de gérer le PID et les permissions. Pour une mission débutante, cette complexité sort du périmètre. Elle sera traitée dans une mission SRE ou DevSecOps dédiée.

## Commandes vérifiées

| Commande | Usage |
|----------|-------|
| `docker build -t my-web-app .` | Construire l'image |
| `docker run -p 8080:80 my-web-app` | Lancer le conteneur |
| `docker ps` | Voir les conteneurs actifs |
| `docker images` | Voir les images locales |
| `docker logs my-web-app-container` | Consulter les logs |

## Liens de documentation

- [Dockerfile reference](https://docs.docker.com/engine/reference/builder/)
- [Docker run](https://docs.docker.com/engine/reference/commandline/run/)
- [Nginx Docker image](https://hub.docker.com/_/nginx)
