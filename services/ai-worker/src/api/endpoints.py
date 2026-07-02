from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, UploadFile, File

from api.models import CorrectionRequest, IngestRequest, MeetingResponse, SearchResponse, SearchResponseItem
from api.security import get_current_role
from rag.embeddings import embed_text
from rag.search import hybrid_search
from rag.vector_store import VectorStore

router = APIRouter()

_ALLOWED_SUFFIXES = {".mp4", ".mkv", ".mov", ".avi", ".wav", ".mp3", ".m4a"}
_UPLOAD_DIR = Path(os.getenv("DATA_DIR", "./data")) / "uploads"


def _get_pipeline(request: Request):
    return request.app.state.pipeline


def _get_store(request: Request):
    return request.app.state.store


# ---------------------------------------------------------------------------
# File upload (browser multipart)
# ---------------------------------------------------------------------------

@router.post("/upload")
async def upload_meeting(
    request: Request,
    file: UploadFile = File(...),
) -> Dict[str, Any]:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in _ALLOWED_SUFFIXES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Allowed: {sorted(_ALLOWED_SUFFIXES)}",
        )

    meeting_id = str(uuid.uuid4())
    dest_dir = _UPLOAD_DIR / meeting_id
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / (file.filename or f"recording{suffix}")

    content = await file.read()
    dest_path.write_bytes(content)

    pipeline = _get_pipeline(request)
    pipeline.submit(meeting_id, dest_path)

    return {"meeting_id": meeting_id, "status": "queued", "filename": file.filename}


# ---------------------------------------------------------------------------
# Processing status polling
# ---------------------------------------------------------------------------

@router.get("/meetings/{meeting_id}/status")
def get_meeting_status(meeting_id: str, request: Request) -> Dict[str, Any]:
    pipeline = _get_pipeline(request)
    status = pipeline.get_status(meeting_id)
    return {"meeting_id": meeting_id, **status}


# ---------------------------------------------------------------------------
# Meeting result viewer
# ---------------------------------------------------------------------------

@router.get("/meetings/{meeting_id}", response_model=MeetingResponse)
def get_meeting(meeting_id: str, request: Request) -> MeetingResponse:
    pipeline = _get_pipeline(request)
    result = pipeline.get_result(meeting_id)
    if result:
        return MeetingResponse(
            meeting_id=result["meeting_id"],
            summary=result.get("summary", ""),
            decisions=result.get("decisions", []),
            action_items=result.get("action_items", []),
            transcript=result.get("transcript", []),
        )

    # Fall back to RAG store if JSON not found
    store = _get_store(request)
    stored = store.get_meeting(meeting_id)
    return MeetingResponse(
        meeting_id=stored["meeting_id"],
        summary=stored.get("summary", ""),
        decisions=stored.get("decisions", []),
        action_items=stored.get("action_items", []),
        transcript=stored.get("transcript", []),
    )


# ---------------------------------------------------------------------------
# Semantic + keyword search
# ---------------------------------------------------------------------------

@router.get("/search", response_model=SearchResponse)
def search(
    request: Request,
    q: str = Query(..., min_length=1),
    speaker: Optional[str] = None,
    from_date: Optional[str] = None,
    role: str = Depends(get_current_role),
) -> SearchResponse:
    store = _get_store(request)
    raw_results = store.search(q, top_k=10)
    items = [
        SearchResponseItem(
            document_id=r.get("document_id", ""),
            score=r.get("score", 0.0),
            text=r.get("text", ""),
            metadata=r.get("metadata"),
        )
        for r in raw_results
    ]
    return SearchResponse(query=q, results=items)


# ---------------------------------------------------------------------------
# Corrections / feedback
# ---------------------------------------------------------------------------

@router.post("/meetings/{meeting_id}/corrections")
def submit_correction(
    meeting_id: str,
    correction: CorrectionRequest,
    request: Request,
    role: str = Depends(get_current_role),
) -> Dict[str, Any]:
    store = _get_store(request)
    store.add_feedback(
        meeting_id=meeting_id,
        original_text=correction.original_text,
        corrected_text=correction.corrected_text,
        correction_type=correction.correction_type,
    )
    return {"meeting_id": meeting_id, "status": "correction_received", "role": role}


# ---------------------------------------------------------------------------
# Action items convenience endpoint
# ---------------------------------------------------------------------------

@router.get("/meetings/{meeting_id}/action-items")
def get_action_items(meeting_id: str, request: Request) -> Dict[str, List[Dict[str, Any]]]:
    pipeline = _get_pipeline(request)
    result = pipeline.get_result(meeting_id)
    action_items = result.get("action_items", []) if result else []
    return {"meeting_id": meeting_id, "action_items": action_items}


# ---------------------------------------------------------------------------
# Server-side path ingestion (kept for backward compat)
# ---------------------------------------------------------------------------

@router.post("/meetings/ingest")
def ingest_meeting(request: Request, req: IngestRequest) -> Dict[str, Any]:
    if not req.source_path:
        raise HTTPException(status_code=400, detail="source_path is required")
    source_path = Path(req.source_path)
    if not source_path.exists():
        raise HTTPException(status_code=400, detail=f"File not found: {req.source_path}")
    meeting_id = str(uuid.uuid4())
    pipeline = _get_pipeline(request)
    pipeline.submit(meeting_id, source_path)
    return {"status": "queued", "meeting_id": meeting_id}
