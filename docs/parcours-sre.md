# Parcours SRE

## Mission 1 — Infrastructure as Code

**Objectif** : Déployer l'infrastructure AWS avec Terraform.

### Livrables

- `infrastructure/terraform/` (VPC, EKS, IAM, S3)
- `docs/runbooks/terraform-apply.md`
- `LEARNED.md`

### Compétences

- Terraform
- AWS (VPC, EKS, IAM, S3)
- Cloud networking

## Mission 2 — Déploiement Kubernetes

**Objectif** : Déployer l'application `online-boutique` sur EKS.

### Livrables

- `kubernetes/base/`
- `online-boutique/` (Deployment, Service, Ingress, HPA)
- `docs/runbooks/deploy-app.md`
- `LEARNED.md`

### Compétences

- Kubernetes
- Helm
- Ingress / TLS
- HPA / Probes

## Mission 3 — CI/CD GitHub Actions

**Objectif** : Industrialiser le build, le test et le déploiement.

### Livrables

- `cicd/build.yml`
- `cicd/deploy.yml`
- `.github/workflows/deploy-staging.yml`
- `docs/runbooks/cicd.md`
- `LEARNED.md`

### Compétences

- GitHub Actions
- Docker
- ghcr.io / ECR
- Tests automatisés

## Mission 4 — GitOps Argo CD

**Objectif** : Déployer avec Argo CD et des charts Helm.

### Livrables

- `gitops/argocd-apps/`
- `gitops/charts/online-boutique/`
- `docs/runbooks/gitops.md`
- `LEARNED.md`

### Compétences

- Argo CD
- Helm
- Promotion staging → production

## Mission 5 — Observabilité

**Objectif** : Superviser l'application et le cluster.

### Livrables

- `observability/prometheus/`
- `observability/grafana/`
- `observability/loki/`
- `docs/runbooks/observability.md`
- `LEARNED.md`

### Compétences

- Prometheus / Grafana
- Loki
- Alertmanager
- SLO / SLI

## Mission 6 — Chaos Engineering

**Objectif** : Prouver la résilience de la plateforme.

### Livrables

- `chaos/experiments/`
- `docs/postmortems/`
- `LEARNED.md`

### Compétences

- Troubleshooting
- Postmortem
- Resilience
