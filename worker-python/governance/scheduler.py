from __future__ import annotations

from pathlib import Path
from typing import Optional

from governance.audit import append_audit_event
from governance.retention import cleanup_raw_storage


def run_retention_cycle(storage_dir: Path, audit_log: Path, retention_days: int = 30) -> int:
    removed = cleanup_raw_storage(storage_dir, retention_days=retention_days)
    append_audit_event(audit_log, f"retention_cleanup:removed={removed}")
    return removed
