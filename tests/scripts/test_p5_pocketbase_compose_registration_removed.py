"""P5 guardrails for removing the PocketBase deployment registration."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import yaml


ROOT = Path(__file__).resolve().parents[2]


def _load_wrapper():
    module_path = ROOT / "scripts" / "docker_compose.py"
    spec = importlib.util.spec_from_file_location("p5_docker_compose", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        sys.modules.pop(spec.name, None)


def test_compose_manifests_do_not_register_pocketbase() -> None:
    for name in ("docker-compose.yml", "compose.yaml", "docker-compose.dev.yml"):
        payload = yaml.safe_load((ROOT / name).read_text(encoding="utf-8"))
        services = payload.get("services", {})
        assert "pocketbase" not in services, name
        depends_on = services.get("deeptutor", {}).get("depends_on", {})
        assert "pocketbase" not in depends_on, name


def test_compose_wrapper_does_not_render_pocketbase_port(tmp_path: Path) -> None:
    module = _load_wrapper()
    settings_dir = tmp_path / "settings"
    settings_dir.mkdir()
    output_path = tmp_path / "docker.env"

    values = module.render_docker_env(settings_dir, output_path)

    assert set(values) == {
        "DEEPTUTOR_DOCKER_BACKEND_PORT",
        "DEEPTUTOR_DOCKER_FRONTEND_PORT",
    }
    assert "POCKETBASE" not in output_path.read_text(encoding="utf-8")
