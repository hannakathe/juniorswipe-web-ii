# Kubernetes manifests

Tested against a local single-node cluster (minikube / kind / Docker Desktop).

## Components

| File | Objects |
|------|---------|
| `00-namespace.yaml` | Namespace `juniorswipe` |
| `10-config.yaml` | ConfigMap (non-secret env) + Secret (keys, DB URL) |
| `20-postgres.yaml` | Headless Service + StatefulSet + `volumeClaimTemplates` (PVC 1Gi) |
| `30-backend.yaml` | Deployment (init-container waits for DB) + PVC (CV storage) + Service + probes on `/api/health` |
| `40-frontend.yaml` | Deployment (nginx, proxies `/api` to `backend`) + NodePort Service `30080` |
| `50-monitoring.yaml` | Prometheus (ConfigMap scrape + NodePort `30090`) + Grafana (datasource ConfigMap + NodePort `30030`) |

## 1. Build the images into the cluster

```bash
# minikube
eval $(minikube docker-env)
docker build -t juniorswipe-backend:local ./backend
docker build -t juniorswipe-frontend:local -f frontend/Dockerfile .

# kind
docker build -t juniorswipe-backend:local ./backend
docker build -t juniorswipe-frontend:local -f frontend/Dockerfile .
kind load docker-image juniorswipe-backend:local juniorswipe-frontend:local
```

## 2. Apply

```bash
kubectl apply -k k8s/            # or: kubectl apply -f k8s/
```

## 3. Verify

```bash
kubectl get pods -n juniorswipe
kubectl get services -n juniorswipe
kubectl get pvc -n juniorswipe
kubectl logs -n juniorswipe deploy/backend
```

Expected: `db-0`, `backend-*`, `frontend-*`, `prometheus-*`, `grafana-*` all `Running`/`Ready`.

## 4. Open

```bash
minikube service frontend  -n juniorswipe      # or http://localhost:30080
minikube service prometheus -n juniorswipe     # http://localhost:30090
minikube service grafana   -n juniorswipe      # http://localhost:30030  (admin/admin)
```

## 5. Tear down

```bash
kubectl delete -k k8s/
```

## Notes

- Secrets here are **demo values**. Use Sealed Secrets / External Secrets / SOPS for real deployments.
- `backend` runs 1 replica because the CV storage PVC is `ReadWriteOnce`. For >1
  replica, switch `STORAGE_DIR` to a `ReadWriteMany` volume (NFS, CephFS…).
- Validate without a cluster: `kubectl apply --dry-run=client -k k8s/`.
