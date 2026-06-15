FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first (layer-cached separately from source)
COPY ../backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY ../backend/src/ ./src/

# Copy sample data so the container works standalone (without compose bind-mount)
COPY ../sample_data/ ./sample_data/

# Named volumes declared here so Docker tracks them
VOLUME ["/data"]
VOLUME ["/root/.cache/huggingface"]

WORKDIR /app/src

EXPOSE 8080

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]