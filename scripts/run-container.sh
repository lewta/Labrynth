#!/bin/bash

# Run script for Labyrinth Adventure Game container
# This script runs the game in a container with proper volume mounts using Docker or Podman

set -e  # Exit on any error

# Create local directories if they don't exist
mkdir -p saves logs

echo "Starting Labyrinth Adventure Game container..."

# Detect available container runtime
if command -v docker &> /dev/null; then
    CONTAINER_CMD="docker"
    echo "Using Docker..."
elif command -v podman &> /dev/null; then
    CONTAINER_CMD="podman"
    echo "Using Podman..."
else
    echo "Error: Neither Docker nor Podman is available"
    exit 1
fi

# Run the container with interactive mode and volume mounts
$CONTAINER_CMD run -it --rm \
    --name labrynth-game \
    -v "$(pwd)/saves:/app/saves" \
    -v "$(pwd)/logs:/app/logs" \
    -v "$(pwd)/config:/app/config:ro" \
    -e GAME_DEBUG=false \
    -e GAME_LOG_LEVEL=INFO \
    -e GAME_SAVE_DIR=/app/saves \
    -e GAME_LOG_DIR=/app/logs \
    -e GAME_CONFIG_DIR=/app/config \
    labrynth:latest "$@"

echo "Game session ended."