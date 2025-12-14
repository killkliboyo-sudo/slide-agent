from __future__ import annotations

"""Entry point for the automated slide-generation agent scaffold."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class PresentationRequest:
    """Data passed into the agent system."""

    inputs: list[Path]
    instructions: Optional[str] = None


def plan_presentation(request: PresentationRequest) -> str:
    """Placeholder planner that echoes the request context."""
    input_list = "\n".join(f"- {path}" for path in request.inputs) or "- (no inputs provided)"
    instructions = request.instructions or "(no additional instructions)"
    return (
        "Auto Presentation Agent scaffold\n"
        f"Inputs:\n{input_list}\n"
        f"Instructions: {instructions}\n"
        "Refer to SPEC.md to implement the full multi-agent pipeline."
    )


def main() -> None:
    """CLI stub to prove the project wiring works."""
    request = PresentationRequest(inputs=[], instructions=None)
    print(plan_presentation(request))


if __name__ == "__main__":
    main()
