from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


def create_temp_storage(root: Path, folder_name: str = "temp_storage") -> Path:
    storage_dir = root / folder_name
    storage_dir.mkdir(parents=True, exist_ok=True)
    return storage_dir.resolve()


def make_secure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    path.chmod(0o700)
    return path


def cleanup_old_files(storage_dir: Path, retention_days: int = 30) -> int:
    cutoff = datetime.utcnow() - timedelta(days=retention_days)
    removed = 0
    for file_path in storage_dir.rglob("*"):
        if not file_path.is_file():
            continue
        if datetime.utcfromtimestamp(file_path.stat().st_mtime) < cutoff:
            file_path.unlink()
            removed += 1
    return removed
