from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

_model = None


def _get_model(model_name: str = "small"):
    global _model
    if _model is None:
        from faster_whisper import WhisperModel
        _model = WhisperModel(model_name, device="cpu", compute_type="int8")
    return _model


def transcribe_whisper(audio_path: Path, model_name: str = "small") -> Dict[str, Any]:
    """Transcribe audio using faster-whisper. Returns transcript text, language, and segments."""
    model = _get_model(model_name)
    segments_iter, info = model.transcribe(
        str(audio_path),
        beam_size=5,
        word_timestamps=False,
        vad_filter=True,
    )
    segments: List[Dict[str, Any]] = []
    transcript_parts: List[str] = []
    for seg in segments_iter:
        text = seg.text.strip()
        segments.append({
            "text": text,
            "start_time": seg.start,
            "end_time": seg.end,
            "speaker": None,
        })
        transcript_parts.append(text)

    return {
        "transcript": " ".join(transcript_parts),
        "language": info.language,
        "segments": segments,
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
