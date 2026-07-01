from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class TranscriptSegment:
    speaker: Optional[str]
    text: str
    start_time: float
    end_time: float


@dataclass
class TranscriptResult:
    meeting_id: str
    audio_path: Path
    transcript_text: str
    segments: List[TranscriptSegment] = field(default_factory=list)
    language: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "meeting_id": self.meeting_id,
            "audio_path": str(self.audio_path),
            "transcript_text": self.transcript_text,
            "segments": [
                {
                    "speaker": segment.speaker,
                    "text": segment.text,
                    "start_time": segment.start_time,
                    "end_time": segment.end_time,
                }
                for segment in self.segments
            ],
            "language": self.language,
            "created_at": self.created_at,
        }
