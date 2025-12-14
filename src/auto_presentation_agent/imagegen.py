from __future__ import annotations

"""Image generation helper with ComfyUI or Gemini backends plus placeholder fallback."""

import base64
import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# 1x1 PNG transparent pixel
_PIXEL = (
    b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGMA"
    b"AQAAAgAB9HFkqQAAAABJRU5ErkJggg=="
)


def generate_image(
    prompt: str,
    assets_dir: Path,
    backend: str = "comfy",
    endpoint: Optional[str] = None,
    gemini_client=None,
    gemini_image_model: Optional[str] = None,
) -> Optional[Path]:
    """
    Attempt to call a ComfyUI endpoint to generate an image.

    If no endpoint is provided or the call fails, emit a placeholder PNG so downstream
    assembly has a concrete asset path.
    """
    assets_dir.mkdir(parents=True, exist_ok=True)
    output = assets_dir / _safe_filename(prompt)

    if backend == "gemini" and gemini_client:
        try:
            data = gemini_client.generate_image(prompt, image_model=gemini_image_model)
            if data:
                output.write_bytes(data)
                return output
        except Exception as exc:  # pragma: no cover - network dependent
            logger.warning("Gemini image generation failed (%s); falling back.", exc)

    # Try calling ComfyUI if available.
    if backend == "comfy" and endpoint:
        import json
        import urllib.error
        import urllib.request

        payload = {"prompt": prompt}
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            endpoint.rstrip("/") + "/prompt",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status in (200, 201):
                    logger.info("ComfyUI accepted prompt for generation.")
                    # Real implementation would pull the generated image; placeholder written below.
        except Exception as exc:  # pragma: no cover - network dependent
            logger.warning("ComfyUI generation failed (%s); using placeholder.", exc)

    _write_placeholder_png(output)
    return output


def _write_placeholder_png(path: Path) -> None:
    """Write a tiny placeholder PNG."""
    path.write_bytes(base64.b64decode(_PIXEL))


def _safe_filename(prompt: str) -> str:
    token = "".join(ch if ch.isalnum() else "_" for ch in prompt)[:40] or "image"
    return f"{token}.png"
