FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (layer-cached separately from source)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY src/ ./src/

# LanceDB stores its data under /data — this path is exposed as a volume
# so the database survives container restarts (see docker-compose.yml).
VOLUME ["/data"]

# Default working directory for CLI invocations
WORKDIR /app/src

ENTRYPOINT ["python", "main.py"]
