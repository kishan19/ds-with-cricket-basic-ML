.DEFAULT_GOAL := help
SOURCE ?= ipl

.PHONY: help setup data lab test lint fmt typecheck check clean

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

setup:  ## Create the venv and install everything (uv)
	uv sync --all-extras
	uv run pre-commit install
	uv run python -m ipykernel install --user --name cricketml --display-name "Python (cricketml)"

data:  ## Download + flatten a Cricsheet source, e.g. make data SOURCE=t20i
	uv run cricketml build-data --source $(SOURCE)

lab:  ## Start JupyterLab
	uv run jupyter lab

test:  ## Run the test suite
	uv run pytest

lint:  ## Lint everything, notebooks included
	uv run ruff check src tests lessons

fmt:  ## Format everything
	uv run ruff format src tests
	uv run ruff check --fix src tests lessons

typecheck:  ## Type-check the shared package
	uv run mypy

check: lint typecheck test  ## What CI runs

clean:  ## Remove caches and build artefacts (never touches data/)
	rm -rf .pytest_cache .ruff_cache .mypy_cache dist build
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
