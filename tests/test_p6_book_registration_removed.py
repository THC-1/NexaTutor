"""P6 negative assertions for removed Book product registrations."""

from deeptutor.api.main import app
from deeptutor.services.memory.snapshot.adapters import SUPPORTED_SURFACES
from deeptutor_cli.main import app as cli_app


def test_book_api_routes_are_not_registered() -> None:
    assert not any(route.path.startswith("/api/v1/book") for route in app.routes)


def test_book_cli_and_memory_surface_are_not_registered() -> None:
    command_names = {
        info.name
        for info in cli_app.registered_groups
        if getattr(info, "name", None)
    }
    assert "book" not in command_names
    assert "book" not in SUPPORTED_SURFACES
