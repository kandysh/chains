.PHONY: help install run test lint format type-check dev clean

help:
	@echo "Available commands:"
	@echo "  make install      - Install dependencies"
	@echo "  make dev          - Run development server"
	@echo "  make test         - Run tests"
	@echo "  make test-cov     - Run tests with coverage"
	@echo "  make lint         - Lint code"
	@echo "  make format       - Format code with Black"
	@echo "  make type-check   - Run type checking"
	@echo "  make clean        - Remove cache files"

install:
	poetry install

dev:
	poetry run uvicorn app.main:app --reload

test:
	poetry run pytest

test-cov:
	poetry run pytest --cov=app --cov-report=html

lint:
	poetry run ruff check .

format:
	poetry run black .

type-check:
	poetry run mypy app

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache htmlcov .coverage
