from __future__ import annotations

"""Assembler stub writes a human-readable preview."""

from pathlib import Path

from .models import AssemblyResult, SlideDraft


def assemble(slides: list[SlideDraft], requested_output: Path) -> AssemblyResult:
    """
    Create a textual preview of the deck.

    Future work will render PPTX via python-pptx; for now we emit a markdown plan
    so the pipeline has a tangible artifact.
    """
    requested_output = requested_output.expanduser()
    requested_output.parent.mkdir(parents=True, exist_ok=True)
    preview_path = requested_output.with_suffix(".md")

    lines = ["# Auto Presentation Agent Preview", ""]
    for idx, slide in enumerate(slides, start=1):
        lines.append(f"## Slide {idx}: {slide.title}")
        for bullet in slide.bullets:
            lines.append(f"- {bullet}")
        if slide.assets:
            assets = ", ".join(asset.type for asset in slide.assets)
            lines.append(f"_Assets_: {assets}")
        if slide.sources:
            lines.append(f"_Sources_: {', '.join(slide.sources)}")
        lines.append("")

    preview_path.write_text("\n".join(lines), encoding="utf-8")
    return AssemblyResult(
        requested_output=requested_output,
        preview_path=preview_path,
        slides_built=len(slides),
        notes="Generated markdown preview; PPTX output to be implemented.",
    )
