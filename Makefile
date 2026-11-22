# CardioScreen AI - Makefile
# Common development commands

.PHONY: help install install-dev train serve test lint format typecheck clean docker-build docker-run docker-dev

# Default target
help:
	@echo "CardioScreen AI - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install       - Install runtime dependencies"
	@echo "  make install-dev   - Install development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make train         - Train models (compare all, save best)"
	@echo "  make serve         - Start API server + Web UI"
	@echo "  make test          - Run all tests"
	@echo "  make lint          - Run linter (ruff)"
	@echo "  make format        - Auto-format code (black + ruff)"
	@echo "  make typecheck     - Run type checker (mypy)"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-run    - Run Docker container"
	@echo "  make docker-dev    - Run Docker dev container with hot reload"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean         - Remove cache and build artifacts"
	@echo "  make check         - Run all checks (lint + typecheck + test)"

# Python and paths
PYTHON := python
PIP := pip
VENV := .venv
VENV_PYTHON := $(VENV)/Scripts/python.exe
VENV_PIP := $(VENV)/Scripts/pip.exe

# Detect OS
ifeq ($(OS),Windows_NT)
    VENV_PYTHON := $(VENV)/Scripts/python.exe
    VENV_PIP := $(VENV)/Scripts/pip.exe
    ACTIVATE := $(VENV)/Scripts/Activate.ps1
else
    VENV_PYTHON := $(VENV)/bin/python
    VENV_PIP := $(VENV)/bin/pip
    ACTIVATE := source $(VENV)/bin/activate
endif

# Setup
install:
	$(PYTHON) -m venv $(VENV)
	$(VENV_PIP) install --upgrade pip
	$(VENV_PIP) install -r requirements.txt

install-dev:
	$(PYTHON) -m venv $(VENV)
	$(VENV_PIP) install --upgrade pip
	$(VENV_PIP) install -r requirements-dev.txt

# Development
train:
	$(VENV_PYTHON) -m cardioscreen train

serve:
	$(VENV_PYTHON) -m cardioscreen serve

# Testing
test:
	$(VENV_PYTHON) -m pytest -v

test-unit:
	$(VENV_PYTHON) -m pytest tests/unit -v

test-integration:
	$(VENV_PYTHON) -m pytest tests/integration -v

test-coverage:
	$(VENV_PYTHON) -m pytest --cov=cardioscreen --cov-report=html --cov-report=term

# Code Quality
lint:
	$(VENV_PYTHON) -m ruff check cardioscreen/ tests/

format:
	$(VENV_PYTHON) -m black cardioscreen/ tests/
	$(VENV_PYTHON) -m ruff check --fix cardioscreen/ tests/

typecheck:
	$(VENV_PYTHON) -m mypy cardioscreen/ --ignore-missing-imports

check: lint typecheck test

# Docker
docker-build:
	docker build -t cardioscreen-ai -f deployment/docker/Dockerfile .

docker-run:
	docker run -d -p 8000:8000 --name cardioscreen cardioscreen-ai

docker-dev:
	docker-compose -f deployment/docker/docker-compose.yml --profile dev up --build

docker-train:
	docker-compose -f deployment/docker/docker-compose.yml --profile training run --rm trainer

docker-stop:
	docker stop cardioscreen || true
	docker rm cardioscreen || true

# Cleanup
clean:
	rm -rf __pycache__/
	rm -rf cardioscreen/__pycache__/
	rm -rf tests/__pycache__/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Pre-commit
pre-commit-install:
	$(VENV_PIP) install pre-commit
	$(VENV_PYTHON) -m pre_commit install

pre-commit-run:
	$(VENV_PYTHON) -m pre_commit run --all-files