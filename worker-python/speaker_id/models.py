from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class SpeakerSegment:
    speaker_id: str
    start_time: float
    end_time: float
    confidence: Optional[float] = None


@dataclass
class SpeakerProfile:
    speaker_id: str
    display_name: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


@dataclass
class DiarizationResult:
    meeting_id: str
    audio_path: Path
    segments: List[SpeakerSegment] = field(default_factory=list)
    speakers: List[SpeakerProfile] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "meeting_id": self.meeting_id,
            "audio_path": str(self.audio_path),
            "segments": [
                {
                    "speaker_id": segment.speaker_id,
                    "start_time": segment.start_time,
                    "end_time": segment.end_time,
                    "confidence": segment.confidence,
                }
                for segment in self.segments
            ],
            "speakers": [
                {
                    "speaker_id": speaker.speaker_id,
                    "display_name": speaker.display_name,
                    "metadata": speaker.metadata,
                    "created_at": speaker.created_at,
                }
                for speaker in self.speakers
            ],
            "created_at": self.created_at,
        }
