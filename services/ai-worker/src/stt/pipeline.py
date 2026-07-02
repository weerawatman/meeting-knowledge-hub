from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from stt.models import TranscriptResult, TranscriptSegment
from stt.preprocess import chunk_audio, normalize_audio
from stt.whisper_inference import assemble_transcript, transcribe_whisper


def run_stt_pipeline(
    meeting_id: str,
    audio_path: Path,
    work_dir: Path,
    sample_rate: int = 16000,
    chunk_duration_seconds: int = 600,
    model_name: str = "small",
) -> TranscriptResult:
    normalized_audio = work_dir / f"{audio_path.stem}_normalized.wav"
    normalize_audio(audio_path, normalized_audio, sample_rate=sample_rate)

    chunk_dir = work_dir / "chunks"
    chunk_paths = chunk_audio(normalized_audio, chunk_dir, chunk_duration_seconds=chunk_duration_seconds)
    if not chunk_paths:
        chunk_paths = [normalized_audio]

    stt_chunks: List[Dict[str, any]] = []
    for chunk_path in chunk_paths:
        stt_chunks.append(transcribe_whisper(chunk_path, model_name=model_name))

    assembled = assemble_transcript(stt_chunks, meeting_id)
    segments = [
        TranscriptSegment(
            speaker=segment.get("speaker"),
            text=segment.get("text", ""),
            start_time=segment.get("start_time", 0.0),
            end_time=segment.get("end_time", 0.0),
        )
        for segment in assembled.get("segments", [])
    ]

    return TranscriptResult(
        meeting_id=meeting_id,
        audio_path=audio_path,
        transcript_text=assembled.get("transcript_text", ""),
        segments=segments,
        language=assembled.get("language"),
    )
