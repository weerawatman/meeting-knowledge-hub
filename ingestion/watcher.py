import os
from pathlib import Path
from typing import Generator

SUPPORTED_EXTENSIONS = {".mp4", ".mkv", ".wav", ".mp3"}


def list_recordings(directory: Path) -> Generator[Path, None, None]:
    """Yield supported recording files from a directory."""
    for root, _, files in os.walk(directory):
        for name in files:
            path = Path(root) / name
            if path.suffix.lower() in SUPPORTED_EXTENSIONS:
                yield path


def validate_recording(path: Path) -> bool:
    """Validate file extension and basic existence."""
    if not path.exists() or not path.is_file():
        return False
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return False
    if path.stat().st_size == 0:
        return False
    return True
