# Implementation Plan: Auto Presentation Agent

This document translates `SPEC.md` into an actionable architecture and roadmap for the Python implementation.

## Goals
- Automate end-to-end slide generation from heterogeneous inputs (reports, tables, PDFs, text) plus user instructions.
- Enforce presentation design principles (single concept per slide, title-as-conclusion, controlled element count, high-contrast styling).
- Produce a PPTX (and optionally PDF) output with consistent visual style.

## System Architecture
- CLI entry (`auto-presentation-agent`) drives a pipeline of four cooperating modules:
  1) **Data Analysis Agent** – parses inputs, extracts key concepts/data, produces structured summary.
  2) **Outline Generator** – plans slide count, per-slide titles (conclusion-style), bullet points, and visual needs.
  3) **Slide Designer** – drafts per-slide text, selects/creates visuals, and proposes layout/style tokens.
  4) **Presentation Assembler** – renders PPTX using the layout/style instructions and assets.
- Shared models: `PresentationRequest`, `ContentSummary`, `OutlinePlan`, `SlideDraft`, `AssetSpec`, `AssemblyPlan`.
- Assets (generated charts/images) saved under `assets/` and referenced by draft/assembly plans.

## Module Responsibilities
- **Data Analysis Agent**
  - Input: `PresentationRequest` (file paths, instructions).
  - Output: `ContentSummary` with topics, key findings, supporting data refs, and source provenance.
  - Implementation: detectors for file types (text/markdown/pdf via pluggable readers), keyword/key-phrase extraction, simple statistics for tables (CSV/XLSX), and optional LLM summarization (Gemini; off by default until configured).
- **Outline Generator**
  - Input: `ContentSummary`, optional target duration.
  - Output: `OutlinePlan` (slides with title-as-conclusion, bullet list 3–5 items, suggested chart/image types, estimated slide count via 1-minute rule).
  - Implementation: heuristic page estimator, rule-based title rewriting, mapping data points to chart suggestions.
- **Slide Designer**
  - Input: `OutlinePlan`, style guide defaults (16:9, high contrast, sans-serif).
  - Output: list of `SlideDraft` items containing text blocks, asset specs (charts/images), and layout tokens (left/right/stack).
  - Implementation: text condensing to short bullets, matplotlib chart generation from sample/provided data, ComfyUI hook for image generation (optional; placeholder fallback when unavailable), Gemini image backend (banana pro) using the same API key when enabled; default models `gemini-1.5-pro-latest` (text) and `gemini-1.5-flash-latest` (image).
- **Presentation Assembler**
  - Input: `SlideDraft` list and assets.
  - Output: `output/presentation.pptx` (and optional PDF export).
  - Implementation: `python-pptx` for slide creation, layout application, font/color theme enforcement, footer/source annotations.

## Detailed behavior for v0
- **Data Analysis**: detect input type by suffix/MIME; text/markdown read with UTF-8 fallback; CSV/XLSX parsed via pandas; PDFs stubbed until adapter added. Normalize extracted text into short paragraphs, collect numeric columns to allow quick charts, and carry absolute file paths in `sources`. Programmatic callers may pass missing files which become findings with a warning; the CLI blocks missing paths earlier.
- **Outline Generation**: slide count = `duration_minutes` if provided, else max(len(findings), len(topics), 3) capped at 12. Titles rewritten to conclusion form (`<topic>: <conclusion>` → `<conclusion>`). Bullets trimmed to <=120 chars, max 5 per slide. Visual suggestion chosen from `chart|image` based on presence of tabular data.
- **Slide Design**: cycle layouts (`split`, `stacked`, `focus`) and attach `AssetSpec` placeholders. Condense bullets to crisp statements; inject note hinting at SPEC principles (single concept, title-as-conclusion). Style tokens: ratio 16:9, sans-serif, high-contrast palette, optional `style_prefs` overrides (palette/font/background choice).
- **Assembly**: build PPTX with `python-pptx` (16:9), emit a markdown preview alongside. Apply theme tokens (font, palette) to title/body/footer, set background fill and accent bar. Assets resolved from `assets/` relative paths; non-existent assets skipped with a note.
- **CLI/Orchestration**: argparse entry validates at least one existing input (rejects missing paths), expands `~`, and passes `PresentationRequest` to `run_pipeline`. Logging prints stage boundaries and preview location with timings; non-zero exit on unhandled exceptions.

## Data Structures (initial draft)
- `PresentationRequest`: `inputs: list[Path]`, `instructions: str|None`, `duration_minutes: int|None`, `style_prefs: dict`.
- `ContentSummary`: `topics`, `findings`, `tables`, `sources`.
- `OutlinePlan`: `slides: list[OutlineSlide]`, `theme`.
- `SlideDraft`: `title`, `bullets`, `notes`, `layout`, `assets: list[AssetSpec]`, `sources`.
- `AssetSpec`: `type` (`chart|image|background`), `data_ref|prompt`, `path`.

## CLI and I/O
- CLI arguments: `--input PATH...`, `--instructions TEXT`, `--duration MIN`, `--style KEY=VALUE`, `--output PATH`.
- Outputs to `output/` by default, creating directories as needed.
- Logging to stdout/stderr with structured info for pipeline stages.

## Dependencies (planned)
- Core: `python-pptx`, `pandas` (for tabular parsing), `matplotlib` (charts), `pydantic` or `dataclasses` for models, `typer` or `argparse` for CLI.
- Optional: PDF/text parsers (`pdfplumber`, `pypdf`), `openpyxl` for XLSX, pluggable LLM/image gen adapters (kept stubbed until configured).

## Testing Strategy
- Unit tests per module with fixture inputs (text, CSV).
- Golden-file tests for outline generation and slide draft layout selection.
- Integration test: small end-to-end run producing a PPTX and verifying slide count and titles.

## Milestones
1) Define data models and CLI (no external deps).
2) Implement Outline Generator heuristics with mock data.
3) Add Slide Designer text condensing and chart stubs.
4) Integrate `python-pptx` assembler with simple theme. ✅
5) Wire data analysis readers for text/CSV and add provenance tracking. ✅
6) Add palette-aware theming and style overrides (font/palette) propagated to PPTX. ✅
7) Add optional adapters (PDF parsing, LLM/image generation).

## Upcoming tasks (working list)
- Harden CLI validation (missing files, empty inputs) and log stage timing.
- Flesh out pandas-based CSV/XLSX parsing with simple numeric summaries and chart suggestions.
- Replace markdown preview with basic python-pptx rendering (title/body, split layout, footer).
- Add fixture-driven tests for outline and designer heuristics plus an end-to-end smoke test.
