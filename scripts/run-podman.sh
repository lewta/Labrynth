#!/bin/bash

# Run script for Labyrinth Adventure Game container using Podman
# This script runs the game in a Podman container with proper volume mounts

set -e  # Exit on any error

# Create local directories if they don't exist
mkdir -p saves logs

echo "Starting Labyrinth Adventure Game container with Podman..."

# Run the container with interactive mode and volume mounts
podman run -it --rm \
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