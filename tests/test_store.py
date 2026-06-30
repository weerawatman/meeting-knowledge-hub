from pathlib import Path

from rag.store import MeetingStore


def test_meeting_store_upsert_and_retrieve(tmp_path: Path) -> None:
    db_file = tmp_path / "test.db"
    store = MeetingStore(db_url=f"sqlite:///{db_file}")
    store.upsert_meeting(
        meeting_id="meeting-1",
        title="Test Meeting",
        date="2026-06-30",
        participants="Alice,Bob",
        status="complete",
        transcript="This is a test transcript.",
        metadata={"topic": "testing"},
    )

    meeting = store.get_meeting("meeting-1")
    assert meeting["meeting_id"] == "meeting-1"
    assert "Test Meeting" in meeting["summary"]


def test_meeting_store_feedback(tmp_path: Path) -> None:
    db_file = tmp_path / "feedback.db"
    store = MeetingStore(db_url=f"sqlite:///{db_file}")
    feedback = store.add_feedback(
        meeting_id="meeting-2",
        original_text="Orig",
        corrected_text="Corrected",
        correction_type="transcript",
    )
    assert feedback.meeting_id == "meeting-2"
    assert feedback.corrected_text == "Corrected"
