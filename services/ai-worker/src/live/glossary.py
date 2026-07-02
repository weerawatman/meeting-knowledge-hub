from __future__ import annotations

from typing import Iterable, List


DEFAULT_PRESERVE_TERMS = ["KPI", "backlog", "budget", "sprint"]


def applied_terms(text: str, glossary_terms: Iterable[str] | None = None) -> List[str]:
    terms = list(glossary_terms or DEFAULT_PRESERVE_TERMS)
    text_lower = text.lower()
    return [term for term in terms if term.lower() in text_lower]


def preserve_terms(caption: str, source_text: str, glossary_terms: Iterable[str] | None = None) -> str:
    """Keep approved English terms visible in the Japanese caption scaffold."""
    terms = applied_terms(source_text, glossary_terms)
    if not terms:
        return caption
    suffix = " / " + ", ".join(terms)
    return caption if suffix in caption else f"{caption}{suffix}"

