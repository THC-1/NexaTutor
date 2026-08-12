"""Packaging contracts for the removed Partner channel stack."""

from __future__ import annotations

from pathlib import Path
import tomllib


ROOT = Path(__file__).resolve().parents[1]


def test_partner_and_matrix_extras_are_absent() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    extras = project["optional-dependencies"]

    assert "partners" not in extras
    assert "tutorbot" not in extras
    assert "matrix" not in extras
    assert "matrix-e2e" not in extras
    assert all("deeptutor[partners]" not in item for item in extras["all"])


def test_partner_requirement_files_are_absent() -> None:
    for name in ("partners.txt", "matrix.txt", "matrix-e2e.txt"):
        assert not (ROOT / "requirements" / name).exists()

    root_requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    assert "requirements/partners.txt" not in root_requirements
