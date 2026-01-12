# Alembic migrations

This document explains how to run Alembic migrations for the backend.

Paths
- Alembic config: `backend/alembic/alembic.ini`
- Migration scripts: `backend/alembic/versions/`

Default behavior
- The project uses a dynamic DB URL set from `src.core.config.settings`.
- By default the `environment` is `development` and the code uses SQLite at `sqlite:///./courier_delivery.db` (relative to the `backend/` directory).

Run migrations locally (recommended for development)

1. From the repository root, build and run the backend test image (or use your local Python environment where dependencies are installed).

Using Podman/Docker (recommended to match CI):

```bash
podman build -f backend/Dockerfile.dev -t courier-backend-test backend
podman run --rm -e PYTHONPATH=/app/backend/src -v $(pwd):/app:Z courier-backend-test sh -c "cd /app/backend && alembic -c alembic/alembic.ini upgrade head"
```

2. Using a local virtualenv (if you have Python deps installed):

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # (or .venv\Scripts\activate on Windows)
pip install -r requirements.txt
alembic -c alembic/alembic.ini upgrade head
```

Specifying a production/Postgres DB
- To target Postgres, set `ENVIRONMENT=production` and the `POSTGRES_*` env vars so `src.core.config.Settings` builds the proper URL. Example (bash):

```bash
export ENVIRONMENT=production
export POSTGRES_SERVER=your-db-host
export POSTGRES_USER=your-user
export POSTGRES_PASSWORD=your-pass
export POSTGRES_DB=your-db
alembic -c alembic/alembic.ini upgrade head
```

CI
- In CI, run the same `alembic` command after ensuring the database is available and the environment variables point to the test DB.

Rollback
- To revert the last migration: `alembic -c alembic/alembic.ini downgrade -1`

Notes
- The `env.py` bundled with Alembic reads `src.core.config.settings` for the DB URL, so ensure the working directory and `PYTHONPATH` include the `backend/src` package when running Alembic (the Docker commands above set `PYTHONPATH`).

# Recent changes (2026-01-12)

- Added `Delivery` and `Notification` models and corresponding API routes and services under `backend/src/models`, `backend/src/services`, and `backend/src/api/routes`.
- Added Alembic migration `002_add_deliveries_notifications.py` and a helper `backend/alembic/README.md` with migration instructions.
- Added unit tests for `DeliveryService` and `NotificationService` under `backend/src/tests/`.
- Applied migrations and verified backend tests in the test container: `19 passed` (with warnings).

If you'd like me to continue working through the remaining TODOs, I can start by adding RBAC schema changes and a migration to update the `users` table, or implement integration tests for the new endpoints—tell me which to prioritize.
