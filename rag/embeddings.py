from __future__ import annotations

import math
from typing import Iterable, List


def embed_text(text: str, dimension: int = 384) -> List[float]:
    tokens = text.split()
    if not tokens:
        return [0.0] * dimension

    vector = [0.0] * dimension
    for index, token in enumerate(tokens):
        vector[index % dimension] += len(token)

    length = math.sqrt(sum(value * value for value in vector))
    if length == 0:
        return vector

    return [value / length for value in vector]


def cosine_similarity(a: Iterable[float], b: Iterable[float]) -> float:
    a_list = list(a)
    b_list = list(b)
    dot = sum(x * y for x, y in zip(a_list, b_list))
    mag_a = math.sqrt(sum(x * x for x in a_list))
    mag_b = math.sqrt(sum(y * y for y in b_list))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)
