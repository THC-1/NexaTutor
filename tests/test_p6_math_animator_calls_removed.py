"""P6 negative assertions for removed Manim calls from retained Visualize."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_visualize_retains_only_lightweight_renderers() -> None:
    for relative in (
        "deeptutor/agents/visualize/capability.py",
        "deeptutor/agents/visualize/agents/analysis_agent.py",
        "deeptutor/agents/visualize/agents/code_generator_agent.py",
        "deeptutor/agents/visualize/models.py",
        "deeptutor/runtime/request_contracts.py",
    ):
        source = (ROOT / relative).read_text(encoding="utf-8").lower()
        assert "manim" not in source
        assert "math_animator" not in source

    models = (ROOT / "deeptutor/agents/visualize/models.py").read_text(encoding="utf-8")
    for renderer in ("svg", "chartjs", "mermaid", "html"):
        assert renderer in models
