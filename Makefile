# Courier Delivery Management System - Docker Operations

.PHONY: help docker-build docker-up docker-down docker-logs docker-clean
.DEFAULT_GOAL := help

# Environment variables
ENV ?= prod
COMPOSE_FILE := docker-compose.yml
ifeq ($(ENV),dev)
	COMPOSE_FILE := docker-compose.dev.yml
endif

help: ## Show this help message
	@echo "Courier Delivery Management System - Docker Operations"
	@echo ""
	@echo "Usage: make [target] [ENV=environment]"
	@echo ""
	@echo "Targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "Environments: prod, dev"
	@echo "Default environment: $(ENV)"

# Docker operations
docker-build: ## Build Docker images
	@echo "🔨 Building Docker images for $(ENV) environment..."
	@docker-compose -f $(COMPOSE_FILE) build

docker-up: ## Start services
	@echo "🚀 Starting services for $(ENV) environment..."
	@docker-compose -f $(COMPOSE_FILE) up -d

docker-down: ## Stop services
	@echo "🛑 Stopping services..."
	@docker-compose -f $(COMPOSE_FILE) down

docker-restart: ## Restart services
	@echo "🔄 Restarting services..."
	@make docker-down ENV=$(ENV)
	@make docker-up ENV=$(ENV)

docker-logs: ## Show logs
	@echo "📋 Showing logs..."
	@docker-compose -f $(COMPOSE_FILE) logs -f

docker-logs-backend: ## Show backend logs
	@docker-compose -f $(COMPOSE_FILE) logs -f backend

docker-logs-frontend: ## Show frontend logs
	@docker-compose -f $(COMPOSE_FILE) logs -f frontend

docker-ps: ## Show running containers
	@docker-compose -f $(COMPOSE_FILE) ps

docker-clean: ## Clean up containers and images
	@echo "🧹 Cleaning up Docker resources..."
	@docker-compose -f $(COMPOSE_FILE) down -v
	@docker system prune -f

docker-clean-all: ## Clean up everything including volumes
	@echo "🧹 Cleaning up all Docker resources (including volumes)..."
	@docker-compose -f $(COMPOSE_FILE) down -v
	@docker system prune -a -f --volumes

# Development shortcuts
dev-setup: ## Setup development environment
	@echo "🛠️ Setting up development environment..."
	@./scripts/docker-setup.sh dev

prod-setup: ## Setup production environment
	@echo "🛠️ Setting up production environment..."
	@./scripts/docker-setup.sh prod

dev-up: ## Start development environment
	@make docker-up ENV=dev

dev-down: ## Stop development environment
	@make docker-down ENV=dev

prod-up: ## Start production environment
	@make docker-up ENV=prod

prod-down: ## Stop production environment
	@make docker-down ENV=prod

# Health checks
health-check: ## Check service health
	@echo "🏥 Checking service health..."
	@curl -f http://localhost:8000/api/health || echo "Backend not healthy"
	@curl -f http://localhost:3000 || echo "Frontend not healthy"

# Database operations in Docker
docker-db-init: ## Initialize database in Docker
	@echo "🗄️ Initializing database..."
	@docker-compose -f $(COMPOSE_FILE) exec backend python -m src.utils.db_cli init

docker-db-reset: ## Reset database in Docker
	@echo "🗄️ Resetting database..."
	@docker-compose -f $(COMPOSE_FILE) exec backend python -m src.utils.db_cli reset

docker-db-backup: ## Backup database
	@echo "💾 Creating database backup..."
	@docker-compose -f $(COMPOSE_FILE) exec postgres pg_dump -U courier_user courier_delivery > backup_$(shell date +%Y%m%d_%H%M%S).sql

# Utility commands
docker-shell-backend: ## Open shell in backend container
	@docker-compose -f $(COMPOSE_FILE) exec backend /bin/bash

docker-shell-frontend: ## Open shell in frontend container
	@docker-compose -f $(COMPOSE_FILE) exec frontend /bin/sh

docker-shell-postgres: ## Open PostgreSQL shell
	@docker-compose -f $(COMPOSE_FILE) exec postgres psql -U courier_user -d courier_delivery

# Monitoring
docker-stats: ## Show container resource usage
	@docker stats

docker-top: ## Show running processes in containers
	@docker-compose -f $(COMPOSE_FILE) top

api-docs-generate: ## Generate API documentation files
	@echo "📚 Generating API documentation..."
	@python scripts/generate-api-docs.py

api-docs-validate: ## Validate API endpoints
	@echo "🔍 Validating API endpoints..."
	@python scripts/validate-api.py

api-docs-serve: ## Serve API documentation locally
	@echo "🌐 Starting API documentation server..."
	@echo "Swagger UI: http://localhost:8000/docs"
	@echo "ReDoc: http://localhost:8000/redoc"
	@echo "OpenAPI JSON: http://localhost:8000/api/openapi.json"

api-test: ## Run API tests
	@echo "🧪 Running API tests..."
	@pytest tests/test_api.py -v

api-spec-export: ## Export OpenAPI specification
	@echo "📤 Exporting OpenAPI specification..."
	@curl -s http://localhost:8000/api/openapi.json | jq . > docs/api/openapi.json
	@echo "✅ OpenAPI spec exported to docs/api/openapi.json"