"""P6 negative assertions for the removed Book frontend surface."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"


def test_book_pages_and_frontend_modules_are_removed() -> None:
    assert not any((WEB / "app/(workspace)/book").rglob("*.tsx"))
    for relative in (
        "components/chat/BookReferencePicker.tsx",
        "components/sidebar/BookRecent.tsx",
        "lib/book-api.ts",
        "lib/book-types.ts",
        "lib/book-references.ts",
        "lib/book-ws-operation.ts",
        "lib/book-progress.ts",
    ):
        assert not (WEB / relative).exists()


def test_retained_frontend_has_no_book_product_links_or_pickers() -> None:
    for path in WEB.rglob("*.tsx"):
        if any(part.startswith(".next") for part in path.parts):
            continue
        source = path.read_text(encoding="utf-8")
        assert 'href: "/book"' not in source
        assert 'href="/book"' not in source
        assert "BookReferencePicker" not in source
