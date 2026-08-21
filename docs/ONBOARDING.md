# Guide du débutant autodidacte

Bienvenue dans `my-cloud-platform`. Ce guide t'explique comment utiliser ce portfolio pour apprendre à travailler en équipe, comme dans une vraie entreprise.

## Pourquoi ce guide

Tu es autodidacte. Tu apprends seul. Mais en entreprise, tu ne travailleras **jamais** seul. Ce portfolio te fait pratiquer les rituels d'une équipe DevOps/SRE :

- Les branches Git
- Les *pull requests*
- Les revues de code
- Les conventions de commit
- Les *pipelines* CI/CD
- La documentation technique

Un recruteur qui lira ce repo verra non seulement tes compétences techniques, mais aussi que tu sais déjà travailler proprement en équipe.

## Objectif

Construire un portfolio DevOps/SRE en partant de zéro. Chaque mission est un mini-projet. Tu le réalises, un Lead IA (comme un senior) le relit, et tu le corriges jusqu'à validation.

## Workflow d'une mission

```text
1. Récupérer la mission en cours
2. Créer une branche mission/mcp-XXX
3. Travailler en local
4. Tester avec make lint
5. Commit et push
6. Ouvrir une pull request
7. Recevoir les retours (CodeRabbit + Lead IA)
8. Corriger
9. Merger
10. Passer à la mission suivante
```

## Commandes essentielles

### Voir la mission en cours

```bash
python career.py --start
```

### Voir ton profil

```bash
python career.py --status
```

### Générer une mission personnalisée

```bash
python career.py --custom-mission "Kubernetes pods, deployments, replicasets"
```

### Soumettre une mission

```bash
python career.py --submit
```

## Git : le workflow d'entreprise

Ce portfolio impose le même workflow que tu trouveras dans la plupart des équipes DevOps.

### Branches

| Type | Format | Exemple |
|------|--------|---------|
| Mission | `mission/mcp-XXX` | `mission/mcp-001` |
| Correction | `fix/...` | `fix/dashboard-json` |
| Outil | `chore/...` | `chore/local-lint` |
| Documentation | `docs/...` | `docs/runbook-mcp-001` |

### Commits

Chaque commit doit être clair. Format : `type(scope): description`

```text
mission(mcp-001): containerize web app with nginx
feat(dashboard): add missions timeline
fix(state): handle missing courses file
docs(README): update employability path
```

Pour les règles détaillées, voir [GIT_WORKFLOW.md](GIT_WORKFLOW.md).

## Avant d'ouvrir une PR

Checklist à suivre :

```text
- [ ] J'ai testé ma mission en local
- [ ] make lint est vert
- [ ] J'ai un fichier LEARNED.md qui explique mes choix
- [ ] Mon runbook est à jour
- [ ] J'ai squashe mes commits si nécessaire
- [ ] La PR est ouverte avec un titre clair
```

## La revue de code

Deux outils relisent ton travail :

1. **CodeRabbit** : review technique automatique.
2. **Lead IA** : review pédagogique basée sur les critères de la mission.

### Comment répondre

Tu n'as pas besoin de tout corriger. Si tu n'es pas d'accord, explique dans la PR pourquoi. Ce qui compte, c'est la discussion.

Exemple :

```text
Merci pour le retour. J'ai modifié le Dockerfile pour utiliser nginx:1.31-alpine
et j'ai documenté ce choix dans LEARNED.md.
```

## Pour le recruteur

Ce repo démontre que l'auteur sait :

- Utiliser Git en équipe (branches, PR, squash).
- Écrire des commits conventionnels.
- Documenter ses décisions techniques.
- Accepter et appliquer une revue de code.
- Automatiser avec CI/CD (GitHub Actions).
- Construire un portfolio structuré et progressif.

L'historique des PRs et des issues est public. Le recruteur peut voir le processus, pas seulement le résultat final.

## Prochaines étapes

1. Lire la mission en cours : `python career.py --start`
2. Créer ta branche : `git checkout -b mission/mcp-XXX`
3. Ouvrir une PR quand c'est prêt.

Pour aller plus loin, voir :

- [GIT_WORKFLOW.md](GIT_WORKFLOW.md) : détail des branches et commits
- [WORKFLOWS.md](WORKFLOWS.md) : les GitHub Actions du projet
