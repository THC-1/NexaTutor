"""Regression checks for the staged Partner/IM runtime removal."""

from __future__ import annotations

import ast
from pathlib import Path


def test_app_lifespan_does_not_manage_partner_runtime() -> None:
    """Starting the Core API must not start or stop any IM channel runtime."""
    main_path = Path(__file__).resolve().parents[2] / "deeptutor" / "api" / "main.py"
    module = ast.parse(main_path.read_text(encoding="utf-8"))
    lifespan = next(
        node
        for node in module.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "lifespan"
    )

    called_attributes = {
        node.func.attr
        for node in ast.walk(lifespan)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    imported_modules = {
        node.module
        for node in ast.walk(lifespan)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }

    assert "auto_start_partners" not in called_attributes
    assert "stop_all" not in called_attributes
    assert "deeptutor.services.partners" not in imported_modules
