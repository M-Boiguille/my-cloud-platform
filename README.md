# My Cloud Platform

Portfolio DevOps / SRE en reconstruction vers un profil **polyvalent et employable** : Linux, Docker, AWS, Terraform, CI/CD, Kubernetes, SRE et DevSecOps.

Chaque couche est d'abord implémentée **à la main** (`raw/`), puis versionnée avec l'outillage standard (`tooled/`). Cette méthode prouve que je comprends ce que chaque abstraction automatise.

## Parcours de missions

Le moteur de missions génère le contexte et les évaluations. Les livrables sont écrits manuellement.

```
Phase 1 — Linux et scripting Bash/Python
Phase 2 — Docker : images, conteneurs, réseaux
Phase 3 — AWS + Terraform : infrastructure as code
Phase 4 — CI/CD avec GitHub Actions
Phase 5 — Kubernetes : k3s/EKS, manifests
Phase 6 — SRE / Observabilité : Prometheus, Grafana
Phase 7 — DevSecOps : sécurité, GitOps, cosign
Phase 8 — Platform Engineering
```

## Structure

| Dossier | Rôle |
|---------|------|
| `infrastructure/terraform/raw/` | Ressources Terraform brutes (manuel) |
| `infrastructure/terraform/modules/` | Modules Terraform communautaires (toole) |
| `kubernetes/application/manifests-raw/` | Manifestes K8s bruts (manuel) |
| `kubernetes/application/helm-chart/` | Chart Helm (toole) |
| `kubernetes/policies/` | NetworkPolicy, PSS, Kyverno |
| `cicd/github-actions/` | Pipelines raw et Marketplace |
| `gitops/argocd/` | Applications Argo CD |
| `observability/` | Prometheus, Grafana, Loki, instrumentation |
| `chaos/` | Fault injection, aiops-agent |
| `security/` | AppArmor, Seccomp, cosign, Falco |
| `networking/docs/` | Schémas et cas de panne |
| `docs/` | Architecture, runbooks, postmortems |

## Moteur de missions

Le moteur est dans `core/`. Il génère le contexte de mission, ouvre une issue, relit la PR et évalue la progression.

Lancer une nouvelle mission : `gh workflow run generate-mission`.

## Review assistée par CodeRabbit

[![CodeRabbit](https://img.shields.io/badge/CodeRabbit-PR%20Review-FF6F61?logo=github)](https://github.com/M-Boiguille/my-cloud-platform/pulls)

CodeRabbit est intégré en tant qu'application GitHub pour relire les PRs en complément du Lead IA pédagogique.

### Pourquoi CodeRabbit

- Review technique de code sans configuration YAML dans le repo
- Chat interactif sur chaque PR
- Gratuit pour les dépôts publics
- Reconnu en entreprise

### Utilisation

CodeRabbit déclenche automatiquement une review à l'ouverture et à chaque mise à jour de PR.
