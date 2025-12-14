from __future__ import annotations

"""Outline generation heuristics."""

from typing import Optional

from .models import ContentSummary, OutlinePlan, OutlineSlide


def generate_outline(
    summary: ContentSummary,
    duration_minutes: Optional[int],
    style_prefs: Optional[dict[str, str]] = None,
    llm_client=None,
    use_llm: bool = False,
) -> OutlinePlan:
    """Create a minimal slide outline using the 1-minute rule and single-concept guidance."""
    target_count = _estimate_slide_count(summary, duration_minutes)
    slides: list[OutlineSlide] = []

    primary_topics = summary.topics[:target_count] or ["Overview"]
    for idx in range(target_count):
        topic = primary_topics[idx % len(primary_topics)]
        title = f"{topic}: key takeaway"
        bullets = _build_bullets(summary, topic)
        if llm_client and use_llm:
            refined = _refine_with_llm(llm_client, title, bullets)
            if refined:
                bullets = refined
        visual = _pick_visual(summary)
        slides.append(
            OutlineSlide(
                title=title,
                bullets=bullets,
                visual_suggestion=visual,
                sources=summary.sources,
            )
        )

    theme = _build_theme(style_prefs or {})
    return OutlinePlan(slides=slides, theme=theme)


def _estimate_slide_count(summary: ContentSummary, duration_minutes: Optional[int]) -> int:
    """Estimate slide count using the 1-minute rule and fallback heuristics."""
    if duration_minutes and duration_minutes > 0:
        return max(duration_minutes, 1)
    complexity = max(len(summary.findings), len(summary.topics), 1)
    return min(max(complexity, 3), 12)


def _build_bullets(summary: ContentSummary, topic: str) -> list[str]:
    """Create short bullets respecting the 3–5 item guideline."""
    candidates = summary.findings or [f"Highlight main point for {topic}"]
    trimmed = [text[:120] for text in candidates]
    return trimmed[:5]


def _pick_visual(summary: ContentSummary) -> str:
    """Choose a visual suggestion based on available data."""
    if summary.data_points:
        return "chart"
    return "image"


def _build_theme(style_prefs: dict[str, str]) -> dict[str, str]:
    """Assemble a theme from defaults plus style overrides."""
    base = {
        "ratio": "16:9",
        "font": "Segoe UI",
        "palette": "high-contrast",
    }
    base.update(style_prefs)
    return base


def _refine_with_llm(llm_client, title: str, bullets: list[str]) -> list[str]:
    """Ask LLM to tighten bullets; fallback to existing bullets on any failure."""
    prompt = (
        "Rewrite these slide bullets to be concise (<=12 words each), 3-5 bullets max.\n"
        f"Title: {title}\nBullets:\n- " + "\n- ".join(bullets)
    )
    try:
        text = llm_client.generate(prompt)
    except Exception:
        return bullets
    if not text:
        return bullets
    lines = [line.strip("- ").strip() for line in text.splitlines() if line.strip()]
    cleaned = [line for line in lines if line][:5]
    return cleaned or bullets
