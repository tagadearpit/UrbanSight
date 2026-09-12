-- Canonical database entry point for local Compose users.
-- Apply the migration and seed in order:
--   psql "$DATABASE_URL" -f database/migrations/001_initial.sql
--   psql "$DATABASE_URL" -f database/seed/demo.sql
\ir database/migrations/001_initial.sql
\ir database/seed/demo.sql
