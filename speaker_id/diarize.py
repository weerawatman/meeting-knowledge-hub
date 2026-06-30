from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from speaker_id.models import DiarizationResult, SpeakerProfile, SpeakerSegment

SPEAKER_LABELS = ["SPEAKER_01", "SPEAKER_02", "SPEAKER_03", "SPEAKER_04"]
SPEAKER_CHANGE_GAP_SECONDS = 1.5


def diarize_audio(
    audio_path: Path,
    meeting_id: str,
    transcript_segments: Optional[List[Dict[str, Any]]] = None,
) -> DiarizationResult:
    """
    Heuristic speaker diarization based on Whisper segment gaps.
    If transcript_segments are provided, uses timing gaps to detect speaker turns.
    Falls back to a single speaker if no segments available.
    """
    if not transcript_segments:
        segment = SpeakerSegment(
            speaker_id="SPEAKER_01",
            start_time=0.0,
            end_time=60.0,
            confidence=0.5,
        )
        profile = SpeakerProfile(speaker_id="SPEAKER_01", display_name="Speaker 1")
        return DiarizationResult(
            meeting_id=meeting_id,
            audio_path=audio_path,
            segments=[segment],
            speakers=[profile],
        )

    sorted_segs = sorted(transcript_segments, key=lambda s: s.get("start_time", 0.0))

    diarized: List[SpeakerSegment] = []
    speaker_ids_used: set = set()
    current_speaker_idx = 0
    prev_end = 0.0

    for seg in sorted_segs:
        start = seg.get("start_time", 0.0)
        end = seg.get("end_time", start + 1.0)
        gap = start - prev_end

        if gap > SPEAKER_CHANGE_GAP_SECONDS and diarized:
            current_speaker_idx = (current_speaker_idx + 1) % len(SPEAKER_LABELS)

        speaker_id = SPEAKER_LABELS[current_speaker_idx]
        speaker_ids_used.add(speaker_id)
        diarized.append(SpeakerSegment(
            speaker_id=speaker_id,
            start_time=start,
            end_time=end,
            confidence=0.7,
        ))
        prev_end = end

    speakers = [
        SpeakerProfile(
            speaker_id=sid,
            display_name=f"Speaker {sid.split('_')[1].lstrip('0') or '1'}",
        )
        for sid in sorted(speaker_ids_used)
    ]

    return DiarizationResult(
        meeting_id=meeting_id,
        audio_path=audio_path,
        segments=diarized,
        speakers=speakers,
    )


def map_speaker_ids(diarization: DiarizationResult, mapping: Dict[str, str]) -> DiarizationResult:
    for speaker in diarization.speakers:
        if speaker.speaker_id in mapping:
            speaker.display_name = mapping[speaker.speaker_id]
    return diarization
