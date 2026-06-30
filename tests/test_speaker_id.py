from pathlib import Path

from speaker_id.diarize import diarize_audio, map_speaker_ids
from speaker_id.models import SpeakerProfile, SpeakerSegment


def test_diarize_audio_returns_segments() -> None:
    result = diarize_audio(Path("/tmp/meeting.wav"), meeting_id="meeting-123")
    assert result.meeting_id == "meeting-123"
    assert result.audio_path == Path("/tmp/meeting.wav")
    assert len(result.segments) == 1
    assert result.segments[0].speaker_id == "SPEAKER_01"


def test_map_speaker_ids_applies_display_names() -> None:
    result = diarize_audio(Path("/tmp/meeting.wav"), meeting_id="meeting-123")
    mapped = map_speaker_ids(result, {"SPEAKER_01": "Somchai"})
    assert mapped.speakers[0].display_name == "Somchai"
