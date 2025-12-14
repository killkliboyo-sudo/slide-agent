from __future__ import annotations

"""CLI entry for the automated slide-generation agent."""

import argparse
import logging
from pathlib import Path

from .models import PresentationRequest
from .pipeline import run_pipeline


def _expand_inputs(paths: list[Path]) -> tuple[list[Path], list[Path]]:
    """Expand user paths and split into existing vs missing."""
    resolved: list[Path] = []
    missing: list[Path] = []
    for raw in paths:
        path = raw.expanduser()
        if path.exists():
            resolved.append(path)
        else:
            missing.append(path)
    return resolved, missing


def _parse_style_overrides(raw: list[str]) -> dict[str, str]:
    """Parse key=value style overrides from CLI."""
    styles: dict[str, str] = {}
    for item in raw:
        if "=" in item:
            key, value = item.split("=", 1)
            styles[key.strip()] = value.strip()
    return styles


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Auto Presentation Agent")
    parser.add_argument(
        "--input",
        "-i",
        type=Path,
        nargs="*",
        default=[],
        help="Input files (text, markdown, pdf, csv, etc.)",
    )
    parser.add_argument(
        "--instructions",
        "-m",
        type=str,
        default=None,
        help="Additional guidance for the agent.",
    )
    parser.add_argument(
        "--duration",
        "-d",
        type=int,
        default=None,
        help="Estimated presentation duration in minutes (1 slide per minute heuristic).",
    )
    parser.add_argument(
        "--style",
        "-s",
        action="append",
        default=[],
        help="Style overrides key=value (e.g., palette=dark).",
    )
    parser.add_argument(
        "--use-llm",
        action="store_true",
        help="Enable LLM-assisted analysis (Gemini; requires GEMINI_API_KEY).",
    )
    parser.add_argument(
        "--llm-model",
        type=str,
        default=None,
        help="LLM model name (default gemini-1.5-flash).",
    )
    parser.add_argument(
        "--llm-provider",
        type=str,
        default="gemini",
        help="LLM provider (currently gemini).",
    )
    parser.add_argument(
        "--image-endpoint",
        type=str,
        default=None,
        help="ComfyUI base URL for image generation (optional).",
    )
    parser.add_argument(
        "--image-backend",
        type=str,
        default="comfy",
        choices=["comfy", "gemini"],
        help="Image generation backend: comfy (local) or gemini (Google).",
    )
    parser.add_argument(
        "--assets-dir",
        type=Path,
        default=Path("assets"),
        help="Directory to store generated assets.",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("output/presentation.pptx"),
        help="Target PPTX output path.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    style_overrides = _parse_style_overrides(args.style)
    resolved_inputs, missing_inputs = _expand_inputs(args.input)

    if missing_inputs:
        missing_list = ", ".join(str(p) for p in missing_inputs)
        parser.error(f"Input file(s) not found: {missing_list}")
    if not resolved_inputs:
        parser.error("At least one --input file is required.")

    request = PresentationRequest(
        inputs=resolved_inputs,
        instructions=args.instructions,
        duration_minutes=args.duration,
        style_prefs=style_overrides,
        output_path=args.output.expanduser(),
        use_llm=args.use_llm,
        llm_provider=args.llm_provider,
        llm_model=args.llm_model,
        image_endpoint=args.image_endpoint,
        image_backend=args.image_backend,
        assets_dir=args.assets_dir.expanduser(),
    )
    result = run_pipeline(request)
    print(f"Slides planned: {result.slides_built}")
    print(f"Preview generated at: {result.preview_path}")
    print(f"Requested PPTX path: {result.requested_output}")
    print(result.notes)


if __name__ == "__main__":
    main()
