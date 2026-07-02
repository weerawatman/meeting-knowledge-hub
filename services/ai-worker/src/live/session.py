from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List

from live.models import AudioChunkRequest, CaptionCandidate, LiveSessionCreate, LiveSessionStatus
from live.segmenter import segment_text_hint
from live.translate_stream import translate_to_formal_japanese


@dataclass
class LiveSessionState:
    session_id: str
    meeting_id: str
    source_language: str
    target_language: str
    glossary_terms: List[str] = field(default_factory=list)
    received_chunks: int = 0
    caption_latency_p95_ms: int = 0
    status: str = "live"


class LiveSessionManager:
    def __init__(self) -> None:
        self._sessions: Dict[str, LiveSessionState] = {}

    def create(self, req: LiveSessionCreate) -> LiveSessionStatus:
        session = LiveSessionState(
            session_id=str(uuid.uuid4()),
            meeting_id=req.meeting_id,
            source_language=req.source_language,
            target_language=req.target_language,
            glossary_terms=req.glossary_terms,
        )
        self._sessions[session.session_id] = session
        return self.status(session.session_id)

    def status(self, session_id: str) -> LiveSessionStatus:
        session = self._require(session_id)
        return LiveSessionStatus(
            session_id=session.session_id,
            meeting_id=session.meeting_id,
            source_language=session.source_language,
            target_language=session.target_language,
            status=session.status,
            received_chunks=session.received_chunks,
            caption_latency_p95_ms=session.caption_latency_p95_ms,
        )

    def ingest_audio_chunk(self, session_id: str, req: AudioChunkRequest) -> CaptionCandidate:
        session = self._require(session_id)
        started = time.perf_counter()
        source_text = segment_text_hint(req.text_hint, req.sequence)
        caption_text, terms = translate_to_formal_japanese(source_text, session.glossary_terms)
        latency_ms = max(120, int((time.perf_counter() - started) * 1000) + len(source_text) * 12)
        session.received_chunks += 1
        session.caption_latency_p95_ms = max(session.caption_latency_p95_ms, latency_ms)
        return CaptionCandidate(
            session_id=session.session_id,
            meeting_id=session.meeting_id,
            segment_id=str(uuid.uuid4()),
            start_ms=req.timestamp_ms,
            end_ms=req.timestamp_ms + max(600, len(source_text) * 30),
            source_text=source_text,
            target_language=session.target_language,
            caption_text=caption_text,
            is_final=True,
            confidence=0.85 if req.text_hint else 0.5,
            latency_ms=latency_ms,
            terms_applied=terms,
        )

    def _require(self, session_id: str) -> LiveSessionState:
        session = self._sessions.get(session_id)
        if not session:
            raise KeyError("Live session not found")
        return session

