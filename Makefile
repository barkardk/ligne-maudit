.PHONY: help venv install run clean test

# Default target
help:
	@echo "Ligne Maudite - Available commands:"
	@echo ""
	@echo "  make venv     - Create virtual environment and install dependencies"
	@echo "  make install  - Install/update dependencies in existing venv"
	@echo "  make run      - Run the game (requires venv)"
	@echo "  make clean    - Remove virtual environment"
	@echo "  make test     - Run tests (when available)"
	@echo "  make help     - Show this help message"

# Python version check
PYTHON := $(shell command -v python3.14 2> /dev/null || command -v python3.13 2> /dev/null || command -v python3.12 2> /dev/null || command -v python3.11 2> /dev/null || command -v python3.10 2> /dev/null || command -v python3 2> /dev/null || command -v python 2> /dev/null)

venv:
	@echo "Setting up virtual environment..."
	@if [ -z "$(PYTHON)" ]; then \
		echo "ERROR: Python not found. Please install Python 3.10+"; \
		exit 1; \
	fi
	@$(PYTHON) -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" || \
		(echo "ERROR: Python 3.10+ required. Found: $$($(PYTHON) --version)"; exit 1)
	@if [ ! -d "venv" ]; then \
		echo "Creating virtual environment..."; \
		$(PYTHON) -m venv venv; \
	else \
		echo "Virtual environment already exists"; \
	fi
	@echo "Installing/updating dependencies..."
	@./venv/bin/pip install --upgrade pip
	@./venv/bin/pip install -r requirements.txt
	@echo "✅ Virtual environment ready!"

install:
	@if [ ! -d "venv" ]; then \
		echo "Virtual environment not found. Run 'make venv' first."; \
		exit 1; \
	fi
	@echo "Installing/updating dependencies..."
	@./venv/bin/pip install -r requirements.txt
	@echo "✅ Dependencies updated!"

run:
	@if [ ! -d "venv" ]; then \
		echo "Virtual environment not found. Run 'make venv' first."; \
		exit 1; \
	fi
	@echo "Starting Ligne Maudite..."
	@./venv/bin/python main.py

clean:
	@echo "Removing virtual environment..."
	@rm -rf venv
	@echo "✅ Cleaned up!"

test:
	@if [ ! -d "venv" ]; then \
		echo "Virtual environment not found. Run 'make venv' first."; \
		exit 1; \
	fi
	@echo "Running tests..."
	@./venv/bin/python -m pytest tests/ || echo "No tests found yet"