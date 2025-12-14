from __future__ import annotations

"""Lightweight data analysis placeholder for the agent pipeline."""

from pathlib import Path
from typing import Iterable, Tuple

from .models import ContentSummary, PresentationRequest

try:
    import pandas as pd  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    pd = None

def analyze_request(request: PresentationRequest) -> ContentSummary:
    """
    Parse inputs and extract a coarse summary.

    Reads text/markdown, parses CSV/XLSX (when pandas is available), and carries
    provenance for downstream slides.
    """
    topics: list[str] = []
    findings: list[str] = []
    data_points: list[str] = []
    sources: list[str] = []

    if request.instructions:
        findings.append(f"User focus: {request.instructions}")

    for path in request.inputs:
        _capture_basic_file_metadata(path, findings, sources)
        if not path.exists():
            continue
        topics.append(path.stem)
        suffix = path.suffix.lower()
        if suffix in {".txt", ".md", ".markdown"}:
            warnings, snippet = _read_text(path)
            findings.extend(warnings)
            if snippet:
                findings.append(f"Excerpt from {path.name}: {snippet}")
        elif suffix in {".csv", ".tsv", ".xlsx"}:
            table_findings, table_points = _summarize_table(path)
            findings.extend(table_findings)
            data_points.extend(table_points)
        else:
            findings.append(f"Unhandled file type noted: {path.name}")

    return ContentSummary(
        topics=topics or ["General overview"],
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
    sources.append(str(path.resolve()))


def _read_text(path: Path) -> Tuple[list[str], str]:
    """Read text/markdown with UTF-8 and return warnings plus a short excerpt."""
    warnings: list[str] = []
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as exc:  # pragma: no cover - filesystem dependent
        warnings.append(f"Unable to read {path.name}: {exc}")
        return warnings, ""
    paragraphs = [line.strip() for line in content.splitlines() if line.strip()]
    excerpt = " ".join(paragraphs[:3])
    return warnings, excerpt[:200]


def _summarize_table(path: Path) -> Tuple[list[str], list[str]]:
    """Parse CSV/XLSX and emit lightweight numeric summaries."""
    if pd is None:
        return [f"Table detected but pandas is not installed: {path.name}"], []

    findings: list[str] = []
    data_points: list[str] = []
    try:
        if path.suffix.lower() == ".csv":
            df = pd.read_csv(path)
        elif path.suffix.lower() == ".tsv":
            df = pd.read_csv(path, sep="\t")
        else:
            df = pd.read_excel(path)
    except Exception as exc:  # pragma: no cover - depends on file contents
        return [f"Failed to parse table {path.name}: {exc}"], []

    findings.append(f"Parsed table {path.name} with {df.shape[0]} rows x {df.shape[1]} cols")
    numeric = df.select_dtypes(include="number")
    if numeric.empty:
        findings.append(f"No numeric columns detected in {path.name}")
        return findings, data_points

    summary = numeric.describe().round(2)
    for col in list(numeric.columns)[:3]:
        stats = summary[col]
        data_points.append(f"{col}: mean {stats.get('mean')}, max {stats.get('max')}")
    return findings, data_points
