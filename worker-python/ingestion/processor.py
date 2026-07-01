from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Optional


def _ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None


def extract_audio(source_path: Path, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    audio_path = output_dir / f"{source_path.stem}.wav"

    if source_path.suffix.lower() in {".wav", ".mp3"}:
        shutil.copy2(source_path, audio_path)
        return audio_path

    if _ffmpeg_available():
        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(source_path),
            "-ac",
            "1",
            "-ar",
            "16000",
            str(audio_path),
        ]
        subprocess.run(command, check=True, capture_output=True)
        return audio_path

    raise RuntimeError(
        "FFmpeg is not available for video-to-audio extraction. "
        "Install ffmpeg or provide a native audio file."
    )


def prepare_audio(source_path: Path, temp_dir: Path) -> Path:
    if source_path.suffix.lower() in {".wav", ".mp3"}:
        return extract_audio(source_path, temp_dir)

    return extract_audio(source_path, temp_dir)
