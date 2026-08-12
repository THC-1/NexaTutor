"""PocketBase SDK must not remain in install metadata."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_pocketbase_dependency_is_absent() -> None:
    files = [ROOT / "pyproject.toml", *sorted((ROOT / "requirements").glob("*.txt"))]
    offenders = [
        path.relative_to(ROOT).as_posix()
        for path in files
        if "pocketbase" in path.read_text(encoding="utf-8").lower()
    ]
    assert offenders == []
