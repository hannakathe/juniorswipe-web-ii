# Database

| Environment | Engine | How it is created |
|-------------|--------|-------------------|
| Local dev / tests | SQLite (`backend/juniorswipe_dev.db`, `:memory:`) | `db.create_all()` on startup + `seed()` |
| Docker / Kubernetes | PostgreSQL 16 | `db.create_all()` on startup, or `schema.sql` + `seed.sql` |

## Build PostgreSQL from scratch

```bash
export DATABASE_URL=postgresql://juniorswipe:juniorswipe@localhost:5432/juniorswipe
psql "$DATABASE_URL" -f database/schema.sql
psql "$DATABASE_URL" -f database/seed.sql
```

`docker compose up` runs `schema.sql` + `seed.sql` automatically (mounted into the
Postgres container's `/docker-entrypoint-initdb.d/`). The Flask app additionally
calls `db.create_all()` and (when `SEED_ON_STARTUP=true`) the Python seeder, so
the API is usable even without running the SQL files manually.

## Entities

`roles` ─< `users` ─1─ `profiles`
`users` ─< `resumes` (CV metadata; file bytes on disk in `STORAGE_DIR`)
`users` ─< `projects` ─< `tasks`

Every `projects`/`tasks`/`resumes`/`profiles` row is owned by exactly one user and
the API rejects cross-user access.
