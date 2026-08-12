"""P6 negative assertions for removed Math Animator implementation."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_math_animator_backend_and_dependency_are_removed() -> None:
    assert not any((ROOT / "deeptutor/agents/math_animator").rglob("*.py"))
    assert not (ROOT / "requirements/math-animator.txt").exists()
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8").lower()
    assert "math-animator" not in pyproject
    assert "manim" not in pyproject


def test_safety_and_lightweight_visualization_are_preserved() -> None:
    assert (ROOT / "deeptutor/services/sandbox").is_dir()
    builtin = (ROOT / "deeptutor/tools/builtin/__init__.py").read_text(encoding="utf-8")
    assert "CodeExecutionTool" in builtin
    models = (ROOT / "deeptutor/agents/visualize/models.py").read_text(encoding="utf-8")
    for renderer in ("svg", "chartjs", "mermaid", "html"):
        assert renderer in models
