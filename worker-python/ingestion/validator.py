from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Optional

SUPPORTED_EXTENSIONS = {".mp4", ".mkv", ".wav", ".mp3"}
MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024 * 1024  # 25 GB


def compute_checksum(path: Path, algorithm: str = "sha256") -> Optional[str]:
    if not path.exists() or not path.is_file():
        return None

    hash_factory = getattr(hashlib, algorithm, None)
    if hash_factory is None:
        raise ValueError(f"Unsupported checksum algorithm: {algorithm}")

    digest = hash_factory()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)

    return digest.hexdigest()


def validate_recording(path: Path) -> bool:
    if not path.exists() or not path.is_file():
        return False
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return False
    size = path.stat().st_size
    if size == 0 or size > MAX_FILE_SIZE_BYTES:
        return False
    return True


def validate_with_checksum(path: Path) -> Optional[str]:
    if not validate_recording(path):
        return None
    return compute_checksum(path, algorithm="sha256")
