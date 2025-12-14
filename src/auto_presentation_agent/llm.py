from __future__ import annotations

"""Lightweight Gemini client wrapper with graceful fallback."""

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
    model: str = "gemini-1.5-flash"

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


def build_gemini_from_env(model: Optional[str] = None) -> Optional[GeminiClient]:
    """Construct a Gemini client when the API key is available."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None
    return GeminiClient(api_key=api_key, model=model or "gemini-1.5-flash")
