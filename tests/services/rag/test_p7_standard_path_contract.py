from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from llama_index.core import Settings
from llama_index.core.embeddings import BaseEmbedding
import pytest


class _DeterministicEmbedding(BaseEmbedding):
    def _vector(self, _text: str) -> list[float]:
        return [1.0, 0.0, 0.0, 0.0]

    def _get_text_embedding(self, text: str) -> list[float]:
        return self._vector(text)

    def _get_query_embedding(self, query: str) -> list[float]:
        return self._vector(query)

    async def _aget_text_embedding(self, text: str) -> list[float]:
        return self._vector(text)

    async def _aget_query_embedding(self, query: str) -> list[float]:
        return self._vector(query)


def test_llamaindex_result_exposes_page_aware_citation() -> None:
    from deeptutor.services.rag.pipelines.llamaindex.pipeline import LlamaIndexPipeline
    from deeptutor.tools.builtin import _rag_sources

    pipeline = object.__new__(LlamaIndexPipeline)
    node = SimpleNamespace(
        node=SimpleNamespace(
            text="Grounded passage",
            metadata={
                "file_name": "lesson.pdf",
                "file_path": "raw/lesson.pdf",
                "page_label": "7",
            },
            node_id="chunk-7",
        ),
        score=0.875,
    )

    result = pipeline._nodes_to_result("Where is the proof?", [node])
    assert result["sources"] == [
        {
            "title": "lesson.pdf",
            "content": "Grounded passage",
            "source": "raw/lesson.pdf",
            "page": "7",
            "chunk_id": "chunk-7",
            "score": 0.875,
        }
    ]
    assert _rag_sources(result, query=result["query"], kb_name="math") == [
        {
            "type": "rag",
            "kb_name": "math",
            **result["sources"][0],
        }
    ]


def test_standard_index_write_persists_faiss_and_bm25(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from llama_index.core import Document

    from deeptutor.services.rag.pipelines.llamaindex import storage, vector_store
    from deeptutor.services.rag.pipelines.llamaindex.retrievers import BM25_PERSIST_DIRNAME

    storage_dir = tmp_path / "version-1"
    storage_dir.mkdir()
    monkeypatch.setattr(Settings, "embed_model", _DeterministicEmbedding())

    assert storage.create_index([Document(text="A theorem and its proof.")], storage_dir) == 1
    assert vector_store.detect_backend(storage_dir) == vector_store.BACKEND_FAISS
    assert (storage_dir / BM25_PERSIST_DIRNAME).is_dir()
