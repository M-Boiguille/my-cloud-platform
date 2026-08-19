# My Cloud Platform

Plateforme Cloud-native de démonstration pour le profil SRE / DevOps confirmé.

## Objectif

Montrer la maîtrise complète du cycle de vie d'une application sur Kubernetes :

```
Infrastructure (Terraform / AWS free tier)
    ↓
Kubernetes (k3s / EKS)
    ↓
Application (online-boutique)
    ↓
CI/CD (GitHub Actions)
    ↓
GitOps (Argo CD)
    ↓
Observability (Prometheus / Grafana / Loki)
    ↓
Chaos / Resilience
```

## Structure

| Dossier | Contenu |
|---------|---------|
| `infrastructure/terraform/` | VPC, EKS, IAM, S3, Route53 |
| `kubernetes/base/` | Namespaces, NetworkPolicies, RBAC |
| `kubernetes/environments/` | Staging, production overlays |
| `kubernetes/policies/` | Kyverno / OPA Gatekeeper |
| `application/` | Code source de l'application simplifiée |
| `online-boutique/` | Déploiement de l'application |
| `cicd/` | GitHub Actions, workflows réutilisables |
| `gitops/` | Charts Helm, Argo CD applications |
| `observability/` | Prometheus, Grafana, Loki, Alertmanager |
| `chaos/` | Scénarios de panne et postmortems |
| `docs/runbooks/` | Procédures d'intervention |

## Parcours métier

Voir [docs/parcours-sre.md](docs/parcours-sre.md).

## Compétences démontrées

- Linux / Bash / Python
- Git / GitHub Actions
- Docker / BuildKit / Trivy
- Kubernetes / Helm / Argo CD
- Terraform / AWS
- Networking / DNS / TLS
- Observability / Alerting
- Troubleshooting / Postmortem
- Security / Secrets management
