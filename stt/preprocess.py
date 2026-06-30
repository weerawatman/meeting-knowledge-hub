from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional


def normalize_audio(input_path: Path, output_path: Path, sample_rate: int = 16000) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
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


def chunk_audio(input_path: Path, output_dir: Path, chunk_duration_seconds: int = 600) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    files = []
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
