# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TGV Times is a Streamlit web application that displays train schedules between French SNCF stations using the Navitia API.

## Development Commands

### Quick Start with Make
```bash
# Run the application
make app

# Install dependencies (includes dev dependencies)
make install

# Run linting checks
make lint

# Auto-fix linting issues
make lint-fix

# Format code
make format

# Run tests (to be implemented)
make test

# Clean Python cache files
make clean
```

### Manual Commands

#### Environment Setup
```bash
# Activate virtual environment
source .venv/bin/activate
```

#### Running the Application
```bash
# Run the Streamlit app (recommended)
streamlit run src/frontend/app.py

# Legacy: Run old single-file version
streamlit run src/main.py
```

#### Package Management
This project uses `uv` for dependency management:
```bash
# Install all dependencies including dev tools
uv sync --all-extras

# Install only runtime dependencies
uv sync
```

#### Code Quality
Ruff is configured for linting and formatting:
```bash
# Check linting and formatting
ruff check src/
ruff format --check src/

# Auto-fix issues
ruff check --fix src/

# Format code
ruff format src/
```

Configuration is in `pyproject.toml` under `[tool.ruff]`.

## Architecture

The codebase follows a backend/frontend separation pattern:

### Backend Layer (`src/backend/`)
Handles all external API interactions with the Navitia SNCF API.

- **sncf_api.py**: `SNCFAPIClient` class that encapsulates all Navitia API operations
  - `get_station_id(station_name)`: Resolves station names to Navitia station IDs
  - `get_journeys(departure_id, arrival_id)`: Fetches journey schedules between stations
  - Manages authentication headers and base URL configuration
  - Returns structured data (station IDs, journey lists) to frontend

### Frontend Layer (`src/frontend/`)
Streamlit UI that presents train schedules to users.

- **app.py**: Streamlit application entry point
  - Renders input fields for departure/arrival stations
  - Instantiates `SNCFAPIClient` for backend communication
  - Formats and displays journey data (times, durations)
  - Handles user errors (station not found, no journeys)

### API Integration Details
The backend integrates with Navitia SNCF API (api.navitia.io/v1/):
- Station lookup: `/coverage/sncf/places?q={query}&type[]=stop_area`
- Journey search: `/coverage/sncf/journeys?from={from_id}&to={to_id}`
- Authentication via API key in request headers

### Dependencies
- **streamlit**: Web UI framework
- **requests**: HTTP client for Navitia API calls

### Development Dependencies
- **ruff**: Fast Python linter and formatter (replaces flake8, black, isort, etc.)
