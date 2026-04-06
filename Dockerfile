FROM python:3.12-slim

WORKDIR /app

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Dependencies first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Game source and config
COPY src/ ./src/
COPY config/ ./config/

# Non-root user
RUN useradd --create-home --shell /bin/bash gameuser && \
    chown -R gameuser:gameuser /app
USER gameuser

ENTRYPOINT ["python", "-m", "src.main"]
