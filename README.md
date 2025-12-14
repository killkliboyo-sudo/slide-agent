# Auto Presentation Agent

Python scaffold for the automated slide-generation agent described in `SPEC.md`. The current layout is intentionally minimal and ready for iterative development. The pipeline produces a PPTX plus a markdown preview for quick inspection.

## Getting Started

1. Use Python 3.10+ and create a virtual environment: `python -m venv .venv && source .venv/bin/activate`.
2. Install in editable mode: `pip install -e .`
3. Run the CLI: `auto-presentation-agent --input sample.txt --instructions "Focus on results"`
4. Find the PPTX at `output/presentation.pptx` and a preview markdown file alongside it.
5. Optional: pass style overrides (e.g., `--style font=Inter --style palette=dark`) to influence theme choices.
6. Optional LLM and image gen: `--use-llm --llm-provider gemini --llm-model gemini-1.5-pro-latest` (requires `GEMINI_API_KEY`); `--image-backend gemini --image-model gemini-1.5-flash-latest` uses the same key for images, or `--image-backend comfy --image-endpoint http://localhost:8188` for ComfyUI. Assets save to `--assets-dir` (default `assets/`).
7. List available Gemini models: `GEMINI_API_KEY=... auto-presentation-agent --list-gemini-models`.

## Project Layout

- `SPEC.md` – high-level product specification and design principles.
- `pyproject.toml` – packaging metadata and CLI entry point.
- `src/auto_presentation_agent/models.py` – dataclasses for pipeline data.
- `src/auto_presentation_agent/data_analysis.py` – stub analyzer.
- `src/auto_presentation_agent/outline.py` – outline generator using the 1-minute rule.
- `src/auto_presentation_agent/designer.py` – slide draft creator with layout hints.
- `src/auto_presentation_agent/assembler.py` – writes PPTX slides and a markdown preview.
- `src/auto_presentation_agent/pipeline.py` – pipeline orchestration.
- `src/auto_presentation_agent/main.py` – CLI entry point.
- `docs/implementation.md` – implementation plan aligned to `SPEC.md`.
- `docs/progress.md` – chronological work log.

## Testing

- Run `python -m unittest discover -v tests`. The PPTX smoke test now runs when `python-pptx` is installed.
- The PPTX smoke test asserts that theme overrides (font, palette) flow through to the rendered file.
- PDF analysis is optional; if `pdfplumber` is not installed, a warning is emitted instead of extraction.
- LLM/Image pathways are covered via mocks; no network calls occur during tests. ComfyUI workflow retrieval is not exercised yet.

## Next Steps

- Translate the specification into richer modules (analysis, outline generation, slide design, assembler).
- Add optional adapters (LLM/image generation) when ready.
- Expand test coverage, including golden-file previews and PDF export validation when added.
