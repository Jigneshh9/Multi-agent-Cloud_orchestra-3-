SHELL := /bin/bash
PY ?= python
VENV := .venv
BIN := $(VENV)/Scripts

.PHONY: help install install-dev lint typecheck test test-cov run-api run-orchestrator eval ablation docker-up docker-down

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'

install: ## Create venv and install base deps
	$(PY) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -e ".[api,dev]"

install-full: ## Install everything (postgres, vector, rl, otel)
	$(BIN)/pip install -e ".[api,postgres,vector,rl,otel,dev]"

lint: ## Lint with ruff
	$(BIN)/ruff check src tests

typecheck: ## Type-check with mypy
	$(BIN)/mypy src

test: ## Run unit + integration tests
	$(BIN)/pytest -q

test-cov: ## Run tests with coverage report
	$(BIN)/pytest --cov=cloud_orchestra --cov-report=term-missing --cov-fail-under=80

run-api: ## Run the control-plane API
	$(BIN)/uvicorn cloud_orchestra.api.app:app --reload --port 8000

run-orchestrator: ## Run all agents + orchestrator in a single process
	$(BIN)/cloud-orchestra run --all

eval: ## Run the evaluation harness (baseline)
	$(BIN)/cloud-orchestra eval

ablation: ## Run all five ablation studies
	$(BIN)/cloud-orchestra ablation

docker-up: ## Start infra (postgres, redis, chroma) via docker compose
	docker compose up -d postgres redis chroma

docker-down:
	docker compose down
