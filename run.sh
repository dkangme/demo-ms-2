#!/bin/bash
set -e

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "Docker is required but not installed. Exiting."
    exit 1
fi

# Detect Docker Compose command
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    echo "Docker Compose is required but not found. Exiting."
    exit 1
fi

# Set up .env if missing
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ .env created from .env.example"
    echo "  Please edit .env and set GCP_PROJECT (and optionally GOOGLE_APPLICATION_CREDENTIALS) before running."
fi

# Build and start services
echo "Building and starting services..."
$DOCKER_COMPOSE up --build -d

# Wait for health check
echo "Waiting for backend to become healthy..."
for i in {1..30}; do
    if $DOCKER_COMPOSE ps | grep -q "healthy"; then
        break
    fi
    sleep 2
done

echo ""
echo "=================================================="
echo "  Demo MS 2 is running!"
echo "  Health check: http://localhost:8080/health"
echo "  API base:     http://localhost:8080"
echo "=================================================="
