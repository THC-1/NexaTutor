"""P5 guardrails for local-only launch and container bindings."""

from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def test_remote_cors_normalizer_implementation_is_removed() -> None:
    assert not (ROOT / "deeptutor" / "services" / "config" / "origins.py").exists()


def test_launcher_does_not_read_external_api_base_or_bind_all_interfaces() -> None:
    source = (ROOT / "deeptutor" / "runtime" / "launcher.py").read_text(encoding="utf-8")
    assert "NEXT_PUBLIC_API_BASE_EXTERNAL" not in source
    assert 'common_env["HOSTNAME"] = "127.0.0.1"' in source
    assert '"--host",\n        "127.0.0.1"' in source


def test_frontend_config_does_not_enumerate_lan_hosts() -> None:
    source = (ROOT / "web" / "next.config.js").read_text(encoding="utf-8")
    assert "NEXT_PUBLIC_API_BASE_EXTERNAL" not in source
    assert "localNetworkHosts" not in source
    assert 'allowedDevOrigins: ["127.0.0.1"]' in source


def test_compose_publishes_core_ports_on_loopback_only() -> None:
    for name in ("docker-compose.yml", "docker-compose.ghcr.yml", "compose.yaml"):
        payload = yaml.safe_load((ROOT / name).read_text(encoding="utf-8"))
        ports = payload["services"]["deeptutor"].get("ports", [])
        assert ports, name
        assert all(str(port).startswith("127.0.0.1:") for port in ports), name

    runner = yaml.safe_load((ROOT / "docker-compose.yml").read_text(encoding="utf-8"))[
        "services"
    ]["sandbox-runner"]
    assert not runner.get("ports")
