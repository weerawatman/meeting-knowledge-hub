from pathlib import Path

from speaker_id.diarize import diarize_audio, map_speaker_ids


def test_diarize_audio_no_segments_returns_single_speaker() -> None:
    """Without transcript segments, falls back to one SPEAKER_01 segment."""
    result = diarize_audio(Path("/tmp/meeting.wav"), meeting_id="meeting-123")
    assert result.meeting_id == "meeting-123"
    assert result.audio_path == Path("/tmp/meeting.wav")
    assert len(result.segments) == 1
    assert result.segments[0].speaker_id == "SPEAKER_01"


def test_diarize_audio_with_segments_assigns_speakers() -> None:
    """With transcript segments, assigns speaker IDs based on gap heuristic."""
    segs = [
        {"start_time": 0.0, "end_time": 2.0, "text": "Hello"},
        {"start_time": 4.0, "end_time": 6.0, "text": "Hi there"},  # gap > 1.5s
        {"start_time": 6.5, "end_time": 8.0, "text": "How are you"},  # same speaker (gap < 1.5s)
    ]
    result = diarize_audio(Path("/tmp/meeting.wav"), meeting_id="m1", transcript_segments=segs)
    assert len(result.segments) == 3
    # First segment and third segment should differ from second
    assert result.segments[0].speaker_id != result.segments[1].speaker_id
    assert result.segments[1].speaker_id == result.segments[2].speaker_id


def test_map_speaker_ids_applies_display_names() -> None:
    result = diarize_audio(Path("/tmp/meeting.wav"), meeting_id="meeting-123")
    mapped = map_speaker_ids(result, {"SPEAKER_01": "Somchai"})
    assert mapped.speakers[0].display_name == "Somchai"
