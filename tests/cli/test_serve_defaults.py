"""Safety contracts for the standalone API server command."""

from __future__ import annotations

import inspect

from typer.models import OptionInfo
from typer.testing import CliRunner

from deeptutor_cli.main import app, serve


def test_serve_defaults_to_ipv4_loopback() -> None:
    host_option = inspect.signature(serve).parameters["host"].default

    assert isinstance(host_option, OptionInfo)
    assert host_option.default == "127.0.0.1"


def test_serve_passes_default_and_explicit_host_to_uvicorn(monkeypatch) -> None:
    import uvicorn

    calls: list[dict[str, object]] = []
    monkeypatch.setattr(uvicorn, "run", lambda *args, **kwargs: calls.append(kwargs))
    runner = CliRunner()

    default_result = runner.invoke(app, ["serve", "--port", "8765"])
    public_result = runner.invoke(
        app, ["serve", "--host", "0.0.0.0", "--port", "8766"]
    )

    assert default_result.exit_code == 0, default_result.output
    assert public_result.exit_code == 0, public_result.output
    assert [call["host"] for call in calls] == ["127.0.0.1", "0.0.0.0"]
