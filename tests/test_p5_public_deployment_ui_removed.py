"""Public deployment controls must not remain in the local Network UI."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_network_ui_exposes_local_ports_only() -> None:
    paths = [
        ROOT / "web" / "app" / "(utility)" / "settings" / "network" / "page.tsx",
        ROOT / "web" / "components" / "settings" / "SettingsHub.tsx",
        ROOT / "web" / "lib" / "settings-nav.ts",
    ]
    forbidden = (
        "public_api_base",
        "browser_api_base",
        "cors_origins",
        "CORS origins",
        "remote Docker",
        "reverse proxy",
        "reverse-proxy",
    )
    offenders: list[str] = []
    for path in paths:
        source = path.read_text(encoding="utf-8")
        if any(token in source for token in forbidden):
            offenders.append(path.relative_to(ROOT).as_posix())
    assert offenders == []
