"""Repository contracts preventing publication under upstream identities."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RELEASE_WORKFLOWS = (
    ROOT / ".github" / "workflows" / "pypi-release.yml",
    ROOT / ".github" / "workflows" / "docker-release.yml",
)


def test_upstream_release_workflows_are_paused() -> None:
    for workflow in RELEASE_WORKFLOWS:
        text = workflow.read_text(encoding="utf-8")

        assert "\n  release:" not in text, workflow
        assert "workflow_dispatch:" in text, workflow
        assert "if: ${{ false }}" in text, workflow
