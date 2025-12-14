# Auto Presentation Agent

Python scaffold for the automated slide-generation agent described in `SPEC.md`. The current layout is intentionally minimal and ready for iterative development. A textual preview is generated today; PPTX rendering will follow.

## Getting Started

1. Use Python 3.10+ and create a virtual environment: `python -m venv .venv && source .venv/bin/activate`.
2. Install in editable mode: `pip install -e .`
3. Run the CLI: `auto-presentation-agent --input sample.txt --instructions "Focus on results"`
4. Find the preview at `output/presentation.md` (currently emitted in place of PPTX).

## Project Layout

- `SPEC.md` – high-level product specification and design principles.
- `pyproject.toml` – packaging metadata and CLI entry point.
- `src/auto_presentation_agent/models.py` – dataclasses for pipeline data.
- `src/auto_presentation_agent/data_analysis.py` – stub analyzer.
- `src/auto_presentation_agent/outline.py` – outline generator using the 1-minute rule.
- `src/auto_presentation_agent/designer.py` – slide draft creator with layout hints.
- `src/auto_presentation_agent/assembler.py` – writes markdown preview (PPTX TBD).
- `src/auto_presentation_agent/pipeline.py` – pipeline orchestration.
- `src/auto_presentation_agent/main.py` – CLI entry point.
- `docs/implementation.md` – implementation plan aligned to `SPEC.md`.
- `docs/progress.md` – chronological work log.

## Next Steps

- Translate the specification into concrete modules (data analysis, outline generation, slide design, and assembler).
- Add dependencies (e.g., `python-pptx`, NLP/LLM tooling) as implementation details solidify.
- Implement tests for each agent module once behavior is defined.
- Replace markdown preview with real PPTX assembly and add PDF export if needed.
