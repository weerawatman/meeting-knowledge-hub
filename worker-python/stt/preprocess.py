from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Iterable, List, Optional


def _ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None


def normalize_audio(input_path: Path, output_path: Path, sample_rate: int = 16000) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not _ffmpeg_available():
        if input_path.suffix.lower() == ".wav":
            shutil.copy2(input_path, output_path)
            return output_path
        raise RuntimeError(
            "FFmpeg is not available for audio normalization. "
            "Provide a WAV file or install ffmpeg."
        )

    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_path),
        "-ac",
        "1",
        "-ar",
        str(sample_rate),
        str(output_path),
    ]
    subprocess.run(command, check=True, capture_output=True)
    return output_path


def chunk_audio(input_path: Path, output_dir: Path, chunk_duration_seconds: int = 600) -> List[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    if not _ffmpeg_available():
        return [input_path]

    files: List[Path] = []
    index = 0
    while True:
        chunk_file = output_dir / f"chunk_{index:03d}.wav"
        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(input_path),
            "-ss",
            str(index * chunk_duration_seconds),
            "-t",
            str(chunk_duration_seconds),
            str(chunk_file),
        ]
        subprocess.run(command, check=True, capture_output=True)
        if not chunk_file.exists() or chunk_file.stat().st_size == 0:
            chunk_file.unlink(missing_ok=True)
            break
        files.append(chunk_file)
        index += 1
    return files
