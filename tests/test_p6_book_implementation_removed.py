"""P6 negative assertions for removed Book backend implementation."""

from pathlib import Path

from deeptutor.services.path_service import PathService


def test_book_backend_modules_are_removed() -> None:
    root = Path(__file__).resolve().parents[1]
    assert not any((root / "deeptutor/book").rglob("*.py"))
    assert not (root / "deeptutor/api/routers/book.py").exists()
    assert not (root / "deeptutor_cli/book.py").exists()


def test_path_service_has_no_book_product_api() -> None:
    for name in dir(PathService):
        assert not name.startswith("get_book_")
        assert not name.startswith("ensure_book_")
