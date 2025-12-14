from __future__ import annotations

"""Pipeline orchestration for the agent."""

from .assembler import assemble
from .data_analysis import analyze_request
from .designer import design_slides
from .models import AssemblyResult, PresentationRequest
from .outline import generate_outline


def run_pipeline(request: PresentationRequest) -> AssemblyResult:
    """Run the end-to-end pipeline using placeholder implementations."""
    summary = analyze_request(request)
    outline = generate_outline(summary, duration_minutes=request.duration_minutes)
    drafts = design_slides(outline)
    result = assemble(drafts, requested_output=request.output_path)
    return result
