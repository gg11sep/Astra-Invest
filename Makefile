.PHONY: help install dev up down logs test lint format typecheck clean migrate migrate-create seed shell

help:
	@echo "Astra-Invest Development Commands"
	@echo "================================="
	@echo "make install          Install backend dependencies"
	@echo "make dev              Start all services (docker compose up)"
	@echo "make up               Start services in background"
	@echo "make down             Stop all services"
	@echo "make logs             Tail backend logs"
	@echo "make test             Run tests with coverage"
	@echo "make lint             Run ruff linter"
	@echo "make format           Format code with black + ruff"
	@echo "make typecheck        Run mypy"
	@echo "make migrate          Apply database migrations"
	@echo "make migrate-create   Create a new migration (MSG='description')"
	@echo "make seed             Seed sample companies"
	@echo "make clean            Remove caches and build artifacts"
	@echo "make shell            Open a shell in the backend container"

install:
	cd backend && pip install -e ".[dev]"

dev:
	docker compose up --build

up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f backend

test:
	cd backend && pytest -v --cov=app --cov-report=term-missing

lint:
	cd backend && ruff check app tests

format:
	cd backend && black app tests && ruff check --fix app tests

typecheck:
	cd backend && mypy app

migrate:
	cd backend && alembic upgrade head

migrate-create:
	cd backend && alembic revision --autogenerate -m "$(MSG)"

seed:
	cd backend && python -m scripts.seed

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf backend/.coverage backend/dist backend/build

shell:
	docker compose exec backend bash
