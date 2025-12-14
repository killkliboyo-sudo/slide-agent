from __future__ import annotations

"""ComfyUI image generation helper with a local placeholder fallback."""

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


def generate_image(prompt: str, assets_dir: Path, endpoint: Optional[str]) -> Optional[Path]:
    """
    Attempt to call a ComfyUI endpoint to generate an image.

    If no endpoint is provided or the call fails, emit a placeholder PNG so downstream
    assembly has a concrete asset path.
    """
    assets_dir.mkdir(parents=True, exist_ok=True)
    output = assets_dir / _safe_filename(prompt)

    # Try calling ComfyUI if available.
    if endpoint:
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
                    # If ComfyUI responds with an image URL or bytes, this is where it would be saved.
                    # For now we just note success and still drop a placeholder.
                    logger.info("ComfyUI accepted prompt for generation.")
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
