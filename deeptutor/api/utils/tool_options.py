"""Configurable-tool surface for the multi-user admin API.

``tools`` mirrors the user-toggleable system tools (the same pool the chat
composer / settings expose); ``builtin_tools`` lists the auto-mounted built-in
tools (rag / read_memory / web_fetch / …) an administrator can allow or deny.
"""

from __future__ import annotations

import logging
from typing import Any

from deeptutor.core.i18n import current_language
from deeptutor.i18n.metadata_i18n import localized_description, tool_description_i18n

logger = logging.getLogger(__name__)


async def build_tool_options(
    *, exclude_builtin: set[str] | None = None
) -> dict[str, list[dict[str, Any]]]:
    """Build the configurable-tool surface.

    ``exclude_builtin`` drops named tools from the ``builtin_tools`` list.
    """
    from deeptutor.agents._shared.tool_composition import default_optional_tools
    from deeptutor.runtime.registry.tool_registry import get_tool_registry
    from deeptutor.tools.builtin import CONFIGURABLE_BUILTIN_TOOL_NAMES

    exclude = exclude_builtin or set()

    registry = get_tool_registry()
    language = current_language()
    def _describe(name: str) -> dict[str, Any]:
        tool = registry.get(name)
        description = ""
        if tool is not None:
            try:
                description = tool.get_definition().description or ""
            except Exception:
                description = ""
        descriptions = tool_description_i18n(name, description)
        return {
            "name": name,
            "description": localized_description(descriptions, language),
            "description_i18n": descriptions,
        }

    tools: list[dict[str, Any]] = [_describe(name) for name in default_optional_tools()]
    builtin_tools: list[dict[str, Any]] = [
        _describe(name) for name in CONFIGURABLE_BUILTIN_TOOL_NAMES if name not in exclude
    ]

    return {"tools": tools, "builtin_tools": builtin_tools}


__all__ = ["build_tool_options"]
