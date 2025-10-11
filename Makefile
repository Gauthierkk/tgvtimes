.PHONY: help app install test lint lint-fix format clean data-playground

# Check if virtual environment exists and set activation command
VENV_DIR := .venv
VENV_ACTIVATE := $(VENV_DIR)/bin/activate
VENV_PYTHON := $(VENV_DIR)/bin/python
VENV_EXISTS := $(shell [ -d $(VENV_DIR) ] && echo 1 || echo 0)

# Use venv python if available, otherwise use system python
ifeq ($(VENV_EXISTS),1)
	PYTHON := $(VENV_PYTHON)
	ACTIVATE := . $(VENV_ACTIVATE) &&
else
	PYTHON := python3
	ACTIVATE :=
endif

help:
	@echo "Available commands:"
	@echo "  make app            - Run the Streamlit application"
	@echo "  make data-playground - Run the data playground for API exploration"
	@echo "  make install        - Install dependencies using uv"
	@echo "  make test           - Run tests (to be implemented)"
	@echo "  make lint           - Run ruff linter and formatter checks"
	@echo "  make lint-fix       - Auto-fix linting issues"
	@echo "  make format         - Format code with ruff"
	@echo "  make clean          - Remove Python cache files"

app:
	@echo "Starting TGV Times application..."
	$(ACTIVATE) streamlit run src/frontend/app.py

data-playground:
	@echo "Starting data playground..."
	$(ACTIVATE) python src/api_explo/data_playground.py

install:
	@echo "Installing dependencies..."
	uv sync --all-extras

test:
	@echo "Running tests..."
	@echo "Tests not yet implemented"

lint:
	@echo "Running ruff checks..."
	$(ACTIVATE) ruff check src/
	$(ACTIVATE) ruff format --check src/

lint-fix:
	@echo "Auto-fixing linting issues..."
	$(ACTIVATE) ruff check --fix src/

format:
	@echo "Formatting code with ruff..."
	$(ACTIVATE) ruff format src/

clean:
	@echo "Cleaning up Python cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
