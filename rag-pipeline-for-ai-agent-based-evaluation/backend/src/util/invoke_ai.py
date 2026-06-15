import os
import requests
from dotenv import load_dotenv

load_dotenv()

_DEFAULT_TIMEOUT = int(os.getenv("LLM_TIMEOUT_SECONDS", "180"))


def _invoke_ollama(system_message: str, user_message: str) -> str:
    """
    Call a locally-running Ollama instance.

    Required .env variables:
      AI_AGENT_MODEL    — model tag pulled in Ollama, e.g. "llama3.2"
      OLLAMA_BASE_URL   — (optional) defaults to http://localhost:11434
      LLM_TIMEOUT_SECONDS — (optional) request timeout in seconds, default 180
    """
    model = os.getenv("AI_AGENT_MODEL")
    if not model:
        raise ValueError("AI_AGENT_MODEL is not configured")

    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    url = f"{base_url}/api/chat"

    payload = {
        "model": model,
        "stream": False,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user",   "content": user_message},
        ],
    }

    try:
        response = requests.post(url, json=payload, timeout=_DEFAULT_TIMEOUT)
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            f"Could not connect to Ollama at {base_url}. "
            "Make sure Ollama is running: https://ollama.com"
        )
    except requests.exceptions.Timeout:
        raise RuntimeError(
            f"Ollama request timed out after {_DEFAULT_TIMEOUT}s. "
            "Try increasing LLM_TIMEOUT_SECONDS in .env."
        )

    data = response.json()
    text = data.get("message", {}).get("content")
    if not text:
        raise ValueError(f"Ollama returned an unexpected response: {data}")
    return text.strip()


def _invoke_groq(system_message: str, user_message: str) -> str:
    """
    Call the Groq inference API (free tier available at https://console.groq.com).

    Required .env variables:
      GROQ_API_KEY    — from https://console.groq.com
      AI_AGENT_MODEL  — Groq model ID, e.g. "llama-3.1-8b-instant"
    """
    try:
        from groq import Groq
    except ImportError:
        raise ImportError(
            "The 'groq' package is not installed. Run: pip install groq"
        )

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set in environment")

    model = os.getenv("AI_AGENT_MODEL")
    if not model:
        raise ValueError("AI_AGENT_MODEL is not configured")

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user",   "content": user_message},
        ],
    )

    text = response.choices[0].message.content
    if not text:
        raise ValueError("Groq returned an empty response")
    return text.strip()


# ---------------------------------------------------------------------------
# Public entry point — routes to the correct provider based on LLM_PROVIDER
# ---------------------------------------------------------------------------

_PROVIDERS = {
    "ollama": _invoke_ollama,
    "groq":   _invoke_groq,
}


def invoke_ai(system_message: str, user_message: str) -> str:
    """
    Invoke the configured LLM provider.

    Reads LLM_PROVIDER from .env (case-insensitive).
    Supported values: "ollama", "groq"
    Falls back to "ollama" if LLM_PROVIDER is not set.
    """
    provider = os.getenv("LLM_PROVIDER", "ollama").strip().lower()
    handler = _PROVIDERS.get(provider)
    if handler is None:
        raise ValueError(
            f"Unknown LLM_PROVIDER '{provider}'. "
            f"Valid options: {', '.join(_PROVIDERS)}"
        )
    return handler(system_message, user_message)
