"""PocketBase must not have a user-facing Web surface."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_web_ui_has_no_pocketbase_surface() -> None:
    roots = [
        ROOT / "web" / "app",
        ROOT / "web" / "components",
        ROOT / "web" / "locales",
    ]
    files = [ROOT / "web" / "lib" / "settings-nav.ts"]
    for root in roots:
        files.extend(path for path in root.rglob("*") if path.is_file())

    offenders = [
        path.relative_to(ROOT).as_posix()
        for path in files
        if "pocketbase" in path.read_text(encoding="utf-8", errors="ignore").lower()
    ]
    assert offenders == []
