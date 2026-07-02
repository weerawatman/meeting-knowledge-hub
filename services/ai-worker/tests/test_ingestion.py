from pathlib import Path
from tempfile import TemporaryDirectory

from ingestion.models import IngestionJob
from ingestion.queue import FileQueue
from ingestion.validator import validate_recording, validate_with_checksum
from ingestion.storage import create_temp_storage, cleanup_old_files


def test_validate_recording(tmp_path: Path) -> None:
    file_path = tmp_path / "meeting.mp4"
    file_path.write_bytes(b"dummy content")
    assert validate_recording(file_path)
    assert validate_with_checksum(file_path) is not None


def test_file_queue_lifecycle(tmp_path: Path) -> None:
    queue_root = tmp_path / "queue"
    queue = FileQueue(queue_root)

    assert list(queue.list_pending()) == []
    job = IngestionJob.create(source_path=tmp_path / "meeting.mp4")
    pending_path = queue.enqueue(job)

    assert pending_path.exists()
    dequeued = queue.dequeue()
    assert dequeued is not None
    queue.mark_done(dequeued)
    assert (queue.done_dir / f"{dequeued.job_id}.json").exists()


def test_temp_storage_cleanup(tmp_path: Path) -> None:
    storage_dir = create_temp_storage(tmp_path)
    old_file = storage_dir / "old.wav"
    old_file.write_bytes(b"legacy")
    old_file_path = str(old_file)
    import os

    os.utime(old_file_path, (0, 0))
    removed = cleanup_old_files(storage_dir, retention_days=1)
    assert removed == 1
