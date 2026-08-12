"""No retained runtime module may import Partner implementation code."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION_FILES = {
    ROOT / "deeptutor" / "api" / "routers" / "partners.py",
    ROOT / "deeptutor" / "api" / "routers" / "_partners_channel_schema.py",
    ROOT / "deeptutor" / "services" / "subagent" / "partner.py",
    ROOT / "deeptutor" / "tools" / "partner_memory.py",
    ROOT / "deeptutor" / "multi_user" / "partner_access.py",
}


def test_retained_python_runtime_has_no_partner_implementation_imports() -> None:
    forbidden = (
        "deeptutor.services.partners",
        "deeptutor.partners",
        "deeptutor.api.routers.partners",
        "deeptutor.multi_user.partner_access",
        "deeptutor.services.subagent.partner",
        "deeptutor.tools.partner_memory",
    )
    offenders: list[str] = []
    for path in (ROOT / "deeptutor").rglob("*.py"):
        if path in IMPLEMENTATION_FILES or "partners" in path.parts:
            continue
        source = path.read_text(encoding="utf-8")
        if any(name in source for name in forbidden):
            offenders.append(str(path.relative_to(ROOT)))

    assert offenders == []
