from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


def transcribe_whisper(audio_path: Path, model_name: str = "small") -> Dict[str, Any]:
    """Placeholder for Whisper/STT model inference."""
    return {
        "transcript": "",
        "language": "th",
        "segments": [],
    }


def assemble_transcript(chunks: List[Dict[str, Any]], meeting_id: str) -> Dict[str, Any]:
    transcript_text = "\n".join(chunk.get("transcript", "") for chunk in chunks)
    segments = []
    for chunk in chunks:
        segments.extend(chunk.get("segments", []))
    return {
        "meeting_id": meeting_id,
        "transcript_text": transcript_text,
        "segments": segments,
    }
