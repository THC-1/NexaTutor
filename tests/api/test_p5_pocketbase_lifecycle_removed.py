"""P5 guardrails for removing PocketBase from the FastAPI lifecycle."""

from __future__ import annotations

import ast
from pathlib import Path


def test_app_lifespan_does_not_ping_pocketbase() -> None:
    main_path = Path(__file__).resolve().parents[2] / "deeptutor" / "api" / "main.py"
    module = ast.parse(main_path.read_text(encoding="utf-8"))
    lifespan = next(
        node
        for node in module.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "lifespan"
    )

    imported_modules = {
        node.module
        for node in ast.walk(lifespan)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    called_names = {
        node.func.id
        for node in ast.walk(lifespan)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }

    assert "deeptutor.services.pocketbase_client" not in imported_modules
    assert "ping_pocketbase" not in called_names
