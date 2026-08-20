# My Cloud Platform

Portfolio DevOps / SRE en reconstruction : infrastructure as code, Kubernetes, CI/CD, GitOps, observability et AIOps.

Chaque couche est d'abord implémentée **à la main** (`raw/`), puis versionnée avec l'outillage standard (`tooled/`). Cette méthode prouve que je comprends ce que chaque abstraction automatise.

## Parcours de missions

Le moteur de missions génère le contexte et les évaluations. Les livrables sont écrits manuellement.

```
Phase 1 — Isolation Linux à la main
Phase 2 — Kubernetes 3-tiers, raw puis Helm
Phase 3 — CI/CD, raw puis Marketplace
Phase 4 — Infra Terraform + observabilité instrumentée
Phase 5 — Sécurité + GitOps
Phase 6 — AIOps & auto-remédiation
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

## Review assistée par Qodo

Le workflow `.github/workflows/qodo-pr-review.yml` est prêt mais inactif par défaut. Il permet d'obtenir un avis technique sur le code d'une PR, en complément du Lead IA pédagogique.

### Utilisation

- Manuelle : `gh workflow run qodo-pr-review.yml -f run_qodo=true -f pr_number=<N>`
- Par label : ajoute le label `qodo` à la PR

La configuration du modèle (Deepseek ou autre) sera activée en phase 2/3.
