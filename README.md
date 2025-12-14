# Auto Presentation Agent

Python scaffold for the automated slide-generation agent described in `SPEC.md`. The current layout is intentionally minimal and ready for iterative development.

## Getting Started

1. Use Python 3.10+ and create a virtual environment: `python -m venv .venv && source .venv/bin/activate`.
2. Install in editable mode: `pip install -e .`
3. Run the placeholder entry point: `auto-presentation-agent`

## Project Layout

- `SPEC.md` – high-level product specification and design principles.
- `pyproject.toml` – packaging metadata and CLI entry point.
- `src/auto_presentation_agent/main.py` – starter CLI and pipeline placeholder.

## Next Steps

- Translate the specification into concrete modules (data analysis, outline generation, slide design, and assembler).
- Add dependencies (e.g., `python-pptx`, NLP/LLM tooling) as implementation details solidify.
- Implement tests for each agent module once behavior is defined.
