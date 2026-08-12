"""P6 negative assertions for removed Math Animator registration."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_math_animator_is_not_registered_or_configurable() -> None:
    for relative in (
        "deeptutor/runtime/bootstrap/builtin_capabilities.py",
        "deeptutor/runtime/request_contracts.py",
        "deeptutor/services/config/capabilities_settings.py",
        "deeptutor/services/config/loader.py",
        "deeptutor/services/setup/init.py",
        "deeptutor_cli/main.py",
    ):
        source = (ROOT / relative).read_text(encoding="utf-8").lower()
        assert "math_animator" not in source
