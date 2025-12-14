from __future__ import annotations

"""CLI entry for the automated slide-generation agent."""

import argparse
from pathlib import Path

from .models import PresentationRequest
from .pipeline import run_pipeline


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
    style_overrides = _parse_style_overrides(args.style)

    request = PresentationRequest(
        inputs=args.input,
        instructions=args.instructions,
        duration_minutes=args.duration,
        style_prefs=style_overrides,
        output_path=args.output,
    )
    result = run_pipeline(request)
    print(f"Slides planned: {result.slides_built}")
    print(f"Preview generated at: {result.preview_path}")
    print(f"Requested PPTX path: {result.requested_output}")
    print(result.notes)


if __name__ == "__main__":
    main()
