#!/usr/bin/env bash
# Usage: ./load_repo_into_aider.sh <model>
# Example: ./load_repo_into_aider.sh ollama_chat/codellama:7b

MODEL=${1:-ollama_chat/stable-code:3b}

# Exclude heavy/unnecessary dirs
EXCLUDES="(.git|node_modules|venv|.venv|dist|build|__pycache__)"

# Build file list
FILES=$(find . -type f \
  | grep -Ev "$EXCLUDES" \
  | sort)

echo "Launching aider with model: $MODEL"
echo "Loading files into context..."

# Run aider with all files
aider --model "$MODEL" $FILES
