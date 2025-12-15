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
        model = image_model or "imagen-4.0-generate-001"
        
        # Imagen models typically use the :predict endpoint
        if "imagen" in model.lower():
            # Ensure model name includes 'models/' prefix for the URL if needed, 
            # or just construct URL with models/{model} if input is bare ID.
            # Safest is to strip prefix if present and use fixed structure.
            model_id = model.replace("models/", "")
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:predict?key={self.api_key}"
            body = {
                "instances": [{"prompt": prompt}],
                "parameters": {"sampleCount": 1},
            }
            data = json.dumps(body).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    payload = json.loads(resp.read().decode("utf-8"))
            except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
                logger.warning("Gemini image request (predict) failed: %s", exc)
                return None
                
            predictions = payload.get("predictions") or []
            if not predictions:
                return None
                
            # Handle possible response formats (string base64 or dict with bytesBase64Encoded)
            first_pred = predictions[0]
            b64_data = None
            if isinstance(first_pred, str):
                b64_data = first_pred
            elif isinstance(first_pred, dict):
                b64_data = first_pred.get("bytesBase64Encoded")
                
            if not b64_data:
                return None
                
            try:
                return base64.b64decode(b64_data)
            except Exception:
                return None

        # Fallback for other models (e.g. older Gemini models using generateContent)
        # Nano Banana (models/nano-banana-pro-preview) fails with responseMimeType: image/png
        # So we omit it for that model, or maybe generally if not sure.
        # But older gemini-1.5-flash-latest might have needed it (though it failed too in tests).
        # Let's make it conditional or just try without it for nano.
        
        generation_config = {}
        if "nano" not in model.lower() and "banana" not in model.lower():
            if "flash-image" in model.lower():
                generation_config["responseModalities"] = ["IMAGE"]
            else:
                 generation_config["responseMimeType"] = "image/png"

        # Ensure model name includes 'models/' prefix for the URL if needed, 
        # or just construct URL with models/{model} if input is bare ID.
        model_id = model.replace("models/", "")
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={self.api_key}"
        )
        body = {
            "contents": [{"parts": [{"text": prompt}]}],
        }
        if generation_config:
            body["generationConfig"] = generation_config
            
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


def list_gemini_models(api_key: str, kind: str = "all") -> list[str]:
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
    names: list[str] = []
    kind = (kind or "all").lower()
    for model in models:
        name = model.get("name")
        if not name:
            continue
        methods = model.get("supportedGenerationMethods") or model.get("supported_generation_methods") or []
        is_text = "generateContent" in methods
        is_image = "image" in name.lower() or "vision" in name.lower()
        if kind == "text" and not is_text:
            continue
        if kind == "image" and not (is_text and is_image):
            continue
        names.append(name)
    return names
