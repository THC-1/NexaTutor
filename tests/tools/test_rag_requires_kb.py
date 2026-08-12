from __future__ import annotations

import asyncio

import pytest

from deeptutor.tools.rag_tool import rag_search


def test_rag_search_requires_an_explicit_knowledge_base() -> None:
    with pytest.raises(ValueError, match="kb_name"):
        asyncio.run(rag_search(query="hi", kb_name=""))
