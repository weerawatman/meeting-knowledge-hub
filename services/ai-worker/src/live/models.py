from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class LiveSessionCreate(BaseModel):
    meeting_id: str
    source_language: str = "th-en"
    target_language: str = "ja"
    glossary_terms: List[str] = Field(default_factory=list)


class LiveSessionStatus(BaseModel):
    session_id: str
    meeting_id: str
    source_language: str
    target_language: str
    status: str
    received_chunks: int
    caption_latency_p95_ms: int


class AudioChunkRequest(BaseModel):
    meeting_id: str
    sequence: int
    timestamp_ms: int
    sample_rate: int = 16000
    channels: int = 1
    encoding: str = "pcm16"
    audio_base64: Optional[str] = None
    text_hint: Optional[str] = None
    speaker_hint: Optional[str] = None


class CaptionCandidate(BaseModel):
    session_id: str
    meeting_id: str
    segment_id: str
    start_ms: int
    end_ms: int
    source_text: str
    target_language: str
    caption_text: str
    is_final: bool
    confidence: float
    latency_ms: int
    terms_applied: List[str]


class TranslateRequest(BaseModel):
    meeting_id: str
    text: str
    target_language: str = "ja"
    glossary_terms: List[str] = Field(default_factory=list)

