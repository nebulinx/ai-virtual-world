#!/bin/bash

set -e

echo "=== AI Virtual World Docker Startup ==="

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "Error: Docker not found. Please install Docker."
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "Error: Docker Compose not found. Please install Docker Compose."
    exit 1
fi

# Check for Poetry (needed for model pulling)
if command -v poetry &> /dev/null; then
    echo "Poetry found. Checking models..."
    
    # Pull models if Ollama is available locally
    if command -v ollama &> /dev/null; then
        echo "Pulling quantized models..."
        ollama pull qwen2.5-coder:7b-q8_0 || echo "Warning: Failed to pull coder model"
        ollama pull deepseek-r1:7b-q8_0 || echo "Warning: Failed to pull reasoning model"
    else
        echo "Note: Ollama not found locally. Models will be pulled in Docker container."
    fi
else
    echo "Warning: Poetry not found. Models may need to be pulled manually."
fi

# Start services
echo "Starting Docker services..."
if docker compose version &> /dev/null; then
    docker compose up -d
else
    docker-compose up -d
fi

echo "Waiting for services to be ready..."
sleep 5

# Check service health
echo "Checking service health..."
if docker ps | grep -q ai-virtual-world-backend; then
    echo "✓ Backend service is running"
else
    echo "✗ Backend service failed to start"
fi

if docker ps | grep -q ai-virtual-world-ollama; then
    echo "✓ Ollama service is running"
    
    # Pull models in container if needed
    echo "Ensuring models are available in Ollama container..."
    docker exec ai-virtual-world-ollama ollama pull qwen2.5-coder:7b-q8_0 || true
    docker exec ai-virtual-world-ollama ollama pull deepseek-r1:7b-q8_0 || true
else
    echo "✗ Ollama service failed to start"
fi

echo ""
echo "=== Services Started ==="
echo "Backend logs: docker logs -f ai-virtual-world-backend"
echo "Ollama logs: docker logs -f ai-virtual-world-ollama"
echo "Stop services: docker compose down"
