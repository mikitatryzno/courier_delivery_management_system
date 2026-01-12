# Courier Delivery Management System

A web platform for local courier operations: package creation, assignment, real-time tracking, and delivery confirmation.

## Table of contents
- [Overview](#overview)
- [Features](#features)
- [Tech stack](#tech-stack)
- [Quickstart (single environment)](#quickstart-single-environment)
- [Running & testing](#running--testing)

## Overview
This repository contains a FastAPI backend and a React frontend. The backend exposes REST endpoints and WebSocket endpoints for live delivery tracking. The frontend is built with Vite and served via nginx in production images.

## Features
- User roles: Administrator, Courier, Sender, Recipient (RBAC scaffolded)
- Package creation and management
- Delivery assignment and status updates
- Real-time delivery location streaming via WebSocket
- Database migrations (Alembic) and seed tools

## Tech stack
- Backend: FastAPI, SQLAlchemy, Alembic, Pydantic
- Frontend: React, TypeScript, Vite
- Tests: pytest (backend), Vitest (frontend)
- Deployment: Docker / docker-compose or Podman + podman-compose

## Quickstart (single environment)
Prerequisites: Docker or Podman, and `docker-compose` or `podman-compose` on PATH.

From the repository root run:

```powershell
# Build and start services (production-like)
podman-compose up -d --build
# or with Docker
docker-compose up -d --build
```

Verify services:

```powershell
curl http://localhost:8000/api/health
curl http://localhost:8000/api/docs
curl http://localhost:3000/
```

If ports or tooling differ in your environment, adapt the commands above accordingly.

## Running & testing
- Seed or initialize the database (inside backend container or via CLI):

```powershell
python -m src.utils.db_cli init
python -m src.utils.db_cli seed
```

- Run backend tests inside a container (recommended):

```powershell
podman build -t courier-backend-test -f backend/Dockerfile backend
podman run --rm -v %CD%:/app:Z courier-backend-test sh -c "pytest -q"
```


