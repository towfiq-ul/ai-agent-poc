"""
Views for the RAG UI.
Each view is a thin proxy: it calls the FastAPI backend and renders a template.
The browser talks only to Django (:8000); Django relays to FastAPI (backend:8080)
over the internal Docker network.
"""
import json

import requests
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

BACKEND = settings.BACKEND_API_URL
TIMEOUT = int(getattr(settings, "BACKEND_TIMEOUT", 180))


# ---------------------------------------------------------------------------
# Page views
# ---------------------------------------------------------------------------

def index(request):
    """Main chat + dashboard page."""
    status = _backend_get("/status") or {}
    return render(request, "index.html", {"status": status})


def evaluate_page(request):
    """Evaluation runner page."""
    return render(request, "evaluate.html")


# ---------------------------------------------------------------------------
# API proxy views (called by JS fetch from the browser)
# Decorator order: @csrf_exempt must be outermost so it wraps @require_http_methods
# ---------------------------------------------------------------------------

@csrf_exempt
@require_http_methods(["POST"])
def api_query(request):
    try:
        body = json.loads(request.body)
        resp = requests.post(f"{BACKEND}/query", json=body, timeout=TIMEOUT)
        return JsonResponse(resp.json(), status=resp.status_code)
    except requests.exceptions.ConnectionError:
        return JsonResponse({"detail": "Backend is unreachable."}, status=503)
    except requests.exceptions.Timeout:
        return JsonResponse({"detail": "Backend timed out — LLM may still be loading."}, status=504)
    except Exception as exc:
        return JsonResponse({"detail": str(exc)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_index_files(request):
    try:
        files = [
            ("files", (f.name, f.read(), f.content_type or "text/plain"))
            for f in request.FILES.getlist("files")
        ]
        if not files:
            return JsonResponse({"detail": "No files received."}, status=400)
        resp = requests.post(f"{BACKEND}/index/files", files=files, timeout=TIMEOUT)
        return JsonResponse(resp.json(), status=resp.status_code)
    except requests.exceptions.ConnectionError:
        return JsonResponse({"detail": "Backend is unreachable."}, status=503)
    except requests.exceptions.Timeout:
        return JsonResponse({"detail": "Indexing timed out."}, status=504)
    except Exception as exc:
        return JsonResponse({"detail": str(exc)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_index_sample(request):
    try:
        resp = requests.post(f"{BACKEND}/index/sample", timeout=TIMEOUT)
        return JsonResponse(resp.json(), status=resp.status_code)
    except requests.exceptions.ConnectionError:
        return JsonResponse({"detail": "Backend is unreachable."}, status=503)
    except requests.exceptions.Timeout:
        return JsonResponse({"detail": "Indexing timed out."}, status=504)
    except Exception as exc:
        return JsonResponse({"detail": str(exc)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_reset(request):
    try:
        resp = requests.post(f"{BACKEND}/reset", timeout=30)
        return JsonResponse(resp.json(), status=resp.status_code)
    except requests.exceptions.ConnectionError:
        return JsonResponse({"detail": "Backend is unreachable."}, status=503)
    except Exception as exc:
        return JsonResponse({"detail": str(exc)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_evaluate(request):
    try:
        body = json.loads(request.body)
        resp = requests.post(f"{BACKEND}/evaluate", json=body, timeout=TIMEOUT)
        return JsonResponse(resp.json(), status=resp.status_code)
    except requests.exceptions.ConnectionError:
        return JsonResponse({"detail": "Backend is unreachable."}, status=503)
    except requests.exceptions.Timeout:
        return JsonResponse({"detail": "Evaluation timed out — try fewer questions."}, status=504)
    except Exception as exc:
        return JsonResponse({"detail": str(exc)}, status=500)


@require_http_methods(["GET"])
def api_status(request):
    try:
        resp = requests.get(f"{BACKEND}/status", timeout=5)
        return JsonResponse(resp.json(), status=resp.status_code)
    except requests.exceptions.ConnectionError:
        return JsonResponse({"detail": "Backend is unreachable."}, status=503)
    except Exception as exc:
        return JsonResponse({"detail": str(exc)}, status=500)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _backend_get(path: str) -> dict | None:
    """Silent GET used to pre-populate template context on page load."""
    try:
        resp = requests.get(f"{BACKEND}{path}", timeout=5)
        return resp.json()
    except Exception:
        return None
