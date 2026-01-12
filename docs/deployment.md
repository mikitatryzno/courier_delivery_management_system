(The file `c:\Users\Mikita_Tryzno\Downloads\courier_delivery_management_system\docs\deployment.md` exists, but is empty)
## Deployment

This document describes simple deployment options for the Courier Delivery Management System.

### Local development (Docker)

1. Copy environment file for development:

```bash
cp .env.docker.dev .env
```

2. Start dev services (docker-compose):

```bash
docker-compose -f docker-compose.dev.yml up --build
```

3. Backend will be available at `http://localhost:8000`, frontend at `http://localhost:3000`.

### Production

- Use Postgres (configure `DATABASE_URL`), set a secure `SECRET_KEY` in `.env`, and run migrations with Alembic.
- Build images and deploy via Kubernetes, ECS, or another container platform.

### Generating API docs

Use the helper script to fetch the live OpenAPI JSON and store YAML/JSON under `docs/api/`:

```bash
python scripts/generate-api-docs.py
```

This requires the backend running on `http://localhost:8000`.

