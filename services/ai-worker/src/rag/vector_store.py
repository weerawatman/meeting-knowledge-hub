from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from loguru import logger

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models as qdrant_models
except ImportError:  # pragma: no cover
    QdrantClient = None
    qdrant_models = None


class VectorStore:
    def __init__(self, collection_name: str = "meetings", host: str = "127.0.0.1", port: int = 6333):
        self.collection_name = collection_name
        self.use_qdrant = False
        self.documents: List[Dict[str, Any]] = []

        if QdrantClient is not None:
            try:
                self.client = QdrantClient(url=f"http://{host}:{port}")
                self.use_qdrant = True
                self._ensure_collection()
            except Exception as error:
                logger.warning("Qdrant unavailable, using local fallback vector store: {}", error)
                self.client = None
        else:
            logger.warning("qdrant-client not installed, using local fallback vector store.")
            self.client = None

    def _ensure_collection(self) -> None:
        if not self.client:
            return
        collections = self.client.get_collections().collections
        if self.collection_name not in [collection.name for collection in collections]:
            self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=qdrant_models.VectorParams(size=384, distance=qdrant_models.Distance.COSINE),
            )

    def upsert(self, document_id: str, text: str, metadata: Dict[str, Any], vector: List[float]) -> None:
        if self.use_qdrant and self.client is not None:
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    qdrant_models.PointStruct(
                        id=document_id,
                        vector=vector,
                        payload={"text": text, "metadata": metadata},
                    )
                ],
            )
            return

        self.documents = [doc for doc in self.documents if doc["document_id"] != document_id]
        self.documents.append({"document_id": document_id, "text": text, "metadata": metadata, "vector": vector})

    def search(self, query_vector: List[float], top_k: int = 5, metadata_filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if self.use_qdrant and self.client is not None:
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=top_k,
                query=qdrant_models.Filter(
                    must=[qdrant_models.FieldCondition(key=key, match=qdrant_models.Match(value=value)) for key, value in (metadata_filter or {}).items()]
                ) if metadata_filter else None,
            )
            return [
                {
                    "document_id": hit.id,
                    "score": hit.score,
                    "text": hit.payload.get("text"),
                    "metadata": hit.payload.get("metadata"),
                }
                for hit in search_result
            ]

        results: List[Dict[str, Any]] = []
        for doc in self.documents:
            if metadata_filter:
                if not all(doc["metadata"].get(key) == value for key, value in metadata_filter.items()):
                    continue
            score = self._cosine_similarity(query_vector, doc["vector"])
            results.append({"document_id": doc["document_id"], "score": score, "text": doc["text"], "metadata": doc["metadata"]})
        return sorted(results, key=lambda item: item["score"], reverse=True)[:top_k]

    @staticmethod
    def _cosine_similarity(a: Iterable[float], b: Iterable[float]) -> float:
        a_list = list(a)
        b_list = list(b)
        numerator = sum(x * y for x, y in zip(a_list, b_list))
        denom_a = sum(x * x for x in a_list) ** 0.5
        denom_b = sum(y * y for y in b_list) ** 0.5
        if denom_a == 0 or denom_b == 0:
            return 0.0
        return numerator / (denom_a * denom_b)
