# JuniorSwipe

Plataforma de vinculación técnica que elimina la fricción en la contratación de
desarrolladores junior: sustituye el CV genérico por evidencias técnicas
verificables (proyectos y tareas), optimiza el filtrado para empresas y da a los
candidatos una hoja de ruta de empleabilidad.

Este repositorio es **autosuficiente en local**: frontend + backend + base de
datos SQL + autenticación JWT, con Docker, Kubernetes, CI, Terraform y
observabilidad Prometheus/Grafana.

---

## Arquitectura

```
landing/            Sitio estático (marketing + formularios de auth)  ─┐
frontend/           React + Vite  (área autenticada: proyectos, tareas, perfil, CV)
                          │  Authorization: Bearer <JWT>
                          ▼
backend/            Flask REST API (Blueprints)  ──►  PostgreSQL (SQLite en dev/tests)
                          │
                          └─► /metrics ──► Prometheus ──► Grafana
```

| Componente | Tecnología | Puerto (local) | Puerto (Docker) |
|-----------|------------|----------------|-----------------|
| Landing | HTML/CSS/JS + Live Server | 5501 | via `/landing/` en frontend |
| Frontend | React 18 + Vite 6 | 5173 | 8080 (nginx) |
| Backend | Flask 3 + SQLAlchemy + PyJWT | 5000 | 5000 |
| Base de datos | PostgreSQL 16 / SQLite | 5432 | 5432 |
| Prometheus | prom/prometheus | — | 9090 |
| Grafana | grafana/grafana | — | 3001 (admin/admin) |

Diagnóstico del estado previo del proyecto: [`ARCHITECTURE_CURRENT.md`](ARCHITECTURE_CURRENT.md).

---

## Requisitos

- **Con Docker:** Docker + Docker Compose v2. Nada más.
- **Sin Docker:** Python 3.12+ y Node.js 20+. PostgreSQL es opcional (por
  defecto el backend usa SQLite).

---

## Ejecutar TODO con Docker (recomendado)

```bash
git clone https://github.com/hannakathe/juniorswipe-web-ii
cd juniorswipe-web-ii
docker compose up --build
```

| Servicio | URL |
|----------|-----|
| App web (React) | http://localhost:8080 |
| Landing estática | http://localhost:8080/landing/index.html |
| API | http://localhost:5000 |
| API health | http://localhost:5000/api/health |
| Métricas | http://localhost:5000/metrics |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3001 (admin / admin) |

Parar: `docker compose down`  ·  Borrar datos: `docker compose down -v`.

---

## Ejecutar sin Docker

### Base de datos

No hace falta nada: el backend crea `backend/juniorswipe_dev.db` (SQLite) y lo
siembra al arrancar. Para usar PostgreSQL, exporta `DATABASE_URL` y opcionalmente
carga `database/schema.sql` + `database/seed.sql` (ver [`database/README.md`](database/README.md)).

### Backend

```bash
cd backend
python -m venv .venv
# Windows:  .venv\Scripts\activate      Linux/macOS:  source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
python run.py                 # http://localhost:5000
```

### Frontend (React)

```bash
cd frontend
npm install
cp .env.example .env          # VITE_API_URL=http://localhost:5000
npm run dev                    # http://localhost:5173
```

### Landing estática

```bash
cd landing
python -m http.server 5501    # o la extensión Live Server (puerto 5501)
```
Los formularios de `landing/auth/` llaman a la API real y, tras el login,
redirigen a la app React pasando el JWT por fragmento de URL.

---

## Variables de entorno

### backend (`backend/.env`)

| Variable | Def. | Descripción |
|----------|------|-------------|
| `SECRET_KEY` / `JWT_SECRET` | `dev-secret…` | Claves de firma |
| `JWT_EXPIRES_SECONDS` | `3600` | Expiración del token |
| `DATABASE_URL` | *(vacío → SQLite)* | DSN PostgreSQL |
| `CORS_ORIGINS` | `localhost:5173,5501` | Orígenes permitidos (lista) |
| `SEED_ON_STARTUP` | `true` | Crea roles + usuarios demo |
| `STORAGE_DIR` | `./storage` | Carpeta de archivos de CV |

### frontend (`frontend/.env`)

| Variable | Def. | Descripción |
|----------|------|-------------|
| `VITE_API_URL` | `http://localhost:5000` | Base de la API. Vacío = mismo origen (Docker/nginx) |

Nunca se suben `.env` reales (ver `.gitignore`). Plantillas: `*.env.example`.

---

## Usuarios de prueba (solo desarrollo local)

| Rol | Email | Password |
|-----|-------|----------|
| `developer` | `dev@local.test` | `Password123!` |
| `company` | `company@local.test` | `Password123!` |

Contraseñas hasheadas (werkzeug `pbkdf2:sha256`), nunca en texto plano ni en el
JWT. Detalle: [`docs/TEST_USERS.md`](docs/TEST_USERS.md).

---

## Autenticación y autorización

- `POST /api/auth/register` → crea usuario + devuelve JWT.
- `POST /api/auth/login` → devuelve `{ token, user }`.
- `GET /api/auth/me` → usuario actual (requiere `Authorization: Bearer <JWT>`).
- JWT HS256, payload: `sub`, `email`, `role`, `iat`, `exp` (sin datos sensibles).
- Errores controlados: token ausente (`401 token_missing`), inválido
  (`401 token_invalid`), expirado (`401 token_expired`), usuario inexistente
  (`401 user_not_found`), rol insuficiente (`403 forbidden`).
- **Roles:** `developer` (perfil, CV, proyectos, tareas) y `company` (perfil de
  empresa, proyectos, tareas; **no** puede crear CV → 403).
- **Aislamiento:** un usuario no puede leer/editar proyectos, tareas, CV o perfil
  de otro cambiando el ID (responde `404`).

---

## API REST

Recursos: `auth`, `users`, `profiles`, `resumes` (CV), `projects`, `tasks`.
Organización por Blueprints en `backend/app/routes/`. Respuestas JSON
consistentes; listados paginados (`page`, `per_page`, `total`); errores con
forma `{ "error": { "code", "message", "details" } }`.

Endpoints principales:

```
POST   /api/auth/register           GET  /api/projects            (paginado, ?status=)
POST   /api/auth/login              POST /api/projects
GET    /api/auth/me                 GET  /api/projects/:id        (incluye tareas)
GET    /api/users/me                PATCH/DELETE /api/projects/:id
GET    /api/profiles/me             GET  /api/tasks               (?project_id=&status=)
PUT    /api/profiles/me             POST /api/tasks
GET    /api/resumes                 GET  /api/projects/:id/tasks
POST   /api/resumes  (dev, multipart)  POST /api/projects/:id/tasks
GET    /api/resumes/:id/file        PATCH/DELETE /api/tasks/:id
GET    /api/health   ·  GET /metrics
```

### OpenAPI

Especificación completa: [`docs/openapi.yaml`](docs/openapi.yaml) (OpenAPI 3.0,
15 paths, JWT bearer, request/response bodies y códigos HTTP). Visualízala en
https://editor.swagger.io o con `npx @redocly/cli preview-docs docs/openapi.yaml`.

### Postman

[`postman/JuniorSwipe.postman_collection.json`](postman/) + entorno.
`Login` guarda `{{token}}` automáticamente. Ejecución headless:

```bash
newman run postman/JuniorSwipe.postman_collection.json --env-var baseUrl=http://localhost:5000
```
(17 requests, 30 asserts). Guía: [`postman/README.md`](postman/README.md).

---

## Pruebas automáticas

```bash
# Backend  (pytest — 30 tests: auth, roles, JWT, projects, tasks, profile/CV, metrics)
cd backend && pytest

# Frontend (vitest — cliente API, manejo 401, login)
cd frontend && npm test

# Integración API (Postman/newman contra la API en marcha)
newman run postman/JuniorSwipe.postman_collection.json --env-var baseUrl=http://localhost:5000
```

CI ejecuta las tres + build + build de imágenes Docker.

---

## Docker

`docker-compose.yml` levanta `db`, `backend`, `frontend`, `prometheus`,
`grafana` con healthchecks, `depends_on: service_healthy`, red dedicada y
volúmenes persistentes (`pgdata`, `storage`, `grafana`). El backend **no**
depende de ningún servicio externo.

```bash
docker compose up --build      # arranca todo
docker compose ps              # estado + health
docker compose logs -f backend
```

---

## Kubernetes

Manifiestos en [`k8s/`](k8s/): namespace, ConfigMap + Secret, StatefulSet de
PostgreSQL con `volumeClaimTemplates`, Deployments de backend/frontend con
probes, Services (NodePort), Prometheus + Grafana.

```bash
# construir imágenes en el clúster (minikube/kind) — ver k8s/README.md
kubectl apply -k k8s/
kubectl get pods -n juniorswipe
kubectl get services -n juniorswipe
```

Validación sin clúster: `kubectl apply --dry-run=client -k k8s/`.

---

## GitHub Actions

[`.github/workflows/ci.yml`](.github/workflows/ci.yml) — en cada push/PR:

1. **backend**: `flake8` + `pytest` (con cobertura).
2. **frontend**: `eslint` + `vitest` + `vite build`.
3. **integration**: servicio PostgreSQL + API con gunicorn + colección Postman (newman).
4. **docker**: build de las dos imágenes + `docker compose config`.

---

## Terraform

[`terraform/`](terraform/) usa el provider `kreuzwerker/docker` para levantar la
misma pila localmente (network, volumen, imágenes, contenedores). Sin recursos
cloud ni costos.

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
terraform init && terraform plan && terraform apply
terraform output          # frontend_url, backend_url, metrics_url, ...
terraform destroy
```

---

## Prometheus / Grafana

- Backend expone `/metrics`: `http_requests_total`,
  `http_request_duration_seconds` (histograma), `http_request_errors_total`.
- Prometheus hace scrape de `backend:5000` cada 5 s (`monitoring/prometheus.yml`).
- Grafana provisiona automáticamente el datasource y el dashboard
  **"JuniorSwipe API"** (request rate, error rate, latencia p95, total de
  requests). Detalle: [`monitoring/README.md`](monitoring/README.md).

Genera tráfico (frontend o newman) y observa los paneles en
http://localhost:3001.

---

## Solución de problemas

| Síntoma | Causa / arreglo |
|---------|-----------------|
| Frontend: "No se pudo conectar con la API" | Backend no está arriba o `VITE_API_URL` mal. Prueba `curl localhost:5000/api/health`. |
| Error CORS en el navegador | Añade el origen a `CORS_ORIGINS` del backend y reinícialo. |
| `401` inmediato tras login | Token expirado (`JWT_EXPIRES_SECONDS`) o `JWT_SECRET` distinto entre procesos. |
| `pytest` lento la 1ª vez | Hashing pbkdf2 del seed; es normal (~1 min). |
| `psycopg` no instala en local | Usa SQLite (deja `DATABASE_URL` vacío); `psycopg` solo se usa en Docker/K8s. |
| Docker: `frontend` no compila | El build usa contexto raíz: `docker compose build frontend`. |
| K8s: pods `ImagePullBackOff` | Falta cargar las imágenes locales (`minikube docker-env` / `kind load`). |
| Puerto ocupado (5000/5173/8080) | Cambia el mapeo en `docker-compose.yml` o las variables `*_port` de Terraform. |

---

## Estructura del repositorio

```
landing/            Sitio estático original (conservado)
frontend/           App React + Vite (nueva)
backend/            API Flask (nueva)
  app/{models,routes,...}  · tests/  · Dockerfile
database/           schema.sql · seed.sql
docs/               openapi.yaml · TEST_USERS.md · Guia1.docx
postman/            colección + entorno
monitoring/         prometheus.yml · grafana/
k8s/                manifiestos + README
terraform/          IaC local (docker provider)
.github/workflows/  ci.yml
docker-compose.yml
ARCHITECTURE_CURRENT.md
```
