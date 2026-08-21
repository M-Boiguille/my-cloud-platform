# Conventions Git

Ce document fixe les règles de nommage des branches et des commits pour maintenir un historique lisible par un recruteur.

## Branches

### Missions

```text
mission/mcp-XXX
```

Exemple : `mission/mcp-001`

### Corrections ou travaux annexes

```text
type/description-courte
```

| Préfixe | Usage |
|---------|-------|
| `feat/` | Nouvelle fonctionnalité |
| `fix/` | Correction de bug |
| `docs/` | Documentation |
| `refactor/` | Refactoring |
| `test/` | Tests |
| `chore/` | Maintenance |
| `infra/` | Infrastructure |
| `sec/` | Sécurité |

Exemples :

```text
feat/missions-page
fix/dashboard-json
docs/runbook-mcp-001
chore/update-deps
```

## Commits

Format : `type(scope): message`

```text
type(scope): description en minuscules, impératif, 72 caractères max
```

### Types autorisés

| Type | Usage |
|------|-------|
| `mission` | Livrable d'une mission |
| `feat` | Nouvelle fonctionnalité du moteur ou du site |
| `fix` | Correction |
| `docs` | Documentation |
| `style` | Mise en forme sans changement de logique |
| `refactor` | Refactoring |
| `test` | Tests |
| `chore` | Tâches de maintenance |
| `infra` | Infrastructure / Terraform |
| `sec` | Sécurité |
| `perf` | Performance |
| `sim` | Simulation / scénarios |

### Exemples de commits

```text
mission(mcp-001): add Dockerfile and static index
feat(dashboard): add missions timeline
fix(state): handle missing courses file
docs(README): update employability path
chore(ci): update commitlint workflow
```

### Règles

1. Écrire au présent impératif.
2. Pas de majuscule au début du message.
3. Pas de point final.
4. Description concise, moins de 72 caractères.
5. Utiliser `scope` quand c'est pertinent.

## Workflow type

```text
git checkout main
git pull
git checkout -b mission/mcp-001
# travail
git add .
git commit -m "mission(mcp-001): containerize web app with nginx"
git push -u origin mission/mcp-001
gh pr create --title "[Mission mcp-001] solution" --body "Mission mcp-001"
```
