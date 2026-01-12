# AI-Assisted Development Workflow

This document describes the AI tools and workflows used while developing the Courier Delivery Management System.

## Primary assistants

- **Claude 3.5 Sonnet (Anthropic)** — architecture design, API specification, and higher-level guidance.
- **GitHub Copilot** — inline code completion and boilerplate generation in the editor.
- **Cursor AI** — context-aware refactoring and large-scale edits.
- **ChatGPT / Assistant** — documentation writing and task orchestration.

## Development phases

1. **Architecture & planning** — generate project structure and OpenAPI first.
2. **API-first implementation** — scaffold backend from OpenAPI, add Pydantic models.
3. **Backend development** — incremental FastAPI endpoints, services, and tests.
4. **Frontend development** — React + TypeScript components consuming the API client.
5. **Testing & CI** — pytest for backend, Vitest for frontend, automated via CI.

## MCP Server tools (dev-only helpers)

- `seed_database` — populate development DB with fixtures.
- `reset_database` — wipe and reinitialize DB state.
- `generate_model` / `generate_crud` — code generation helpers for models and CRUD.
- `validate_api` — run basic API validation and health checks (see `scripts/validate-api.py`).

## Prompting patterns & best practices

- Start with clear context + example inputs and outputs.
- Narrow focus for incremental changes; use tests to validate AI edits.
- Keep prompts reproducible and store reused prompt templates.

## Notes

- Always review AI-generated code and tests. Do not merge unreviewed security-sensitive code.
- Record decisions in `docs/` and keep OpenAPI specs up-to-date.
AI-Assisted Development Workflow
This document outlines the AI tools, strategies, and workflows used to develop the Courier Delivery Management System. The development follows an AI-first approach, leveraging various AI assistants and automation tools to accelerate development while maintaining code quality.

AI Tools and Assistants Used
Primary Development Assistant
Tool: Claude 3.5 Sonnet (Anthropic)
Usage: Primary coding assistant for architecture design, code generation, and problem-solving
Strengths: Complex reasoning, code structure design, API specification creation
Integration: Direct conversation-based development with copy-paste workflow
Code Generation and IDE Integration
Tool: GitHub Copilot
Usage: Real-time code completion and suggestion during development
Integration: VS Code extension for inline code generation
Focus Areas: Boilerplate code, test generation, common patterns
Specialized AI Tools
Tool: Cursor AI
Usage: Context-aware code editing and refactoring
Integration: AI-powered IDE for complex code modifications
Use Cases: Large-scale refactoring, cross-file code generation
Documentation and API Design
Tool: ChatGPT-4
Usage: Documentation generation, API specification refinement
Integration: Web interface for documentation tasks
Focus Areas: README files, API documentation, user guides
Development Phases and AI Integration
Phase 1: Architecture and Planning
AI Assistant: Claude 3.5 Sonnet Approach: Conversational architecture design Prompting Strategy:


# AI-Assisted Development Workflow

This repository was developed with AI-assisted tools and follows an iterative, test-driven approach. The notes below capture the core assistants used, development phases, and recent project state relevant to contributors.

## Primary assistants
- GitHub Copilot — inline code completion and boilerplate generation.
- Claude / other LLMs — architecture design and API specification guidance.
- ChatGPT / Assistant — documentation, task orchestration, and CI/docs updates.

## Development highlights
- Backend: FastAPI + SQLAlchemy, Alembic migrations, Pydantic models.
- Frontend: React + TypeScript, Vite (dev) and an nginx-based production build.
- Realtime: WebSocket endpoints for live delivery location streaming and a connection manager.
- Tests: Backend unit + integration tests run in a containerized environment (pytest). WebSocket integration tests added and passing.

## Recent repository changes
- Removed dev-only artifacts (`*.Dockerfile.dev`, `docker-compose.dev.yml`) to simplify to a single production-like environment.
- Added `Delivery` and `Notification` models, services, routes, and related Alembic migrations.
- Implemented WebSocket-based live tracking and a frontend `LiveTracking` page with a quick-jump from the `Navbar`.
- Seed and reset DB helpers are available under `backend/src/utils` and `backend/src/database/init`.

## Running and testing
Use the included `docker-compose.yml` for a single environment. Prefer `podman-compose` on systems using Podman.

Basic run steps:

```powershell
# Build and run (from repo root)
docker-compose up -d --build
# or with Podman
podman-compose up -d --build

# Backend health
curl http://localhost:8000/api/health
# API docs
curl http://localhost:8000/api/docs
# Frontend (production) should be served on port 3000 if compose maps it
curl http://localhost:3000/
```

To seed the database (inside the backend container or using the python CLI):

```powershell
python -m src.utils.db_cli init
python -m src.utils.db_cli seed
```

To run backend tests inside a container (recommended):

```powershell
# build a test image that contains test deps, then run pytest inside it
podman build -t courier-backend-test -f backend/Dockerfile backend
podman run --rm -v %CD%:/app:Z courier-backend-test sh -c "pytest -q"
```

## Notes & next steps
- RBAC columns were added to `User` model schema; full role enforcement is partially implemented — see `backend/src/services`.
- Rate-limiting middleware, additional integration tests, and frontend smoke tests remain to be added.
- If you want me to also build and validate the production frontend image and confirm endpoints, tell me and I'll run the compose cycle and health checks from here.

---
Keep this document concise; move project-specific runbooks into `docs/` for longer instructions.
Implement API integration
