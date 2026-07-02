from __future__ import annotations

from typing import Dict, List, Optional, Set

from rag.embeddings import embed_text
from rag.vector_store import VectorStore


def keyword_search(query: str, documents: List[Dict[str, str]], top_k: int = 5) -> List[Dict[str, str]]:
    query_tokens = set(query.lower().split())
    scored = []
    for document in documents:
        text = document.get("text", "").lower()
        score = sum(1 for token in query_tokens if token in text)
        if score > 0:
            scored.append({"document_id": document["document_id"], "score": score, "text": document["text"], "metadata": document.get("metadata", {})})
    return sorted(scored, key=lambda item: item["score"], reverse=True)[:top_k]


def semantic_search(query: str, vector_store: VectorStore, top_k: int = 5, metadata_filter: Optional[Dict[str, str]] = None) -> List[Dict[str, str]]:
    query_vector = embed_text(query)
    return vector_store.search(query_vector, top_k=top_k, metadata_filter=metadata_filter)


def hybrid_search(query: str, vector_store: VectorStore, documents: List[Dict[str, str]], top_k: int = 5, metadata_filter: Optional[Dict[str, str]] = None) -> List[Dict[str, str]]:
    semantic_results = semantic_search(query, vector_store, top_k=top_k, metadata_filter=metadata_filter)
    keyword_results = keyword_search(query, documents, top_k=top_k)
    merged: Dict[str, Dict[str, any]] = {}
    for item in semantic_results:
        merged[item["document_id"]] = {**item, "hybrid_score": item["score"] * 0.7}
    for item in keyword_results:
        existing = merged.get(item["document_id"])
        if existing:
            existing["hybrid_score"] += item["score"] * 0.3
        else:
            merged[item["document_id"]] = {**item, "hybrid_score": item["score"] * 0.3}
    ranked = sorted(merged.values(), key=lambda item: item["hybrid_score"], reverse=True)
    return ranked[:top_k]
