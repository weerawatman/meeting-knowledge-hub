from pathlib import Path

from rag.embeddings import embed_text, cosine_similarity
from rag.search import hybrid_search, keyword_search, semantic_search
from rag.vector_store import VectorStore


def test_embed_text_produces_vector_length() -> None:
    vector = embed_text("Test embedding")
    assert len(vector) == 384
    assert any(value != 0.0 for value in vector)


def test_cosine_similarity_identity() -> None:
    vector = embed_text("hello world")
    assert cosine_similarity(vector, vector) == 1.0


def test_keyword_search_scores_documents() -> None:
    documents = [
        {"document_id": "doc1", "text": "This is a meeting note about budget.", "metadata": {}},
        {"document_id": "doc2", "text": "This note is about project timeline.", "metadata": {}},
    ]
    results = keyword_search("budget", documents)
    assert len(results) == 1
    assert results[0]["document_id"] == "doc1"


def test_semantic_search_local_fallback() -> None:
    store = VectorStore()
    store.upsert("doc1", "budget meeting notes", {"meeting_id": "meeting-1"}, embed_text("budget meeting notes"))
    store.upsert("doc2", "project timeline discussion", {"meeting_id": "meeting-1"}, embed_text("project timeline discussion"))
    results = semantic_search("budget meeting", store)
    assert results[0]["document_id"] == "doc1"


def test_hybrid_search_combines_results() -> None:
    store = VectorStore()
    documents = [
        {"document_id": "doc1", "text": "budget meeting notes", "metadata": {"meeting_id": "meeting-1"}},
        {"document_id": "doc2", "text": "project timeline discussion", "metadata": {"meeting_id": "meeting-1"}},
    ]
    store.upsert("doc1", "budget meeting notes", documents[0]["metadata"], embed_text("budget meeting notes"))
    store.upsert("doc2", "project timeline discussion", documents[1]["metadata"], embed_text("project timeline discussion"))
    results = hybrid_search("budget meeting", store, documents)
    assert results[0]["document_id"] == "doc1"
