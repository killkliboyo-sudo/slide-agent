from __future__ import annotations

"""Assembler renders a minimal PPTX and companion markdown preview."""

from pathlib import Path
from typing import Optional

from pptx import Presentation
from pptx.enum.text import MSO_ANCHOR
from pptx.util import Inches, Pt

from .models import AssemblyResult, AssetSpec, SlideDraft


def assemble(slides: list[SlideDraft], requested_output: Path, theme: Optional[dict[str, str]] = None) -> AssemblyResult:
    """Render the slide drafts into a PPTX and a lightweight markdown preview."""
    requested_output = requested_output.expanduser()
    requested_output.parent.mkdir(parents=True, exist_ok=True)

    presentation = _build_presentation(slides, theme or {})
    presentation.save(requested_output)

    preview_path = requested_output.with_suffix(".md")
    preview_path.write_text(_render_preview(slides), encoding="utf-8")

    notes = (
        "Generated PPTX with simple title/body layouts; markdown preview emitted "
        "for quick inspection."
    )
    return AssemblyResult(
        requested_output=requested_output,
        preview_path=preview_path,
        slides_built=len(slides),
        notes=notes,
    )


def _build_presentation(slides: list[SlideDraft], theme: dict[str, str]) -> Presentation:
    """Create a presentation with 16:9 ratio and basic styling."""
    prs = Presentation()
    prs.slide_width = Inches(13.33)
    prs.slide_height = Inches(7.5)
    font_name = theme.get("font", "Segoe UI")

    for slide in slides:
        _add_slide(prs, slide, font_name)
    return prs


def _add_slide(prs: Presentation, slide: SlideDraft, font_name: str) -> None:
    """Add a single slide honoring the requested layout when possible."""
    layout = prs.slide_layouts[6]  # blank layout
    ppt_slide = prs.slides.add_slide(layout)

    margin = Inches(0.6)
    body_top = margin + Inches(1.0)
    body_height = prs.slide_height - body_top - Inches(1.2)
    body_width = prs.slide_width - (margin * 2)
    gap = Inches(0.4)

    _add_title(ppt_slide, slide.title, margin, margin, body_width, font_name)

    if slide.layout == "split":
        text_width = (body_width - gap) * 0.55
        _add_bullets_box(
            ppt_slide,
            slide.bullets,
            left=margin,
            top=body_top,
            width=text_width,
            height=body_height,
            font_name=font_name,
        )
        _add_asset_placeholder(
            ppt_slide,
            slide.assets,
            left=margin + text_width + gap,
            top=body_top,
            width=body_width - text_width - gap,
            height=body_height,
            font_name=font_name,
        )
    elif slide.layout == "stacked":
        _add_bullets_box(
            ppt_slide,
            slide.bullets,
            left=margin,
            top=body_top,
            width=body_width,
            height=body_height * 0.55,
            font_name=font_name,
        )
        _add_asset_placeholder(
            ppt_slide,
            slide.assets,
            left=margin,
            top=body_top + body_height * 0.6,
            width=body_width,
            height=body_height * 0.35,
            font_name=font_name,
        )
    else:  # focus
        _add_bullets_box(
            ppt_slide,
            slide.bullets,
            left=margin,
            top=body_top + Inches(0.4),
            width=body_width,
            height=body_height * 0.8,
            emphasize=True,
            font_name=font_name,
        )

    _add_footer(ppt_slide, slide.sources, slide.notes or "", font_name)


def _add_title(slide, title: str, left, top, width, font_name: str) -> None:
    box = slide.shapes.add_textbox(left, top, width, Inches(1.0))
    frame = box.text_frame
    frame.text = title
    para = frame.paragraphs[0]
    para.font.size = Pt(32)
    para.font.bold = True
    para.font.name = font_name


def _add_bullets_box(
    slide, bullets: list[str], left, top, width, height, emphasize: bool = False, font_name: str = "Segoe UI"
) -> None:
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    for idx, bullet in enumerate(bullets or ["Highlight key message"]):
        paragraph = tf.add_paragraph()
        if idx == 0:
            paragraph.level = 0
        paragraph.text = bullet
        paragraph.font.size = Pt(24 if emphasize else 22)
        paragraph.font.name = font_name
    if emphasize:
        for paragraph in tf.paragraphs:
            paragraph.font.bold = True


def _add_asset_placeholder(slide, assets: list[AssetSpec], left, top, width, height, font_name: str) -> None:
    if not assets:
        return
    asset = assets[0]
    if asset.path and asset.path.exists():
        try:
            slide.shapes.add_picture(str(asset.path), left, top, width=width, height=height)
            return
        except Exception:
            pass

    box = slide.shapes.add_textbox(left, top, width, height)
    frame = box.text_frame
    frame.word_wrap = True
    frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    description = asset.prompt or f"{asset.type} placeholder"
    frame.text = description
    frame.paragraphs[0].font.size = Pt(18)
    frame.paragraphs[0].font.name = font_name
    frame.paragraphs[0].font.italic = True


def _add_footer(slide, sources: list[str], note: str, font_name: str) -> None:
    footer = slide.shapes.add_textbox(
        Inches(0.6),
        slide.part.slide_height - Inches(0.8),
        slide.part.slide_width - Inches(1.2),
        Inches(0.6),
    )
    frame = footer.text_frame
    frame.clear()
    if sources:
        src_para = frame.add_paragraph()
        src_para.text = f"Sources: {', '.join(sources)}"
        src_para.font.size = Pt(12)
        src_para.font.name = font_name
    if note:
        note_para = frame.add_paragraph()
        note_para.text = note
        note_para.font.size = Pt(12)
        note_para.font.name = font_name


def _render_preview(slides: list[SlideDraft]) -> str:
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
        if slide.notes:
            lines.append(f"_Notes_: {slide.notes}")
        lines.append("")
    return "\n".join(lines)
