"""
Django settings for the RAG UI frontend.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret-change-in-production")

DEBUG = os.getenv("DJANGO_DEBUG", "true").lower() == "true"

_raw_hosts = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost 127.0.0.1 frontend 0.0.0.0")
ALLOWED_HOSTS = _raw_hosts.replace(",", " ").split()

INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "rag_ui",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "rag_ui_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
            ],
        },
    },
]

WSGI_APPLICATION = "rag_ui_project.wsgi.application"

# Static files — WhiteNoise compresses and caches with content-hash filenames
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Backend API base URL — injected from docker-compose environment
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://backend:8080")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
