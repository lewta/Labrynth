#!/bin/bash

# Build script for Labyrinth Adventure Game container
# This script builds the container image using Docker or Podman

set -e  # Exit on any error

echo "Building Labyrinth Adventure Game container..."

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

# Build the container image
$CONTAINER_CMD build -t labrynth:latest .

echo "Container build completed successfully!"
echo "Image: labrynth:latest"

# Show image information
echo ""
echo "Image details:"
$CONTAINER_CMD images labrynth:latest