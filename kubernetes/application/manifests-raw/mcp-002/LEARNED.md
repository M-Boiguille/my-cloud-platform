# Ce que j'ai appris — Mission mcp-002

## Objectif

Déployer une application web statique sur Kubernetes en manipulant les trois objets fondamentaux : Pod, ReplicaSet et Deployment. Comprendre comment Kubernetes gère le nombre de réplicas, sélectionne les Pods, et termine proprement les conteneurs.

## Stratégies de gestion du nombre de Pods

### Pod isolé

Un `Pod` est l'unité minimale. S'il est supprimé, il n'est pas recréé. Il sert à tester et observer un conteneur en isolation.

### ReplicaSet

Un `ReplicaSet` assure qu'un nombre défini de réplicas est toujours en cours d'exécution. Si un Pod disparaît, le ReplicaSet en recrée un autre.

```yaml
spec:
  replicas: 3
  selector:
    matchLabels:
      type: web-app
```

### Deployment

Un `Deployment` gère un ou plusieurs ReplicaSets. Il permet les mises à jour progressives (*RollingUpdate*) et les rollbacks. Quand l'image change, un nouveau ReplicaSet est créé et l'ancien est progressivement remplacé.

## Selectors et matchLabels

Les `matchLabels` permettent au ReplicaSet et au Deployment de savoir quels Pods ils contrôlent. Le selector du ReplicaSet et les labels du Pod doivent correspondre.

```yaml
# Pod
metadata:
  labels:
    type: web-app

# ReplicaSet
spec:
  selector:
    matchLabels:
      type: web-app
```

Si les labels du Pod ne correspondent pas au selector du ReplicaSet, le ReplicaSet considère que le Pod ne lui appartient pas et en crée d'autres, ce qui peut donner plus de Pods que prévu.

## Arrêt propre des Pods

Quand Kubernetes supprime un Pod, il envoie un signal `SIGTERM` au conteneur. L'application dispose alors d'un délai pour s'arrêter proprement.

Par défaut, ce délai est de **30 secondes**. Il est configurable avec `terminationGracePeriodSeconds`.

```yaml
spec:
  terminationGracePeriodSeconds: 30
```

Si l'application n'a pas terminé au bout de ce délai, Kubernetes envoie un `SIGKILL` pour la forcer à s'arrêter.

### Pourquoi c'est important

Lors d'un `RollingUpdate`, les anciens Pods reçoivent `SIGTERM`. Si l'application ne le gère pas et se termine avec un code d'erreur, Kubernetes affiche un statut `Error`. Cela ne signifie pas que l'application est en panne, juste qu'elle ne s'est pas arrêtée proprement.

## Commandes vérifiées

| Commande | Usage |
|----------|-------|
| `kubectl apply -f pod.yaml` | Créer le Pod |
| `kubectl apply -f replicaset.yaml` | Créer le ReplicaSet |
| `kubectl apply -f deployment.yaml` | Créer le Deployment |
| `kubectl get pods,rs,deployments` | Voir l'état global |
| `kubectl describe pod <nom>` | Détails d'un Pod |
| `kubectl port-forward pod/<nom> 8080:80` | Accès local à l'application |
| `kubectl rollout restart deployment/<nom>` | Déclencher un RollingUpdate |
| `kubectl rollout undo deployment/<nom>` | Revenir à la version précédente |
| `kubectl delete -f <fichier.yaml>` | Supprimer la ressource |

## Liens de documentation

- [Pods](https://kubernetes.io/docs/concepts/workloads/pods/)
- [ReplicaSets](https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/)
- [Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Labels and Selectors](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/)
- [Pod Lifecycle — Termination](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-termination)
