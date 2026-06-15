import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

_gemini_api_key = os.getenv("GEMINI_API_KEY")
if not _gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set in environment")

_genai_client = genai.Client(api_key=_gemini_api_key)


def invoke_ai(system_message: str, user_message: str) -> str:
    """
    Invoke a Gemini model for text generation.

    Required .env variables:
      GEMINI_API_KEY   — Google AI Studio API key
      AI_AGENT_MODEL   — Gemini model name, e.g. "gemini-2.0-flash" or "gemini-1.5-pro"
    """
    model = os.getenv("AI_AGENT_MODEL")
    if not model:
        raise ValueError("AI_AGENT_MODEL is not configured")

    response = _genai_client.models.generate_content(
        model=model,
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=system_message,
        ),
    )

    if response.text is None:
        raise ValueError(
            f"Gemini returned no text. Finish reason: {response.candidates[0].finish_reason}"
        )

    return response.text
