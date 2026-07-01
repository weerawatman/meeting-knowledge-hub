from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


def cleanup_raw_storage(storage_dir: Path, retention_days: int = 30) -> int:
    cutoff = datetime.utcnow() - timedelta(days=retention_days)
    removed = 0
    for path in storage_dir.rglob("*"):
        if not path.is_file():
            continue
        if datetime.utcfromtimestamp(path.stat().st_mtime) < cutoff:
            path.unlink()
            removed += 1
    return removed


def is_retention_policy_met(storage_dir: Path, retention_days: int = 30) -> bool:
    cutoff = datetime.utcnow() - timedelta(days=retention_days)
    return all(datetime.utcfromtimestamp(path.stat().st_mtime) >= cutoff for path in storage_dir.rglob("*") if path.is_file())
