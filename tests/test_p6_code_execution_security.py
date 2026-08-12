from __future__ import annotations

import inspect

import pytest


def test_code_execution_is_explicit_opt_in_and_host_subprocess_defaults_off() -> None:
    from deeptutor.api.routers.settings import DEFAULT_UI_SETTINGS
    from deeptutor.services.config.runtime_settings import DEFAULT_SYSTEM_SETTINGS
    from deeptutor.tools.builtin import USER_TOGGLEABLE_TOOL_NAMES

    assert "code_execution" in USER_TOGGLEABLE_TOOL_NAMES
    assert "code_execution" not in DEFAULT_UI_SETTINGS["enabled_optional_tools"]
    assert DEFAULT_SYSTEM_SETTINGS["sandbox_allow_subprocess"] is False


@pytest.mark.asyncio
async def test_code_execution_is_python_only_and_uses_argv_without_shell(tmp_path, monkeypatch) -> None:
    from deeptutor.services.sandbox.spec import ExecResult, IsolationLevel
    from deeptutor.tools.builtin import CodeExecutionTool

    captured = {}

    class Sandbox:
        async def isolation_level(self):
            return IsolationLevel.SYSTEM

        async def run(self, request, *, user_id):
            captured["request"] = request
            return ExecResult(stdout="ok")

    import deeptutor.services.sandbox as sandbox

    monkeypatch.setattr(sandbox, "get_sandbox_service", lambda: Sandbox())
    tool = CodeExecutionTool()
    with pytest.raises(ValueError):
        await tool.execute(language="cpp", code="int main(){}", _sandbox_workdir=str(tmp_path))
    result = await tool.execute(language="python", code="print(1)", _sandbox_workdir=str(tmp_path))
    assert result.success
    request = captured["request"]
    assert request.argv[:2] == ("python3", "-I")
    assert request.command == "python3 -I main.py"


@pytest.mark.asyncio
async def test_code_execution_fails_closed_without_system_isolation(tmp_path, monkeypatch) -> None:
    from deeptutor.services.sandbox.spec import IsolationLevel
    from deeptutor.tools.builtin import CodeExecutionTool

    class Sandbox:
        async def isolation_level(self):
            return IsolationLevel.APPLICATION

    import deeptutor.services.sandbox as sandbox

    monkeypatch.setattr(sandbox, "get_sandbox_service", lambda: Sandbox())
    result = await CodeExecutionTool().execute(
        language="python", code="print(1)", _sandbox_workdir=str(tmp_path)
    )
    assert result.success is False
    assert "system-isolated" in result.content.lower()


def test_code_execution_does_not_build_shell_commands() -> None:
    from deeptutor.tools.builtin import CodeExecutionTool

    source = inspect.getsource(CodeExecutionTool)
    assert "command_template" not in source
    assert "stdin_redirect" not in source
    assert "ExecRequest.of_argv" in source


def test_code_execution_rejects_process_and_network_imports() -> None:
    from deeptutor.tools.builtin import CodeExecutionTool

    tool = CodeExecutionTool()
    with pytest.raises(ValueError, match="subprocess"):
        tool._validate_python("import subprocess\nsubprocess.run(['whoami'])")
    with pytest.raises(ValueError, match="os"):
        tool._validate_python("import os\nos.system('whoami')")
    with pytest.raises(ValueError, match="socket"):
        tool._validate_python("import socket")


@pytest.mark.asyncio
async def test_old_runner_without_argv_capability_fails_closed(monkeypatch) -> None:
    from deeptutor.services.sandbox.backends import RunnerSidecarBackend

    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {"status": "ok"}

    class Client:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def get(self, _url):
            return Response()

    import deeptutor.services.sandbox.backends as backends

    monkeypatch.setattr(backends.httpx, "AsyncClient", lambda **_kwargs: Client())
    healthy, detail = await RunnerSidecarBackend("http://old-runner").health()
    assert healthy is False
    assert "argv-v1" in detail


def test_compose_keeps_runner_private_and_network_isolated() -> None:
    from pathlib import Path

    content = Path("docker-compose.yml").read_text(encoding="utf-8")
    assert "sandbox-runner:" in content
    assert "sandbox-network:" in content
    assert "internal: true" in content
    runner = content.split("  sandbox-runner:", 1)[1].split("networks:", 1)[0]
    assert "ports:" not in runner
    assert "./data/users" not in runner
    assert "./data/cli-apps" not in runner
