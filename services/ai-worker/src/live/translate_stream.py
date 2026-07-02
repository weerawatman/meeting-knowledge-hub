from __future__ import annotations

from typing import Iterable, Tuple

from live.glossary import applied_terms, preserve_terms


def translate_to_formal_japanese(text: str, glossary_terms: Iterable[str] | None = None) -> Tuple[str, list[str]]:
    """
    Deterministic scaffold for the live translation contract.

    Production implementation should call the approved on-prem translation model
    and enforce formal business Japanese plus glossary constraints.
    """
    clean = " ".join(text.strip().split())
    terms = applied_terms(clean, glossary_terms)
    if not clean:
        return "", terms

    caption = f"{clean} について確認いたします。"
    return preserve_terms(caption, clean, glossary_terms), terms

