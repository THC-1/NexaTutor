from __future__ import annotations

from pathlib import Path
import tomllib


ROOT = Path(__file__).resolve().parents[1]


def test_account_auth_dependencies_are_absent() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    groups = [
        project["project"]["dependencies"],
        project["project"]["optional-dependencies"]["server"],
    ]
    for dependencies in groups:
        normalized = "\n".join(dependencies).lower()
        assert "bcrypt" not in normalized
        assert "python-jose" not in normalized

    requirements = (ROOT / "requirements" / "server.txt").read_text(encoding="utf-8").lower()
    assert "bcrypt" not in requirements
    assert "python-jose" not in requirements
    assert "python-multipart" in requirements
    assert "oauth-cli-kit" not in "\n".join(project["project"]["dependencies"]).lower()
    assert (ROOT / "deeptutor" / "services" / "codex_auth" / "service.py").is_file()
