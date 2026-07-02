from pathlib import Path
from typing import Any, Dict


def preprocess_audio(input_path: Path, output_path: Path) -> Path:
    """Placeholder for audio normalization and preprocessing."""
    # TODO: implement resampling, channel normalization, and optional noise reduction
    return output_path


def transcribe_audio(audio_path: Path) -> Dict[str, Any]:
    """Placeholder for speech-to-text transcription output."""
    return {
        "transcript": "",
        "segments": [],
        "language": None,
    }
