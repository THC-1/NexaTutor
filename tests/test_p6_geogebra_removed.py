from __future__ import annotations

import importlib.util
from pathlib import Path

from deeptutor.capabilities.solve.capability import DeepSolveCapability
from deeptutor.tools.builtin import (
    BUILTIN_TOOL_NAMES,
    USER_TOGGLEABLE_TOOL_NAMES,
)


ROOT = Path(__file__).resolve().parents[1]


def test_geogebra_registration_and_implementation_are_removed() -> None:
    assert "geogebra_analysis" not in BUILTIN_TOOL_NAMES
    assert "geogebra_analysis" not in USER_TOGGLEABLE_TOOL_NAMES
    assert "geogebra_analysis" not in DeepSolveCapability.manifest.tools_used
    assert importlib.util.find_spec("deeptutor.agents.vision_solver.vision_solver_agent") is None
    assert importlib.util.find_spec("deeptutor.tools.vision.ggb_validator") is None


def test_geogebra_call_sites_and_ui_are_removed() -> None:
    backend_files = [
        ROOT / "deeptutor" / "agents" / "chat" / "agentic_pipeline.py",
        ROOT / "deeptutor" / "capabilities" / "solve" / "capability.py",
        ROOT / "deeptutor" / "capabilities" / "solve" / "loop.py",
        ROOT / "deeptutor" / "capabilities" / "solve" / "tools.py",
        ROOT / "deeptutor" / "capabilities" / "solve" / "prompts" / "en" / "system.md",
        ROOT / "deeptutor" / "capabilities" / "solve" / "prompts" / "zh" / "system.md",
    ]
    assert all("geogebra" not in path.read_text(encoding="utf-8").lower() for path in backend_files)

    web_files = [
        ROOT / "web" / "app" / "(workspace)" / "home" / "[[...sessionId]]" / "page.tsx",
        ROOT / "web" / "components" / "chat" / "home" / "SessionViewerPanel.tsx",
        ROOT / "web" / "components" / "chat" / "home" / "TracePanels.tsx",
        ROOT / "web" / "components" / "common" / "RichMarkdownRenderer.tsx",
        ROOT / "web" / "lib" / "playground-config.ts",
        ROOT / "web" / "locales" / "en" / "app.json",
        ROOT / "web" / "locales" / "zh" / "app.json",
    ]
    text = "\n".join(path.read_text(encoding="utf-8") for path in web_files).lower()
    assert "geogebra" not in text
    assert "ggbscript" not in text
    assert "deployggb" not in text

    assert not (ROOT / "web" / "components" / "Geogebra.tsx").exists()
    assert not (ROOT / "web" / "components" / "common" / "GeogebraOpenCTA.tsx").exists()
    assert not (ROOT / "web" / "context" / "GeogebraTabContext.tsx").exists()
