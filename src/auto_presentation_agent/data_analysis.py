from __future__ import annotations

"""Lightweight data analysis placeholder for the agent pipeline."""

from pathlib import Path

from .models import ContentSummary, PresentationRequest


def analyze_request(request: PresentationRequest) -> ContentSummary:
    """
    Parse inputs and extract a coarse summary.

    Current stub infers topics from filenames and echoes instructions.
    """
    topics = [path.stem for path in request.inputs] or ["General overview"]
    findings: list[str] = []
    data_points: list[str] = []
    sources: list[str] = []

    if request.instructions:
        findings.append(f"User focus: {request.instructions}")

    for path in request.inputs:
        _capture_basic_file_metadata(path, findings, sources)

    return ContentSummary(
        topics=topics,
        findings=findings or ["Summarize key points and visuals per SPEC.md."],
        data_points=data_points,
        sources=sources,
    )


def _capture_basic_file_metadata(path: Path, findings: list[str], sources: list[str]) -> None:
    """Record lightweight metadata to carry provenance forward."""
    if not path.exists():
        findings.append(f"Missing input noted: {path}")
        return
    findings.append(f"Detected input file: {path.name}")
    sources.append(str(path))
