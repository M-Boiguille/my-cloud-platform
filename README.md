# My Cloud Platform

Portfolio DevOps / SRE construit mission par mission, depuis les fondations jusqu'à l'ingénierie de plateforme.

## Approche

Chaque couche est d'abord implémentée **à la main** (`raw/`), puis industrialisée avec l'outillage standard (`tooled/`). Cette méthode oblige à comprendre ce que chaque abstraction cache avant de l'utiliser.

## Parcours

```
1 — Linux et scripting Bash/Python
2 — Docker : images, conteneurs, réseaux
3 — AWS + Terraform : infrastructure as code
4 — CI/CD avec GitHub Actions
5 — Kubernetes : k3s/EKS, manifests
6 — SRE / Observabilité : Prometheus, Grafana
7 — DevSecOps : sécurité, GitOps, cosign
8 — Platform Engineering
```

## Moteur de missions

Le moteur dans `core/` génère le contexte de chaque mission, ouvre l'issue associée, relit les PR et évalue la progression. Les livrables sont écrits manuellement.

## Qualité et workflow

- Conventional commits, lint et type checking en local.
- Branches par mission, pull requests et revues (CodeRabbit + Lead IA).
- CI/CD avec GitHub Actions : commitlint, review, merge, dashboard, Pages.
- Documentation structurée : runbooks, decisions, `LEARNED.md`.

## Démarrer

- [Onboarding](docs/ONBOARDING.md)
- [Workflow Git](docs/GIT_WORKFLOW.md)
- [Workflows GitHub Actions](docs/WORKFLOWS.md)

## Dashboard

Les missions et la progression sont visibles ici :

```text
https://m-boiguille.github.io/my-cloud-platform/
```
