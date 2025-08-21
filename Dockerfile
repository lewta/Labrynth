# Use Python 3.12-slim as base image for optimal size and security
FROM python:3.12-slim

# Set working directory in container
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Create directories for game data persistence
RUN mkdir -p /app/saves /app/logs /app/config

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy game source code and configuration
COPY src/ ./src/
COPY config/ ./config/
COPY game_config.json .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash gameuser && \
    chown -R gameuser:gameuser /app
USER gameuser

# Expose any ports if needed (none for this CLI game)
# EXPOSE 8000

# Set the entry point to run the game
ENTRYPOINT ["python", "-m", "src.main"]

# Default command arguments (can be overridden)
CMD []