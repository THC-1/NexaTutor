"""P6 negative assertions for the removed videogen frontend surface."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"


def test_video_settings_page_is_removed() -> None:
    assert not (WEB / "app/(utility)/settings/video/page.tsx").exists()


def test_retained_frontend_does_not_expose_videogen() -> None:
    for relative in (
        "app/(workspace)/home/[[...sessionId]]/page.tsx",
        "components/settings/SettingsContext.tsx",
        "components/settings/ServiceConfigEditor.tsx",
        "lib/settings-nav.ts",
    ):
        source = (WEB / relative).read_text(encoding="utf-8").lower()
        assert "videogen" not in source
