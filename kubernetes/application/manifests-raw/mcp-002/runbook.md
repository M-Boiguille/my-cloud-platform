# Runbook

## Contexte

Déploiement et gestion du cycle de vie d'une application web statique (image `my-web-app:1.0`) sur un cluster Kubernetes K3s local. L'architecture s'appuie sur une chaîne d'objets Pod, ReplicaSet et Deployment.

## Symptômes

Lors d'une mise à jour de version (*RollingUpdate*) déclenchée par `kubectl apply -f deployment.yaml` ou `kubectl rollout restart`:
1. La commande `kubectl get pods --watch` affiche brièvement un statut `Error` sur les anciens pods en cours de fermeture.
2. Tenter d'inspecter l'ancien pod immédiatement après avec `kubectl describe pod` ou `kubectl logs` retourne une erreur du serveur :
   `Error from server (NotFound): pods "..." not found`.

## Diagnostic

1. **Causes du statut `Error` :** Lorsque Kubernetes ferme un pod (phase `Terminating`), il lui envoie un signal `SIGTERM`. L'application `my-web-app:1.0` intercepte ce signal et s'arrête en renvoyant un code de sortie d'erreur (`Exit Code 1` au lieu de `0`).
2. **Disparition rapide du Pod :** Le Deployment a déjà instancié avec succès les nouveaux pods (`1/1 Running`). Le Garbage Collector de Kubernetes supprime immédiatement les anciens pods terminés dès que la rotation est validée, rendant les pods `NotFound`.
3. **Impact applicatif :** Réellement nul. L'application est restée 100% disponible sur `http://localhost:8080` sans aucune interruption de service.

## Commandes clés

| Commande | Usage |
|----------|-------|
| `kubectl apply -f <fichier.yaml>` | Appliquer les manifests (`pod.yaml`, `replicaset.yaml`, `deployment.yaml`) |
| `kubectl get pods,rs,deployments` | Vérifier l'état global des ressources du cluster |
| `kubectl describe pod <nom-du-pod>` | Inspecter les événements et le code de sortie (`Last State`) d'un pod |
| `kubectl logs <nom-du-pod> --previous` | Consulter les logs d'un conteneur qui vient de s'arrêter |
| `kubectl get events --watch` | Analyser les événements du cluster en direct pendant un rollout |
| `kubectl port-forward pod/my-web-pod 8080:80` | Rendre l'application accessible sur `http://localhost:8080` |
| `kubectl delete -f <fichier.yaml>` | Nettoyer ou supprimer les ressources Kubernetes |

## Mitigation

- **En développement / test :** Aucune action requise. Le comportement est inoffensif.
- **En production (bonnes pratiques applicatives) :** Capturer le signal `SIGTERM` dans le code de l'application pour intercepter l'arrêt et s'éteindre proprement avec un code de sortie `0`.

## Rollback

En cas de problème sur un nouveau déploiement :

```bash
# Revenir à la version précédente du Deployment
kubectl rollout undo deployment/my-web-deploy

# Vérifier l'historique des déploiements
kubectl rollout history deployment/my-web-deploy
```

## Validation

Un script d'audit local a été exécuté avec succès sur le cluster K3s. Les étapes couvertes :

1. `kubectl apply` des manifests.
2. Vérification de l'état des Pods, ReplicaSet et Deployment.
3. Test d'accès HTTP via `kubectl port-forward` : **code 200**.
4. `kubectl rollout restart` : le Deployment recrée les Pods sans interruption de service.
5. Nettoyage complet avec `kubectl delete -f`.

Le script et le rapport d'exécution sont conservés localement dans `SUPPORT/audit/mcp-002/`.
