from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class PresentationRequest:
    """User request passed into the agent pipeline."""

    inputs: list[Path] = field(default_factory=list)
    instructions: Optional[str] = None
    duration_minutes: Optional[int] = None
    style_prefs: dict[str, str] = field(default_factory=dict)
    output_path: Path = Path("output/presentation.pptx")
    use_llm: bool = False
    llm_provider: Optional[str] = "gemini"
    llm_model: Optional[str] = None
    image_endpoint: Optional[str] = None
    image_backend: str = "comfy"  # comfy | gemini
    assets_dir: Path = Path("assets")


@dataclass
class ContentSummary:
    """Structured understanding of the inputs."""

    topics: list[str] = field(default_factory=list)
    findings: list[str] = field(default_factory=list)
    data_points: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)


@dataclass
class OutlineSlide:
    """Single slide plan with title-as-conclusion."""

    title: str
    bullets: list[str] = field(default_factory=list)
    visual_suggestion: Optional[str] = None
    sources: list[str] = field(default_factory=list)


@dataclass
class OutlinePlan:
    """Slide deck outline."""

    slides: list[OutlineSlide] = field(default_factory=list)
    theme: dict[str, str] = field(default_factory=dict)


@dataclass
class AssetSpec:
    """Representation of a visual asset to be generated or embedded."""

    type: str  # chart | image | background
    path: Optional[Path] = None
    prompt: Optional[str] = None
    data_ref: Optional[str] = None


@dataclass
class SlideDraft:
    """Designed slide ready for assembly."""

    title: str
    bullets: list[str] = field(default_factory=list)
    layout: str = "split"  # split | stacked | focus
    assets: list[AssetSpec] = field(default_factory=list)
    notes: Optional[str] = None
    sources: list[str] = field(default_factory=list)


@dataclass
class AssemblyResult:
    """Outcome of the assembler stage."""

    requested_output: Path
    preview_path: Path
    slides_built: int
    notes: str
