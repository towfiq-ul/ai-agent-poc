FROM python:3.11-slim

ARG DJANGO_SECRET_KEY

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY ../frontend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ../frontend/ .

ENV DJANGO_SETTINGS_MODULE=rag_ui_project.settings

# Collect static files into /app/staticfiles at build time.
# WhiteNoise will serve them from there at runtime.
# DJANGO_SECRET_KEY is required by Django even for collectstatic.
RUN DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY} python manage.py collectstatic --noinput

EXPOSE 8000

# Gunicorn with WhiteNoise — no separate nginx needed for a POC
CMD ["gunicorn", "rag_ui_project.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "2", \
     "--timeout", "180"]