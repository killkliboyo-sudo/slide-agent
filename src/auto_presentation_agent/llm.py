from __future__ import annotations

"""Lightweight Gemini client wrapper with graceful fallback."""

import base64
import json
import logging
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class GeminiClient:
    api_key: str
    model: str = "gemini-1.5-pro-latest"

    def generate(self, prompt: str) -> Optional[str]:
        """Send a simple prompt to Gemini and return the text response."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        body = {"contents": [{"parts": [{"text": prompt}]}]}
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            logger.warning("Gemini request failed: %s", exc)
            return None
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Unexpected Gemini error: %s", exc)
            return None

        candidates = payload.get("candidates") or []
        if not candidates:
            return None
        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            return None
        return parts[0].get("text")

    def generate_image(self, prompt: str, image_model: Optional[str] = None) -> Optional[bytes]:
        """Generate an image via Gemini image generation (returns PNG bytes)."""
        model = image_model or "gemini-1.5-flash-latest"
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
        )
        body = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "image/png"},
        }
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            logger.warning("Gemini image request failed: %s", exc)
            return None
        candidates = payload.get("candidates") or []
        if not candidates:
            return None
        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            return None
        data_field = parts[0].get("inlineData") or {}
        if not data_field.get("data"):
            return None
        try:
            return base64.b64decode(data_field["data"])
        except Exception:  # pragma: no cover - defensive
            return None


def build_gemini_from_env(model: Optional[str] = None) -> Optional[GeminiClient]:
    """Construct a Gemini client when the API key is available."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None
    return GeminiClient(api_key=api_key, model=model or "gemini-1.5-pro-latest")


def list_gemini_models(api_key: str) -> list[str]:
    """Retrieve available Gemini model names using the public models endpoint."""
    url = "https://generativelanguage.googleapis.com/v1beta/models"
    req = urllib.request.Request(f"{url}?key={api_key}", method="GET")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
        logger.warning("Failed to list Gemini models: %s", exc)
        return []
    models = payload.get("models") or []
    return [model.get("name") for model in models if model.get("name")]
