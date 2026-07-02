from __future__ import annotations


def segment_text_hint(text_hint: str | None, sequence: int) -> str:
    if text_hint and text_hint.strip():
        return text_hint.strip()
    return f"Live audio chunk {sequence} received"

