## Architecture Overview

This project follows a simple separation of concerns:

- **backend/** — FastAPI application, SQLAlchemy models, Alembic migrations, and API routes. The backend exposes a REST API and WebSocket endpoints for realtime updates.
- **frontend/** — React + TypeScript single page application built with Vite. Uses `@` alias for `src` imports and Vitest for tests.
- **docs/** — Generated API docs and human-facing architecture/deployment guides.
- **scripts/** — Helper scripts for generating docs, validating the API, and managing container-based development.

Deployment and local dev use Docker and docker-compose. The backend uses SQLite for development (configurable for Postgres in production via environment variables).

Key components

- **Authentication:** JWT-based access tokens; refresh tokens supported.
- **Authorization:** Role-based checks in route handlers (admin/courier/sender/recipient).
- **Persistence:** SQLAlchemy models with alembic migrations under `backend/alembic/`.
- **Realtime:** WebSocket endpoints under `src/api/routes/websocket.py` and connection manager in `src/websocket/`.

Scalability note: For production, use a managed Postgres instance, background workers for heavy work, and an object store / CDN for media assets.
