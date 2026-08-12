from __future__ import annotations

from pathlib import Path

import tomllib

from typer.testing import CliRunner

from deeptutor.api.main import app as api_app
from deeptutor.runtime.env import get_prefixed_env
from deeptutor_cli.main import app as cli_app
import deeptutor_cli.compat as compat_cli


ROOT = Path(__file__).resolve().parents[2]


def test_distribution_and_cli_brand_are_nexatutor() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]

    assert project["name"] == "nexatutor"
    assert project["scripts"]["nexatutor"] == "deeptutor_cli.main:main"
    assert project["scripts"]["deeptutor"] == "deeptutor_cli.compat:main"
    assert cli_app.info.name == "nexatutor"
    assert "NexaTutor" in (cli_app.info.help or "")


def test_cli_help_and_openapi_have_no_visible_old_brand() -> None:
    result = CliRunner().invoke(cli_app, ["--help"])

    assert result.exit_code == 0
    assert "NexaTutor" in result.stdout
    assert "DeepTutor" not in result.stdout
    assert api_app.title == "NexaTutor API"


def test_frontend_package_metadata_is_nexatutor() -> None:
    package = __import__("json").loads((ROOT / "web" / "package.json").read_text(encoding="utf-8"))

    assert package["name"] == "nexatutor-web"


def test_compose_uses_nexatutor_service_and_image() -> None:
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    ghcr = (ROOT / "docker-compose.ghcr.yml").read_text(encoding="utf-8")

    assert "  nexatutor:" in compose
    assert "container_name: nexatutor" in compose
    assert "ghcr.io/thc-1/nexatutor:latest" in ghcr.lower()
    assert "  deeptutor:" not in compose


def test_data_root_is_not_renamed_or_migrated() -> None:
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")

    assert "./data:/app/data" in compose


def test_new_environment_prefix_wins_with_legacy_fallback(monkeypatch) -> None:
    monkeypatch.setenv("DEEPTUTOR_EXAMPLE", "legacy")
    assert get_prefixed_env("EXAMPLE") == "legacy"

    monkeypatch.setenv("NEXATUTOR_EXAMPLE", "current")
    assert get_prefixed_env("EXAMPLE") == "current"


def test_legacy_cli_warns_and_forwards(monkeypatch, capsys) -> None:
    calls: list[bool] = []
    monkeypatch.setattr(compat_cli, "nexatutor_main", lambda: calls.append(True))

    compat_cli.main()

    assert calls == [True]
    assert "deprecated" in capsys.readouterr().err
