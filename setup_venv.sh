#!/bin/bash

# Maginot RPG Virtual Environment Setup Script

echo "Setting up virtual environment for Maginot RPG..."

# Check if Python 3.10+ is available
PYTHON_CMD=""
MIN_VERSION="3.10"

# Try different Python commands
for cmd in python3.14 python3.13 python3.12 python3.11 python3.10 python3 python; do
    if command -v "$cmd" >/dev/null 2>&1; then
        VERSION=$($cmd -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" 2>/dev/null; then
            PYTHON_CMD="$cmd"
            echo "Found suitable Python: $cmd (version $VERSION)"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "ERROR: Python 3.10 or higher is required but not found."
    echo "Please install Python 3.10+ and try again."
    echo "You can download it from: https://www.python.org/downloads/"
    exit 1
fi

# Remove existing venv if it exists
if [ -d "venv" ]; then
    echo "Removing existing virtual environment..."
    rm -rf venv
fi

# Create virtual environment
echo "Creating virtual environment with $PYTHON_CMD..."
$PYTHON_CMD -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

echo ""
echo "✅ Virtual environment setup complete!"
echo ""
echo "To activate the virtual environment in the future, run:"
echo "    source venv/bin/activate"
echo ""
echo "To run the game:"
echo "    python main.py"
echo ""
echo "To deactivate when done:"
echo "    deactivate"