"""PageIndex KBs remain reachable through the ordinary RAG surface."""

from __future__ import annotations

from deeptutor.agents.chat.agentic_pipeline import AgenticChatPipeline
from deeptutor.core.context import UnifiedContext


def test_pageindex_is_not_removed_from_the_rag_kb_list() -> None:
    pipe = AgenticChatPipeline.__new__(AgenticChatPipeline)
    context = UnifiedContext(knowledge_bases=["pageindex-kb", "local-kb"])

    assert pipe._rag_kbs(context) == ["pageindex-kb", "local-kb"]
