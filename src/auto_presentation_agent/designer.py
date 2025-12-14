from __future__ import annotations

"""Slide designer stub: shapes slide drafts from outlines."""

from itertools import cycle

from .models import AssetSpec, OutlinePlan, SlideDraft


def design_slides(outline: OutlinePlan) -> list[SlideDraft]:
    """Convert outline slides into designed drafts with layout hints and asset placeholders."""
    layouts = cycle(["split", "stacked", "focus"])
    drafts: list[SlideDraft] = []

    for slide in outline.slides:
        layout = next(layouts)
        assets: list[AssetSpec] = []
        if slide.visual_suggestion:
            assets.append(AssetSpec(type=slide.visual_suggestion, prompt=f"Visual for {slide.title}"))

        drafts.append(
            SlideDraft(
                title=_title_as_conclusion(slide.title),
                bullets=slide.bullets[:6],
                layout=layout,
                assets=assets,
                notes="Drafted per SPEC guidelines.",
                sources=slide.sources,
            )
        )
    return drafts


def _title_as_conclusion(title: str) -> str:
    """Ensure the slide title reads as a conclusion."""
    if ":" in title:
        return title.split(":", 1)[1].strip()
    return title
