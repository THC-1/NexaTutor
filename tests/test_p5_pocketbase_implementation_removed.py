"""P5 guardrails for deleted PocketBase implementation modules."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_pocketbase_backend_modules_and_setup_script_are_absent() -> None:
    assert importlib.util.find_spec("deeptutor.services.pocketbase_client") is None
    assert importlib.util.find_spec("deeptutor.services.session.pocketbase_store") is None
    assert not (ROOT / "scripts" / "pb_setup.py").exists()


def test_production_python_has_no_pocketbase_reference() -> None:
    offenders: list[str] = []
    for root in (ROOT / "deeptutor", ROOT / "deeptutor_cli"):
        for path in root.rglob("*.py"):
            if "pocketbase" in path.read_text(encoding="utf-8", errors="ignore").lower():
                offenders.append(path.relative_to(ROOT).as_posix())
    assert offenders == []
