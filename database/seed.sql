-- JuniorSwipe — seed data (idempotent).  Run AFTER schema.sql:
--   psql "$DATABASE_URL" -f database/seed.sql
--
-- Demo credentials (LOCAL DEVELOPMENT ONLY):
--   developer -> dev@local.test      / Password123!
--   company   -> company@local.test  / Password123!
-- The hash below is werkzeug pbkdf2:sha256 of "Password123!".
-- The Flask app also seeds this automatically when SEED_ON_STARTUP=true.

INSERT INTO roles (name, description) VALUES
    ('developer', 'Junior developer looking for opportunities'),
    ('company',   'Company hiring junior developers')
ON CONFLICT (name) DO NOTHING;

INSERT INTO users (email, password_hash, full_name, role_id)
SELECT 'dev@local.test',
       'pbkdf2:sha256:1000000$mdqosraMtdVinmk6$cab61b90e278429f27a16c106e4f0408332a6d296d819e945467207214569cf3',
       'Dana Developer', r.id
FROM roles r WHERE r.name = 'developer'
ON CONFLICT (email) DO NOTHING;

INSERT INTO users (email, password_hash, full_name, role_id)
SELECT 'company@local.test',
       'pbkdf2:sha256:1000000$mdqosraMtdVinmk6$cab61b90e278429f27a16c106e4f0408332a6d296d819e945467207214569cf3',
       'Acme Corp', r.id
FROM roles r WHERE r.name = 'company'
ON CONFLICT (email) DO NOTHING;

INSERT INTO profiles (user_id, headline, company_name)
SELECT u.id,
       CASE u.email WHEN 'dev@local.test' THEN 'Full-stack in training'
                    ELSE 'We hire junior talent' END,
       CASE u.email WHEN 'company@local.test' THEN 'Acme Corp' ELSE NULL END
FROM users u
WHERE u.email IN ('dev@local.test', 'company@local.test')
  AND NOT EXISTS (SELECT 1 FROM profiles p WHERE p.user_id = u.id);

INSERT INTO projects (owner_id, title, description, status, tech_stack)
SELECT u.id, 'Portfolio API', 'REST API showcase for JuniorSwipe', 'active',
       'Flask, PostgreSQL'
FROM users u
WHERE u.email = 'dev@local.test'
  AND NOT EXISTS (SELECT 1 FROM projects p WHERE p.owner_id = u.id);

INSERT INTO tasks (project_id, title, status)
SELECT p.id, t.title, t.status
FROM projects p
JOIN users u ON u.id = p.owner_id AND u.email = 'dev@local.test'
CROSS JOIN (VALUES ('Design schema', 'done'),
                   ('Implement auth', 'in_progress'),
                   ('Write tests', 'todo')) AS t(title, status)
WHERE p.title = 'Portfolio API'
  AND NOT EXISTS (SELECT 1 FROM tasks x WHERE x.project_id = p.id);
