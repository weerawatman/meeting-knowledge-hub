from pathlib import Path

from stt.models import TranscriptResult, TranscriptSegment
from stt.whisper_inference import assemble_transcript


def test_transcript_model_to_dict() -> None:
    transcript = TranscriptResult(
        meeting_id="meeting-123",
        audio_path=Path("/tmp/meeting.wav"),
        transcript_text="Hello world",
        segments=[
            TranscriptSegment(
                speaker="SPEAKER_01",
                text="Hello world",
                start_time=0.0,
                end_time=2.0,
            )
        ],
    )
    result = transcript.to_dict()
    assert result["meeting_id"] == "meeting-123"
    assert result["transcript_text"] == "Hello world"
    assert result["segments"][0]["speaker"] == "SPEAKER_01"


def test_assemble_transcript_chunks() -> None:
    chunks = [
        {"transcript": "Hello", "segments": [{"speaker": "SPEAKER_01", "text": "Hello", "start_time": 0.0, "end_time": 1.0}]},
        {"transcript": "world", "segments": [{"speaker": "SPEAKER_01", "text": "world", "start_time": 1.0, "end_time": 2.0}]},
    ]
    assembled = assemble_transcript(chunks, "meeting-123")
    assert assembled["meeting_id"] == "meeting-123"
    assert "Hello\nworld" in assembled["transcript_text"]
    assert len(assembled["segments"]) == 2
