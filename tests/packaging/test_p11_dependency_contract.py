from __future__ import annotations

from pathlib import Path

import tomllib


ROOT = Path(__file__).resolve().parents[2]


def _dependency_names(path: Path) -> set[str]:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    dependencies = data["project"]["dependencies"]
    return {item.split("[", 1)[0].split("<", 1)[0].split(">", 1)[0].split("=", 1)[0].lower() for item in dependencies}


def test_cli_distribution_has_no_removed_async_loop_shim() -> None:
    dependencies = _dependency_names(ROOT / "packaging" / "deeptutor-cli" / "pyproject.toml")

    assert "nest_asyncio" not in dependencies


def test_cli_distribution_keeps_local_agent_terminal_emulator() -> None:
    dependencies = _dependency_names(ROOT / "packaging" / "deeptutor-cli" / "pyproject.toml")

    assert "pyte" in dependencies


def test_cli_requirements_keep_local_agent_terminal_emulator() -> None:
    requirements = (ROOT / "requirements" / "cli.txt").read_text(encoding="utf-8").lower()

    assert "pyte>=0.8.1" in requirements
