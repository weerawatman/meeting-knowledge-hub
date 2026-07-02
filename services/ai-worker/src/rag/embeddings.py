from __future__ import annotations

import math
from typing import Iterable, List

_model = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("BAAI/bge-small-en-v1.5")
    return _model


def embed_text(text: str, dimension: int = 384) -> List[float]:
    if not text or not text.strip():
        return [0.0] * dimension
    model = _get_model()
    vector = model.encode([text])[0].tolist()
    return vector


def cosine_similarity(a: Iterable[float], b: Iterable[float]) -> float:
    a_list = list(a)
    b_list = list(b)
    dot = sum(x * y for x, y in zip(a_list, b_list))
    mag_a = math.sqrt(sum(x * x for x in a_list))
    mag_b = math.sqrt(sum(y * y for y in b_list))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)
