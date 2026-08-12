"""Manage local NexaTutor skills."""

from __future__ import annotations

from rich.table import Table
import typer

from .common import console


def register(app: typer.Typer) -> None:
    @app.command("list")
    def skill_list() -> None:
        """List local skills."""
        from deeptutor.services.skill.service import get_skill_service

        service = get_skill_service()
        table = Table(title="Skills")
        table.add_column("Name", style="bold")
        table.add_column("Source")
        table.add_column("Description")
        for info in service.list_skills():
            table.add_row(info.name, info.source, info.description[:80])
        console.print(table)

    @app.command("remove")
    def skill_remove(
        name: str = typer.Argument(..., help="Skill name to remove."),
    ) -> None:
        """Remove a user-layer skill (builtin skills are read-only)."""
        from deeptutor.services.skill.service import (
            InvalidSkillNameError,
            SkillNotFoundError,
            SkillReadOnlyError,
            get_skill_service,
        )

        try:
            get_skill_service().delete(name)
        except (SkillNotFoundError, InvalidSkillNameError):
            console.print(f"[bold red]Skill not found:[/] {name}")
            raise typer.Exit(code=1)
        except SkillReadOnlyError as exc:
            console.print(f"[bold red]{exc}[/]")
            raise typer.Exit(code=1)
        console.print(f"[green]Removed[/] {name}")
