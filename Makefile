.PHONY: help install up down api processor test lint format clean

help:
	@echo "Trade Reconciliation Platform"
	@echo ""
	@echo "  make up           Start all services (Docker Compose)"
	@echo "  make down         Stop all services"
	@echo "  make api          Run API service locally (port 8000)"
	@echo "  make processor    Run Processor service locally (port 8001)"
	@echo "  make test         Run tests"
	@echo "  make lint         Lint with ruff"
	@echo "  make format       Format with black"
	@echo "  make clean        Remove cache files"

install:
	pip install -r requirements.txt

up:
	docker compose up --build

down:
	docker compose down

api:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

processor:
	python -m app.processor.worker

test:
	pytest tests/ -v

lint:
	ruff check app/ tests/

format:
	black app/ tests/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache htmlcov .coverage
