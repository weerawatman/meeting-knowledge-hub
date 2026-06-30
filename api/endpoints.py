from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Any, Dict, List, Optional

from api.models import CorrectionRequest, IngestRequest, MeetingResponse, SearchResponse, SearchResponseItem
from api.security import get_current_role
from rag.embeddings import embed_text
from rag.search import hybrid_search
from rag.vector_store import VectorStore

router = APIRouter()
vector_store = VectorStore()
local_documents: List[Dict[str, Any]] = []


@router.post("/meetings/ingest")
def ingest_meeting(request: IngestRequest) -> Dict[str, Any]:
    if not request.source_path:
        raise HTTPException(status_code=400, detail="source_path is required")
    document_id = request.source_path
    local_documents.append({"document_id": document_id, "text": request.source_path, "metadata": request.metadata or {}})
    vector_store.upsert(document_id, request.source_path, request.metadata or {}, embed_text(request.source_path))
    return {"status": "ingested", "meeting_id": document_id}


@router.get("/meetings/{meeting_id}", response_model=MeetingResponse)
def get_meeting(meeting_id: str) -> MeetingResponse:
    return MeetingResponse(
        meeting_id=meeting_id,
        summary="Placeholder summary",
        decisions=[],
        action_items=[],
        transcript=[],
    )


@router.get("/search", response_model=SearchResponse)
def search(
    q: str = Query(..., min_length=1),
    speaker: Optional[str] = None,
    from_date: Optional[str] = None,
    role: str = Depends(get_current_role),
) -> SearchResponse:
    results = hybrid_search(q, vector_store, local_documents)
    return SearchResponse(query=q, results=[SearchResponseItem(**item) for item in results])


@router.post("/meetings/{meeting_id}/corrections")
def submit_correction(meeting_id: str, correction: CorrectionRequest, role: str = Depends(get_current_role)) -> Dict[str, Any]:
    return {"meeting_id": meeting_id, "status": "correction_received", "role": role}


@router.get("/meetings/{meeting_id}/action-items")
def get_action_items(meeting_id: str) -> Dict[str, List[Dict[str, Any]]]:
    return {"meeting_id": meeting_id, "action_items": []}
