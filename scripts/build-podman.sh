#!/bin/bash

# Build script for Labyrinth Adventure Game container using Podman
# This script builds the container image for the game using Podman

set -e  # Exit on any error

echo "Building Labyrinth Adventure Game container with Podman..."

# Build the container image
podman build -t labrynth:latest .

echo "Container build completed successfully!"
echo "Image: labrynth:latest"

# Show image information
echo ""
echo "Image details:"
podman images labrynth:latest