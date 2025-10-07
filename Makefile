.PHONY: help build up down restart logs shell migrate clean test

help: ## Show this help message
	@echo "Zynx AGI Core Foundation - Make Commands"
	@echo "========================================"
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Docker Operations
build: ## Build all containers
	docker-compose build

up: ## Start all services in background
	docker-compose up -d

down: ## Stop all services
	docker-compose down

restart: ## Restart all services
	make down && make up

logs: ## Show logs from all services
	docker-compose logs -f

##@ Database Operations
migrate: ## Run database migrations
	docker-compose exec web alembic upgrade head

migrate-rollback: ## Rollback last migration
	docker-compose exec web alembic downgrade -1

migrate-create: ## Create new migration (use name=migration_name)
	docker-compose exec web alembic revision --autogenerate -m "$(name)"

##@ Development
shell: ## Open shell in web container
	docker-compose exec web bash

test: ## Run tests
	docker-compose exec web python -m pytest tests/ -v

lint: ## Run code linting
	docker-compose exec web python -m black app/
	docker-compose exec web python -m flake8 app/

##@ Data Operations
seed: ## Seed database with sample data (migrations handle this)
	@echo "✅ Seed data is handled by migration 0003_seed_manifest.py"

backup-db: ## Backup database
	docker-compose exec postgres pg_dump -U zynxuser zynxagi > backup_$(shell date +%Y%m%d_%H%M%S).sql

##@ Cleanup
clean: ## Clean up containers, volumes, and images
	docker-compose down -v --remove-orphans
	docker system prune -f

clean-all: ## Clean everything including images
	docker-compose down -v --remove-orphans
	docker system prune -af

##@ Health Checks
status: ## Check service status
	docker-compose ps

health: ## Check application health
	@echo "🔍 Checking service health..."
	@curl -s http://localhost:8000/health || echo "❌ Web service not responding"
	@curl -s http://localhost:8000/api/v1/llm/ping || echo "❌ LLM service not responding"

##@ Quick Operations
dev: ## Start development environment (build + up + migrate)
	make build && make up && sleep 10 && make migrate

stop: ## Alias for down
	make down