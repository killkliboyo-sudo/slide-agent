from __future__ import annotations

"""Pipeline orchestration for the agent."""

import logging
from time import perf_counter

from . import imagegen, llm
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
    llm_client = None
    if request.use_llm and (request.llm_provider or "").lower() == "gemini":
        llm_client = llm.build_gemini_from_env(model=request.llm_model)

    summary = _run_stage("analysis", analyze_request, request, llm_client)
    outline = _run_stage(
        "outline", generate_outline, summary, request.duration_minutes, request.style_prefs, llm_client, request.use_llm
    )

    def image_generator(prompt, assets_dir):
        return imagegen.generate_image(
            prompt,
            assets_dir,
            backend=request.image_backend,
            endpoint=request.image_endpoint,
            gemini_client=llm_client,
            gemini_image_model=request.llm_model,
        )

    drafts = _run_stage("design", design_slides, outline, image_generator, request.assets_dir)
    result = _run_stage("assembly", assemble, drafts, requested_output=request.output_path, theme=outline.theme)
    return result
