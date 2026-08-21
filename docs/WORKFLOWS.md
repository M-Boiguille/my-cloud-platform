# Workflows GitHub Actions

Ce fichier liste tous les workflows automatisés du projet et explique leur rôle.

## Workflows actifs

### `generate-mission.yml`

- **Déclencheur** : manuel (`workflow_dispatch`)
- **Rôle** : Génère la prochaine mission avec le PO IA
- **Déclenchement** : Lancer manuellement quand une nouvelle mission automatique est nécessaire

```bash
gh workflow run generate-mission
```

### `review-mission.yml`

- **Déclencheur** : `pull_request` sur une branche `mission/mcp-*`
- **Rôle** : Relit la PR avec le Lead IA pédagogique
- **Déclenchement** : Automatique à l'ouverture/mise à jour d'une PR de mission

### `complete-mission.yml`

- **Déclencheur** : `pull_request` fermée et mergée sur une branche `mission/mcp-*`
- **Rôle** : Évalue la mission, met à jour `data/progress.yml`, génère la mission suivante
- **Déclenchement** : Automatique après merge

### `commitlint.yml`

- **Déclencheur** : `push`, `pull_request`
- **Rôle** : Vérifie que les messages de commit respectent Conventional Commits
- **Déclenchement** : À chaque push

### `update-dashboard.yml`

- **Déclencheur** : `push` sur `main`
- **Rôle** : Met à jour `web/metrics.json` et `web/missions.json`
- **Déclenchement** : Automatique

### `pages.yml`

- **Déclencheur** : push modifiant `web/**` ou `data/**`, `workflow_dispatch`
- **Rôle** : Déploie le site sur GitHub Pages
- **Déclenchement** : Automatique

## Review externe

### CodeRabbit

- **Type** : Application GitHub (pas de YAML)
- **Rôle** : Review technique automatique à chaque PR
- **Utilisation** : Automatique

## En résumé

En pratique, le workflow est le suivant :

1. La branche est poussée.
2. `commitlint.yml` vérifie les messages de commit.
3. `review-mission.yml` et CodeRabbit relisent la PR.
4. Au merge, `complete-mission.yml` valide la mission.
