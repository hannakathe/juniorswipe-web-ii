# Monitoring (Prometheus + Grafana)

`docker compose up` starts both:

| Service | URL | Notes |
|---------|-----|-------|
| Backend metrics | http://localhost:5000/metrics | Prometheus text format |
| Prometheus | http://localhost:9090 | Scrapes `backend:5000/metrics` every 5s (`prometheus.yml`) |
| Grafana | http://localhost:3001 | admin / admin. Datasource + "JuniorSwipe API" dashboard auto-provisioned |

## Metrics exposed by the backend (`app/metrics.py`)

| Metric | Type | Labels |
|--------|------|--------|
| `http_requests_total` | counter | method, endpoint, status |
| `http_request_duration_seconds` | histogram | method, endpoint |
| `http_request_errors_total` | counter | method, endpoint, status |

## Verify

```bash
curl -s http://localhost:9090/api/v1/targets | grep juniorswipe   # target = up
open http://localhost:3001/d/juniorswipe-api                        # dashboard
```

Generate some traffic (e.g. run the Postman collection or the frontend) and the
panels — request rate, error rate, p95 latency, total requests — will populate.
