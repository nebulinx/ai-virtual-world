#!/bin/bash

set -e

echo "=== AI Virtual World Setup ==="

# Check for Poetry
if ! command -v poetry &> /dev/null; then
    echo "Poetry not found. Installing..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
fi

echo "Installing Python dependencies..."
poetry install

echo "Pulling Ollama models..."
if command -v ollama &> /dev/null; then
    echo "Pulling qwen2.5-coder:7b-q8_0..."
    ollama pull qwen2.5-coder:7b-q8_0 || echo "Warning: Failed to pull coder model"
    
    echo "Pulling deepseek-r1:7b-q8_0..."
    ollama pull deepseek-r1:7b-q8_0 || echo "Warning: Failed to pull reasoning model"
else
    echo "Warning: Ollama not found. Install Ollama to pull models."
fi

# Create .env template if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env template..."
    cat > .env << EOF
# Git Configuration
GIT_USER_NAME=AI Virtual World
GIT_USER_EMAIL=ai@virtualworld.local

# GitHub Token (optional, for token-based auth)
# GITHUB_TOKEN=your_token_here
EOF
    echo ".env file created. Please update with your git credentials."
fi

# Create necessary directories
mkdir -p backend/data/history
mkdir -p backend/data/backups

echo "Setup complete!"
