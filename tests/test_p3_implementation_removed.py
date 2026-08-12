from __future__ import annotations

import importlib.util

from typer.testing import CliRunner

from deeptutor.api.main import app
from deeptutor_cli.main import app as cli_app


def test_extension_implementation_packages_are_absent() -> None:
    for module in (
        "deeptutor.services.mcp",
        "deeptutor.services.cli_apps",
        "deeptutor.runtime.providers",
        "deeptutor.runtime.registry.deferred_tools",
        "deeptutor.services.skill.hub",
    ):
        assert importlib.util.find_spec(module) is None


def test_extension_routes_are_absent() -> None:
    paths = {route.path for route in app.routes}
    assert not any("mcp" in path.lower() for path in paths)
    assert not any("cli-app" in path.lower() for path in paths)
    assert not any("plugin" in path.lower() for path in paths)
    assert not any("/hub/" in path.lower() for path in paths)
    assert "/api/v1/skills/install" not in paths


def test_cli_keeps_local_skills_but_has_no_market_commands() -> None:
    root_help = CliRunner().invoke(cli_app, ["--help"])
    assert root_help.exit_code == 0
    assert "plugin" not in root_help.stdout.lower()

    skill_help = CliRunner().invoke(cli_app, ["skill", "--help"])
    assert skill_help.exit_code == 0
    for command in ("search", "install", "login", "logout", "publish", "update"):
        assert command not in skill_help.stdout.lower()
    assert "list" in skill_help.stdout.lower()
    assert "remove" in skill_help.stdout.lower()
