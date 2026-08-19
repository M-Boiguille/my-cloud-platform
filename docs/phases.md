# Phases du parcours SRE

## Phase 1 — Isolation Linux

- `container.sh run <rootfs> <command>`
- namespaces PID, mount, UTS, IPC
- `chroot`, cgroups v2
- `docs/troubleshooting.md` mis à jour

## Phase 2 — Kubernetes 3-tiers

- `kubernetes/application/manifests-raw/`
- `kubernetes/policies/`
- 10 scénarios de panne
- `helm-chart/` + `diff.sh`

## Phase 3 — CI/CD

- `cicd/github-actions/raw-steps.yml`
- `cicd/github-actions/marketplace.yml`
- `docs/raw-vs-tooled.md`

## Phase 4 — Infra + Observabilité

- `infrastructure/terraform/raw/`
- `observability/prometheus/prometheus.yml`
- `observability/app-instrumentation/`
- Dashboards Grafana RED

## Phase 5 — Sécurité + GitOps

- `security/`
- `gitops/argocd/`
- Falco, AppArmor, Seccomp, cosign

## Phase 6 — AIOps

- `chaos/fault-injection/`
- `chaos/aiops-agent/`
- Postmortems
