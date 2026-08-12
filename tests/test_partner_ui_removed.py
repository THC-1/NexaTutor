"""Negative contracts for the removed Partner web surface."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"


def test_partner_routes_components_and_clients_are_absent() -> None:
    assert not any(path.is_file() for path in (WEB / "app" / "(workspace)" / "partners").rglob("*"))
    assert not any(path.is_file() for path in (WEB / "components" / "partners").rglob("*"))
    assert not (WEB / "lib" / "partners-api.ts").exists()
    assert not (WEB / "lib" / "partner-session.ts").exists()


def test_retained_web_source_has_no_partner_surface_references() -> None:
    forbidden = (
        'href: "/partners"',
        'href="/partners"',
        "@/components/partners",
        "@/lib/partners-api",
        "@/lib/partner-session",
    )
    offenders: list[str] = []
    for root in (WEB / "app", WEB / "components", WEB / "features", WEB / "lib"):
        for path in root.rglob("*"):
            if path.suffix not in {".ts", ".tsx"}:
                continue
            source = path.read_text(encoding="utf-8")
            if any(token in source for token in forbidden):
                offenders.append(str(path.relative_to(ROOT)))

    assert offenders == []
