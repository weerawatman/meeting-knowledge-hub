from __future__ import annotations

from pathlib import Path
from typing import Dict

from speaker_id.models import DiarizationResult, SpeakerProfile, SpeakerSegment


def diarize_audio(audio_path: Path, meeting_id: str) -> DiarizationResult:
    """Return a placeholder diarization result for a meeting audio file."""
    dummy_segment = SpeakerSegment(
        speaker_id="SPEAKER_01",
        start_time=0.0,
        end_time=10.0,
        confidence=0.98,
    )
    dummy_profile = SpeakerProfile(
        speaker_id="SPEAKER_01",
        display_name="Unknown Speaker",
    )
    return DiarizationResult(
        meeting_id=meeting_id,
        audio_path=audio_path,
        segments=[dummy_segment],
        speakers=[dummy_profile],
    )


def map_speaker_ids(diarization: DiarizationResult, mapping: Dict[str, str]) -> DiarizationResult:
    for speaker in diarization.speakers:
        if speaker.speaker_id in mapping:
            speaker.display_name = mapping[speaker.speaker_id]
    return diarization
