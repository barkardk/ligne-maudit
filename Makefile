-include llm.mk
.PHONY: help venv install run clean test run0 run1 run2 run3 run4 run5

help:
	@echo "Ligne Maudite - Available commands:"
	@echo ""
	@echo "  make venv     - Create virtual environment and install dependencies"
	@echo "  make install  - Install/update dependencies in existing venv"
	@echo "  make run      - Run the full game (requires venv)"
	@echo "  make run0     - Run scene 0 (story) directly"
	@echo "  make run1     - Run scene 1 (forest path) directly"
	@echo "  make run2     - Run scene 2 (field) directly"
	@echo "  make run3     - Run scene 3 (behind bunker) directly"
	@echo "  make run4     - Run scene 4 (dragonteeth) directly"
	@echo "  make run5     - Run scene 5 (bunker interior) directly"
	@echo "  make clean    - Remove virtual environment"
	@echo "  make test     - Run tests (when available)"
	@echo ""
	@echo "  make load     - Open all project files in aider with selected model"
	@echo "                  (default: $(MODEL), override with MODEL=...)"
	@echo "  make readme   - Ask aider to generate a comprehensive README.md"
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
	@echo "Checking for Homebrew and SDL2..."
	@if ! command -v brew >/dev/null 2>&1; then \
		echo "ERROR: Homebrew not found. Please install Homebrew first:"; \
		echo "  /bin/bash -c \"\$$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""; \
		exit 1; \
	fi
	@echo "Installing required dependencies via Homebrew..."
	@brew install pkg-config sdl2 sdl2_image sdl2_mixer sdl2_ttf freetype
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

# Scene-specific run commands
run0:
	@if [ ! -d "venv" ]; then \
		echo "Virtual environment not found. Run 'make venv' first."; \
		exit 1; \
	fi
	@echo "Starting Scene 0 (Story)..."
	@./venv/bin/python main.py --scene 0

run1:
	@if [ ! -d "venv" ]; then \
		echo "Virtual environment not found. Run 'make venv' first."; \
		exit 1; \
	fi
	@echo "Starting Scene 1 (Forest Path)..."
	@./venv/bin/python main.py --scene 1

run2:
	@if [ ! -d "venv" ]; then \
		echo "Virtual environment not found. Run 'make venv' first."; \
		exit 1; \
	fi
	@echo "Starting Scene 2 (Field)..."
	@./venv/bin/python main.py --scene 2

run3:
	@if [ ! -d "venv" ]; then \
		echo "Virtual environment not found. Run 'make venv' first."; \
		exit 1; \
	fi
	@echo "Starting Scene 3 (Behind Bunker)..."
	@./venv/bin/python main.py --scene 3

run4:
	@if [ ! -d "venv" ]; then \
		echo "Virtual environment not found. Run 'make venv' first."; \
		exit 1; \
	fi
	@echo "Starting Scene 4 (Dragonteeth)..."
	@./venv/bin/python main.py --scene 4

run5:
	@if [ ! -d "venv" ]; then \
		echo "Virtual environment not found. Run 'make venv' first."; \
		exit 1; \
	fi
	@echo "Starting Scene 5 (Bunker Interior)..."
	@./venv/bin/python main.py --scene 5
