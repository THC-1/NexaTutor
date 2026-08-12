"""CLI contracts for staged removal of Partner commands."""

from __future__ import annotations

from typer.main import get_command

from deeptutor_cli.main import app


def test_partner_group_is_not_registered_and_core_groups_remain() -> None:
    commands = set(get_command(app).commands)

    assert "partner" not in commands
    assert {"chat", "config", "kb", "memory", "notebook", "session"} <= commands
