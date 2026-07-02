from pathlib import Path

from governance.audit import append_audit_event, read_audit_log
from governance.retention import cleanup_raw_storage, is_retention_policy_met


def test_audit_logging(tmp_path: Path) -> None:
    log_path = tmp_path / "audit.log"
    append_audit_event(log_path, "user:ingest:success")
    content = read_audit_log(log_path)
    assert "user:ingest:success" in content


def test_retention_cleanup_and_policy(tmp_path: Path) -> None:
    storage = tmp_path / "raw"
    storage.mkdir(parents=True)
    old_file = storage / "old.mp4"
    old_file.write_bytes(b"data")
    import os

    os.utime(str(old_file), (0, 0))
    removed = cleanup_raw_storage(storage, retention_days=1)
    assert removed == 1
    assert is_retention_policy_met(storage, retention_days=1)
