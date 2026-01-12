# Courier Delivery Management System - Database Operations

.PHONY: help db-info db-create db-drop db-reset db-seed db-init db-check db-cleanup
.DEFAULT_GOAL := help

# Environment variables
ENV ?= development
PYTHON := python
DB_CLI := $(PYTHON) -m src.utils.db_cli

help: ## Show this help message
	@echo "Courier Delivery Management System - Database Operations"
	@echo ""
	@echo "Usage: make [target] [ENV=environment]"
	@echo ""
	@echo "Targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "Environments: development, production, test"
	@echo "Default environment: $(ENV)"

db-info: ## Show database information
	@echo "🔍 Getting database information..."
	@ENVIRONMENT=$(ENV) $(DB_CLI) info

db-create: ## Create database tables
	@echo "🔧 Creating database tables..."
	@ENVIRONMENT=$(ENV) $(DB_CLI) create

db-drop: ## Drop database tables
	@echo "🗑️  Dropping database tables..."
	@ENVIRONMENT=$(ENV) $(DB_CLI) drop

db-reset: ## Reset database (drop and recreate)
	@echo "🔄 Resetting database..."
	@ENVIRONMENT=$(ENV) $(DB_CLI) reset

db-seed: ## Seed database with sample data
	@echo "🌱 Seeding database with sample data..."
	@ENVIRONMENT=$(ENV) $(DB_CLI) seed

db-init: ## Initialize database (create + seed)
	@echo "🚀 Initializing database..."
	@ENVIRONMENT=$(ENV) $(DB_CLI) init

db-check: ## Check database connection
	@echo "🔍 Checking database connection..."
	@ENVIRONMENT=$(ENV) $(DB_CLI) check

db-cleanup: ## Clean up test data
	@echo "🧹 Cleaning up test data..."
	@ENVIRONMENT=$(ENV) $(DB_CLI) cleanup

# Migration commands
migrate-create: ## Create a new migration
	@echo "📝 Creating new migration..."
	@ENVIRONMENT=$(ENV) alembic revision --autogenerate -m "$(MSG)"

migrate-up: ## Run migrations
	@echo "⬆️  Running migrations..."
	@ENVIRONMENT=$(ENV) alembic upgrade head

migrate-down: ## Rollback last migration
	@echo "⬇️  Rolling back migration..."
	@ENVIRONMENT=$(ENV) alembic downgrade -1

migrate-history: ## Show migration history
	@echo "📜 Migration history:"
	@ENVIRONMENT=$(ENV) alembic history

# Docker commands
docker-db-up: ## Start PostgreSQL database container
	@echo "🐳 Starting PostgreSQL container..."
	@docker-compose up -d postgres

docker-db-down: ## Stop PostgreSQL database container
	@echo "🐳 Stopping PostgreSQL container..."
	@docker-compose down postgres

docker-db-logs: ## Show PostgreSQL container logs
	@echo "📋 PostgreSQL container logs:"
	@docker-compose logs -f postgres

# Development commands
dev-setup: ## Set up development environment
	@echo "🛠️  Setting up development environment..."
	@cp .env.development .env
	@make db-init ENV=development
	@echo "✅ Development environment ready!"

prod-setup: ## Set up production environment
	@echo "🛠️  Setting up production environment..."
	@cp .env.production .env
	@make docker-db-up
	@sleep 10
	@make migrate-up ENV=production
	@make db-seed ENV=production
	@echo "✅ Production environment ready!"

test-setup: ## Set up test environment
	@echo "🛠️  Setting up test environment..."
	@cp .env.test .env
	@make db-init ENV=test
	@echo "✅ Test environment ready!"