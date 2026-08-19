# Architecture

## Vue d'ensemble

```text
                    Internet
                       │
                       ▼
                  Route 53
                       │
                       ▼
                Application Load Balancer
                       │
                       ▼
                  Ingress Controller
                       │
                       ▼
                 Online Boutique (k8s)
                       │
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
      Metrics        Logs          Traces
         │             │             │
         ▼             ▼             ▼
     Prometheus       Loki         Tempo
         │             │             │
         └─────────────┼─────────────┘
                       ▼
                    Grafana
                       │
              ┌────────┴────────┐
              ▼                 ▼
           Alerts              SLOs
              │
              ▼
          Alertmanager
              │
              ▼
           Webhook / Email
```

## Infrastructure

- **Cloud** : AWS Free Tier (compte dédié)
- **Compute** : EKS ou k3s sur EC2 t2.micro/t3.medium
- **Storage** : S3 pour les artefacts, EBS pour les PVC
- **Networking** : VPC, subnets publics/privés, NAT, ALB

## CI/CD

```text
Push / PR
    │
    ▼
GitHub Actions
    │
    ├── lint
    ├── test
    ├── trivy scan
    ├── build image
    └── push to ECR
            │
            ▼
    Update image tag
            │
            ▼
        Argo CD
            │
            ▼
        Kubernetes
```

## Environnements

- `dev` : local (k3d)
- `staging` : EKS minimal
- `production` : EKS avec HA (objectif)

## Sécurité

- Secrets : SOPS + AWS KMS ou Sealed Secrets
- Images : scan Trivy à chaque build
- Policies : Kyverno pour interdire les images non scannées
- Network : NetworkPolicies par namespace
