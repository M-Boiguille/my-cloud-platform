# Onboarding

Ce document décrit le fonctionnement du portfolio et le workflow utilisé pour le construire. Il sert à la fois de référence personnelle et de preuve de méthode.

## Objectif du portfolio

Construire un profil DevOps/SRE polyvalent en partant des fondations. Chaque mission est un livrable concret, relu, validé et documenté.

## Méthode

Chaque couche technologique est d'abord implémentée à la main (`raw/`), puis outillée (`tooled/`). Cela oblige à comprendre ce que chaque outil automatise avant de l'utiliser.

## Cycle d'une mission

```text
1. Mission générée et ouverte sous forme d'issue
2. Branche `mission/mcp-XXX` créée depuis main
3. Travail en local, tests avec make lint
4. Commit et push
5. Pull request ouverte
6. Revues : CodeRabbit (technique) + Lead IA (pédagogique)
7. Corrections itératives
8. Merge sur main
9. Évaluation et mise à jour du profil
10. Mission suivante générée
```

## Commandes principales

### Voir la mission en cours

```bash
python career.py --start
```

### Voir le profil

```bash
python career.py --status
```

### Générer une mission personnalisée

```bash
python career.py --custom-mission "Kubernetes pods, deployments, replicasets"
```

Forcer le niveau :

```bash
python career.py --custom-mission "Kubernetes pods" --level junior
```

Niveaux possibles : `debutant`, `junior`, `confirme`, `senior`.

Si `--level` n'est pas précisé, le moteur ajuste automatiquement la difficulté en fonction du score de la dernière mission :

| Score | Ajustement |
|-------|------------|
| ≥ 90 | Monte d'un niveau |
| 70-89 | Reste au niveau actuel |
| < 70 | Descend d'un niveau |

### Soumettre une mission

```bash
python career.py --submit
```

## Workflow Git

Les règles détaillées sont dans [GIT_WORKFLOW.md](GIT_WORKFLOW.md). En résumé :

- Branche par mission : `mission/mcp-XXX`
- Commits conventionnels : `type(scope): description`
- Pull request pour chaque livrable
- Squash ou rebase avant merge si l'historique est trop granulaire

## Checklist avant PR

```text
- [ ] make lint passe
- [ ] Les livrables attendus sont présents
- [ ] LEARNED.md est rédigé
- [ ] Le runbook est à jour
- [ ] Les commits sont propres et nommés
- [ ] La PR a un titre explicite
```

## Revue de code

Deux sources de retour sur chaque PR :

- **CodeRabbit** : analyse technique du code.
- **Lead IA** : évaluation par rapport aux critères d'acceptation de la mission.

Les retours sont traités de la même façon qu'en équipe : correction, justification ou discussion dans la PR.

## Compétences travaillées

Ce processus entraîne à :

- Versionner proprement avec Git.
- Écrire des commits et des messages de PR clairs.
- Documenter les choix techniques.
- Recevoir et intégrer une revue.
- Automatiser la qualité (lint, tests, CI/CD).
- Construire un portfolio structuré et traçable.

## Workflows automatisés

Voir [WORKFLOWS.md](WORKFLOWS.md) pour le détail des GitHub Actions.
