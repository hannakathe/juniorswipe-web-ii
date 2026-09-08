# Test users (LOCAL DEVELOPMENT ONLY)

These accounts are created automatically by the seeder (`SEED_ON_STARTUP=true`,
`database/seed.sql`, and the pytest fixtures). **Do not use these credentials in
any real deployment.** Passwords are stored hashed (werkzeug `pbkdf2:sha256`);
they are never kept in plain text and never placed in the JWT payload.

| Role | Email | Password | Can do |
|------|-------|----------|--------|
| `developer` | `dev@local.test` | `Password123!` | Manage own profile, CV/resumes (upload + download), projects and tasks |
| `company` | `company@local.test` | `Password123!` | Manage own company profile, projects and tasks. **Cannot** create resumes (403) |

The demo developer is seeded with one project ("Portfolio API") and three tasks so
that list endpoints return data immediately.

## Quick login

```bash
curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"dev@local.test","password":"Password123!"}'
```

Response: `{ "token": "<JWT>", "user": { ... } }` — send it as
`Authorization: Bearer <JWT>` on every protected endpoint.

## Register a fresh user

```bash
curl -s -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"me@local.test","password":"Password123!","full_name":"Me","role":"developer"}'
```
