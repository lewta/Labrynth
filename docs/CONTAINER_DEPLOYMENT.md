# Container Deployment Guide

This guide explains how to build, deploy, and run the Labyrinth Adventure Game using Docker containers.

## About Container Deployment

**Container deployment is completely optional.** The Labyrinth Adventure Game can be run directly with Python without any containerization. Containers provide the following benefits:

- **Isolated Environment:** Run the game in a clean, controlled environment
- **Consistent Dependencies:** Avoid Python version and dependency conflicts
- **Easy Distribution:** Share the game as a single container image
- **Simplified Setup:** No need to manage Python environments or dependencies
- **Cross-Platform:** Run consistently across different operating systems

Choose container deployment if you prefer isolated environments or want to avoid managing Python dependencies directly.

## Prerequisites

- Docker Engine 20.10+ or Podman 3.0+
- Docker Compose 2.0+ or Podman Compose (optional, for compose deployment)
- At least 256MB available memory
- 1GB available disk space

**Note:** The scripts automatically detect and use the available container runtime (Docker or Podman).

## Quick Start

### Option 1: Using Build and Run Scripts (Recommended)

1. **Build the container image:**
   ```bash
   ./scripts/build-container.sh
   ```

2. **Run the game:**
   ```bash
   ./scripts/run-container.sh
   ```

### Option 2: Using Docker Compose

1. **Run with Docker Compose:**
   ```bash
   ./scripts/run-compose.sh
   ```

   Or manually:
   ```bash
   docker-compose up --build labrynth-game
   ```

### Option 3: Manual Container Commands

**Using Docker:**
1. **Build the image:**
   ```bash
   docker build -t labrynth:latest .
   ```

2. **Run the container:**
   ```bash
   docker run -it --rm \
     --name labrynth-game \
     -v "$(pwd)/saves:/app/saves" \
     -v "$(pwd)/logs:/app/logs" \
     -v "$(pwd)/config:/app/config:ro" \
     labrynth:latest
   ```

**Using Podman:**
1. **Build the image:**
   ```bash
   podman build -t labrynth:latest .
   ```

2. **Run the container:**
   ```bash
   podman run -it --rm \
     --name labrynth-game \
     -v "$(pwd)/saves:/app/saves" \
     -v "$(pwd)/logs:/app/logs" \
     -v "$(pwd)/config:/app/config:ro" \
     labrynth:latest
   ```

**Podman-specific scripts:**
- `./scripts/build-podman.sh` - Build with Podman specifically
- `./scripts/run-podman.sh` - Run with Podman specifically

## Container Configuration

### Environment Variables

The container supports the following environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `GAME_DEBUG` | `false` | Enable debug mode |
| `GAME_LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `GAME_SAVE_DIR` | `/app/saves` | Directory for save games |
| `GAME_LOG_DIR` | `/app/logs` | Directory for log files |
| `GAME_CONFIG_DIR` | `/app/config` | Directory for configuration files |

### Volume Mounts

The container uses the following volume mounts for data persistence:

| Host Path | Container Path | Purpose | Mode |
|-----------|----------------|---------|------|
| `./saves` | `/app/saves` | Save game files | Read/Write |
| `./logs` | `/app/logs` | Application logs | Read/Write |
| `./config` | `/app/config` | Configuration files | Read-Only |

## Advanced Usage

### Custom Configuration

To use custom game configurations:

1. Modify files in the `config/` directory
2. The container will automatically use the updated configurations

### Debug Mode

To run the game in debug mode:

```bash
docker run -it --rm \
  --name labrynth-game \
  -v "$(pwd)/saves:/app/saves" \
  -v "$(pwd)/logs:/app/logs" \
  -v "$(pwd)/config:/app/config:ro" \
  -e GAME_DEBUG=true \
  -e GAME_LOG_LEVEL=DEBUG \
  labrynth:latest
```

### Persistent Named Volumes

For better data management, you can use named Docker volumes:

```bash
# Create named volumes
docker volume create labrynth-saves
docker volume create labrynth-logs

# Run with named volumes
docker run -it --rm \
  --name labrynth-game \
  -v labrynth-saves:/app/saves \
  -v labrynth-logs:/app/logs \
  -v "$(pwd)/config:/app/config:ro" \
  labrynth:latest
```

## Troubleshooting

### Common Issues

#### 1. Permission Denied on Scripts
**Problem:** Cannot execute build or run scripts
```bash
chmod +x scripts/*.sh
```

#### 2. Container Runtime Not Found
**Problem:** "docker: command not found" or "podman: command not found"

**Solutions:**
- **Install Docker:** Follow [Docker installation guide](https://docs.docker.com/get-docker/)
- **Install Podman:** Follow [Podman installation guide](https://podman.io/getting-started/installation)
- **Verify installation:** Run `docker --version` or `podman --version`

#### 3. Container Build Fails
**Problem:** Build process fails with errors

**Solutions:**
- Ensure Docker/Podman is running: `docker info` or `podman info`
- Check that all required files exist in the project directory
- Verify network connectivity for downloading base image
- Clear build cache: `docker system prune` or `podman system prune`
- Check Dockerfile syntax and dependencies

#### 4. Save Games Not Persisting
**Problem:** Game progress is lost between container runs

**Solutions:**
- Ensure the `saves/` directory exists: `mkdir -p saves`
- Check directory permissions: `chmod 755 saves`
- Verify volume mount paths in run commands
- Use absolute paths for volume mounts if relative paths fail

#### 5. Game Won't Start
**Problem:** Container starts but game doesn't run properly

**Solutions:**
- Check container logs: `docker logs labrynth-game`
- Verify all required files are copied to the container
- Ensure Python dependencies are properly installed
- Check for missing configuration files
- Verify container has sufficient resources

#### 6. Port or Resource Conflicts
**Problem:** Container fails to start due to resource conflicts

**Solutions:**
- Stop conflicting containers: `docker stop $(docker ps -q)`
- Remove stopped containers: `docker container prune`
- Check available disk space: `df -h`
- Monitor memory usage: `docker stats`

#### 7. Volume Mount Issues
**Problem:** Files not accessible or permission errors

**Solutions:**
- Use absolute paths: `-v /full/path/to/saves:/app/saves`
- Check SELinux contexts (on RHEL/CentOS): Add `:Z` flag to volumes
- Verify directory ownership matches container user
- Test with simple volume mount first

#### 8. Docker Compose Issues
**Problem:** Docker Compose fails to start services

**Solutions:**
- Verify docker-compose.yml syntax: `docker-compose config`
- Check service names match updated configuration
- Ensure all referenced images exist
- Use `docker-compose logs` to view service logs
- Try rebuilding: `docker-compose up --build --force-recreate`

### Advanced Troubleshooting

#### Container Debugging
To debug container issues, run an interactive shell:
```bash
# Docker
docker run -it --rm labrynth:latest /bin/bash

# Podman
podman run -it --rm labrynth:latest /bin/bash
```

#### Network Connectivity Testing
Test if the container can access external resources:
```bash
docker run --rm labrynth:latest ping -c 3 google.com
```

#### Resource Monitoring
Monitor container resource usage:
```bash
# Real-time stats
docker stats labrynth-game

# Historical usage
docker logs labrynth-game | grep -i memory
```

### Viewing Logs

#### Container Logs
To view container logs:
```bash
docker logs labrynth-game
```

#### Game Logs
To view game logs from mounted volume:
```bash
tail -f logs/game_*.log
```

#### Follow Logs in Real-time
```bash
docker logs -f labrynth-game
```

### Cleaning Up

#### Remove Container Image
```bash
docker rmi labrynth:latest
```

#### Clean Up Volumes
```bash
docker volume rm labrynth-saves labrynth-logs
```

#### Complete Cleanup
```bash
# Remove all stopped containers
docker container prune

# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune

# Remove unused networks
docker network prune
```

### Getting Help

If you continue to experience issues:

1. **Check the main README.md** for native Python installation instructions
2. **Review Docker/Podman documentation** for platform-specific issues
3. **Verify system requirements** are met
4. **Try running the game natively** to isolate container-specific issues
5. **Check container runtime logs** for system-level errors

## Security Considerations

- The container runs as a non-root user (`gameuser`) for security
- Configuration files are mounted read-only
- Resource limits are applied to prevent resource exhaustion
- No network ports are exposed (CLI-only application)

## Performance

- **Memory Usage:** ~128-256MB typical usage
- **CPU Usage:** Minimal (single-threaded CLI application)
- **Disk Usage:** ~100MB for image, variable for save games and logs
- **Startup Time:** ~2-5 seconds depending on system

## Integration with CI/CD

The container can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Build Container
  run: ./scripts/build-container.sh

- name: Test Container
  run: |
    docker run --rm labrynth:latest --help
```

For more information about the game itself, see the main [README.md](../README.md) file.