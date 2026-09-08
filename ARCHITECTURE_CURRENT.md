# ARCHITECTURE_CURRENT.md — Diagnóstico inicial (FASE 1)

Fecha de auditoría: 2026-09-08
Rama de trabajo: `feature/local-full-stack`

## 1. Arquitectura actual

El repositorio contiene **únicamente un sitio estático de marketing + formularios de autenticación**. No hay backend, ni base de datos, ni proceso de build, ni framework de frontend.

```
juniorswipe-web-ii/
├── landing/
│   ├── index.html          # Landing page (marketing)
│   ├── styles.css
│   ├── script.js           # navbar scroll, smooth-scroll, IntersectionObserver
│   └── auth/
│       ├── login.html
│       ├── register.html
│       ├── auth.css
│       └── auth.js         # validación cliente + login/registro SIMULADO (sin backend)
├── docs/JuniorSwipe - Guia1.docx   # Guía 1 (reflexión HTML5 semántico)
├── README.md               # 1 línea de descripción
├── .vscode/settings.json   # Live Server puerto 5501
└── .gitattributes
```

## 2. Frontend

- **Framework:** ninguno. HTML5 + CSS3 + JavaScript vanilla (ES6).
- **Package manager:** ninguno (no hay `package.json`, no hay `node_modules`).
- **Build:** ninguno. Se sirve con VS Code **Live Server** en el puerto **5501**.
- **Rutas:** navegación por archivos `.html`. `index.html` → `auth/login.html` / `auth/register.html`.
- **Estado global:** ninguno. No hay almacenamiento de sesión ni token.
- **Servicios HTTP:** ninguno activo. En `landing/auth/auth.js` las llamadas `fetch('/api/auth/login')` y `fetch('/api/auth/register')` están **comentadas**; el éxito se simula con `console.log` + `setTimeout` y redirección a `dashboard.html` / `dashboard-developer.html` / `dashboard-company.html` (**archivos inexistentes**).
- **Roles en UI:** `developer` y `company` (selector `data-type` en `register.html`, `input#userType`).

## 3. Backend

- **No existe.** Ningún lenguaje, ningún framework, ningún archivo de servidor.

## 4. API

- **No existe.** No hay endpoints. Solo referencias comentadas a rutas conceptuales `/api/auth/login` y `/api/auth/register`.

## 5. Base de datos

- **No existe.** No hay SQL, ni ORM, ni migraciones, ni `localStorage` usado para datos.

## 6. Autenticación existente

- Solo **validación de formularios en cliente** (email regex, longitud de password ≥ 8, coincidencia de passwords, medidor de fortaleza).
- Botones OAuth (Google / GitHub) presentes en UI pero sin lógica (`console.log`).
- **No hay JWT, no hay sesión, no hay hashing.**

## 7. Servicios externos / URLs remotas

- **Ninguno.** Búsqueda de `fetch`, `axios`, `http://`, `https://` (APIs), `localhost`, `API_URL`, `BACKEND_URL`, `VITE_`, `REACT_APP_`, `NEXT_PUBLIC_`, WebSocket → **sin coincidencias funcionales**.
- Los únicos enlaces externos son perfiles de LinkedIn/GitHub del equipo en `index.html`.
- **Conclusión:** el proyecto NO depende hoy de ningún servidor en otro equipo dentro del código. La "dependencia de un backend en otro equipo" mencionada es conceptual: la app fue diseñada para conectarse a un backend que aún no se ha escrito.

## 8. Docker / Deployment / Tests / CI

- **Ninguno.** No hay `Dockerfile`, `docker-compose.yml`, `k8s/`, `.github/`, `terraform/`, ni tests.

## 9. Guía académica

`docs/JuniorSwipe - Guia1.docx` corresponde a la **Guía 1** (preguntas de reflexión sobre HTML5 semántico) y **no** contiene la especificación técnica de 15 resultados. La especificación autoritativa es la **guía de Ingeniería Web II** descrita en el enuncado del trabajo (registro, login, JWT, proyectos, tareas, React, Postman, tests, Docker, Kubernetes, GitHub Actions, Terraform, Prometheus/Grafana; backend REST con Blueprints y OpenAPI).

## 10. Problemas detectados

| # | Problema | Impacto |
|---|----------|---------|
| 1 | No hay backend ni API | No se puede autenticar, ni persistir, ni cumplir la guía |
| 2 | No hay base de datos | Sin persistencia |
| 3 | Login/registro simulados; redirigen a páginas inexistentes | Flujo roto tras "login" |
| 4 | No hay React | La guía exige "trabajar desde React" para el área autenticada |
| 5 | Sin Docker / CI / IaC / observabilidad | Faltan 7 de los 15 resultados |
| 6 | Sin `.env` ni centralización de URL de API | URLs se tendrían que hardcodear |
| 7 | Sin tests | Falta resultado "ejecutar pruebas automáticas" |

## 11. Qué se CONSERVA (sin tocar diseño ni lógica)

- Todo `landing/` (HTML, CSS, JS, assets, animaciones, navbar, landing page).
- Los formularios `login.html` / `register.html` y su CSS: se mantienen; solo se **descomenta y completa** la llamada `fetch` hacia la API local y el guardado del JWT (cambio mínimo, sin alterar markup ni estilos).
- Roles `developer` / `company`.
- El dominio JuniorSwipe (CV, perfil, matching, proyectos, ruta de aprendizaje, dashboards developer/company).

## 12. Qué se MODIFICA (mínimo imprescindible)

- `landing/auth/auth.js`: activar `fetch` real a `${API_URL}/api/auth/*`, guardar token en `localStorage`, redirección a la app React tras éxito. Sin cambios de UI.
- `landing/auth/*.html`: añadir `<script src="config.js">` (define `window.JUNIORSWIPE_API_URL`) — 1 línea por archivo.
- `README.md`: reescritura completa con instrucciones (lo exige la guía).
- `.gitignore`: crear (no existe) para no subir `.env`, `node_modules`, `__pycache__`, volúmenes.

## 13. Qué se AGREGA (nuevo, aditivo, sin romper lo existente)

| Área | Ubicación | Tecnología |
|------|-----------|------------|
| Backend REST | `backend/` | Flask + Blueprints, SQLAlchemy, PyJWT, prometheus-client |
| Base de datos | `backend/` (SQLAlchemy) + `database/schema.sql`, `database/seed.sql` | PostgreSQL (Docker) / SQLite (dev y tests) |
| Modelos | `backend/app/models/` | users, roles, profiles, resumes (CV), projects, tasks |
| Auth JWT | `backend/app/routes/auth.py` | register / login / me + `@jwt_required`, roles |
| Frontend app | `frontend/` | React + Vite (área autenticada: proyectos, tareas, perfil, CV) |
| Servicio HTTP centralizado | `frontend/src/api/` | `client.js` (baseURL vía `VITE_API_URL`, Bearer, manejo 401/403) |
| OpenAPI | `docs/openapi.yaml` | OpenAPI 3.0 |
| Postman | `postman/JuniorSwipe.postman_collection.json` | colección + variables `baseUrl`/`token` |
| Tests | `backend/tests/`, `frontend/src/**/*.test.jsx` | pytest, vitest |
| Docker | `backend/Dockerfile`, `frontend/Dockerfile`, `docker-compose.yml` | frontend, backend, db, prometheus, grafana |
| Kubernetes | `k8s/` | deployments, services, configmap, secret, PVC, `k8s/README.md` |
| CI | `.github/workflows/ci.yml` | lint + tests backend/frontend + build + docker build |
| Terraform | `terraform/` | provider docker (infra local reproducible), variables, outputs |
| Observabilidad | `monitoring/prometheus.yml`, `monitoring/grafana/` | scrape `/metrics`, datasource + dashboard |
| Docs credenciales | `docs/TEST_USERS.md` | usuarios de prueba dev/company |

## 14. Decisiones técnicas (y por qué)

1. **Flask** para el backend: es la referencia de la guía, es liviano, fácil de explicar académicamente, y **no hay backend previo con el que competir**.
2. **React + Vite** en `frontend/` **nuevo y separado** de `landing/`: la guía exige React; `landing/` permanece intacto. Los "dashboards" nunca existieron como archivos, así que no se reemplaza nada.
3. **SQLite en dev/tests, PostgreSQL en Docker/K8s**: permite `pytest` y desarrollo sin instalar Postgres, mientras `docker compose up` levanta PostgreSQL real. Mismo código (SQLAlchemy). Se entrega `database/schema.sql` para Postgres desde cero.
4. **`landing/auth` se conecta al backend** con el mínimo cambio (descomentar `fetch`), en lugar de reescribir esos formularios en React: respeta "cambios mínimos" y "no reemplazar el frontend".
5. **Terraform con provider `kreuzwerker/docker`**: representa infraestructura **local** reproducible sin costos cloud.

## 15. Mapa de dependencias objetivo

```
landing/ (estático, Live Server / Nginx)  ──┐
                                            ├─► backend Flask :5000  ──► PostgreSQL :5432
frontend/ React+Vite :5173  ────────────────┘         │
                                                      └─► /metrics ──► Prometheus :9090 ──► Grafana :3000
```
