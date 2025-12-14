from __future__ import annotations

"""Pipeline orchestration for the agent."""

import logging
from time import perf_counter

from .assembler import assemble
from .data_analysis import analyze_request
from .designer import design_slides
from .models import AssemblyResult, PresentationRequest
from .outline import generate_outline

logger = logging.getLogger(__name__)


def _run_stage(stage: str, func, *args, **kwargs):
    """Log stage boundaries and timing for pipeline steps."""
    logger.info("Starting %s", stage)
    started = perf_counter()
    result = func(*args, **kwargs)
    elapsed = perf_counter() - started
    logger.info("Finished %s in %.2fs", stage, elapsed)
    return result


def run_pipeline(request: PresentationRequest) -> AssemblyResult:
    """Run the end-to-end pipeline using placeholder implementations."""
    summary = _run_stage("analysis", analyze_request, request)
    outline = _run_stage("outline", generate_outline, summary, request.duration_minutes)
    drafts = _run_stage("design", design_slides, outline)
    result = _run_stage("assembly", assemble, drafts, requested_output=request.output_path)
    return result
