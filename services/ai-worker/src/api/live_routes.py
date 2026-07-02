from __future__ import annotations

from fastapi import APIRouter, HTTPException

from live.models import AudioChunkRequest, CaptionCandidate, LiveSessionCreate, LiveSessionStatus, TranslateRequest
from live.session import LiveSessionManager
from live.translate_stream import translate_to_formal_japanese

live_router = APIRouter(prefix="/worker/live")
manager = LiveSessionManager()


@live_router.post("/sessions", response_model=LiveSessionStatus)
def create_live_session(req: LiveSessionCreate) -> LiveSessionStatus:
    return manager.create(req)


@live_router.get("/sessions/{session_id}", response_model=LiveSessionStatus)
def get_live_session(session_id: str) -> LiveSessionStatus:
    try:
        return manager.status(session_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@live_router.post("/sessions/{session_id}/audio-chunks", response_model=CaptionCandidate)
def ingest_live_audio_chunk(session_id: str, req: AudioChunkRequest) -> CaptionCandidate:
    try:
        return manager.ingest_audio_chunk(session_id, req)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@live_router.post("/translate", response_model=CaptionCandidate)
def translate_text(req: TranslateRequest) -> CaptionCandidate:
    caption_text, terms = translate_to_formal_japanese(req.text, req.glossary_terms)
    return CaptionCandidate(
        session_id="direct",
        meeting_id=req.meeting_id,
        segment_id="direct",
        start_ms=0,
        end_ms=max(600, len(req.text) * 30),
        source_text=req.text,
        target_language=req.target_language,
        caption_text=caption_text,
        is_final=True,
        confidence=0.9,
        latency_ms=max(120, len(req.text) * 12),
        terms_applied=terms,
    )
