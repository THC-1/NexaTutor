"""P6 negative assertions for removed Math Animator UI."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"


def test_math_animator_components_and_types_are_removed() -> None:
    assert not (WEB / "components/math-animator/MathAnimatorViewer.tsx").exists()
    assert not (WEB / "lib/math-animator-types.ts").exists()


def test_retained_frontend_has_no_math_animator_or_manim_surface() -> None:
    for relative in (
        "app/(workspace)/home/[[...sessionId]]/page.tsx",
        "app/(utility)/settings/capabilities/page.tsx",
        "components/chat/home/CapabilityConfigCard.tsx",
        "components/chat/home/ChatMessages.tsx",
        "components/chat/home/TracePanels.tsx",
        "components/visualize/VisualizationViewer.tsx",
        "components/visualize/VisualizeConfigPanel.tsx",
        "lib/visualize-types.ts",
    ):
        source = (WEB / relative).read_text(encoding="utf-8").lower()
        assert "math_animator" not in source
        assert "math-animator" not in source
        assert "manim" not in source
