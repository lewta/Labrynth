#!/bin/bash

# Docker Compose run script for Labyrinth Adventure Game
# This script uses docker-compose to run the game with all configurations

set -e  # Exit on any error

# Create local directories if they don't exist
mkdir -p saves logs

echo "Starting Labyrinth Adventure Game with Docker Compose..."

# Check if docker-compose is available
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif command -v docker &> /dev/null && docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    echo "Error: Neither docker-compose nor 'docker compose' is available"
    exit 1
fi

# Run with docker-compose
$COMPOSE_CMD up --build labrynth-game

echo "Game session ended."