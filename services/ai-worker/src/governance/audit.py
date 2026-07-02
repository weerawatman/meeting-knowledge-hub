from __future__ import annotations

from datetime import datetime
from pathlib import Path


def append_audit_event(log_path: Path, event: str) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(f"{datetime.utcnow().isoformat()}Z | {event}\n")


def read_audit_log(log_path: Path) -> str:
    if not log_path.exists():
        return ""
    return log_path.read_text(encoding="utf-8")
