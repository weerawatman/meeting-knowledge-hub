from __future__ import annotations

from pydantic import BaseModel
from typing import Any, Dict, List, Optional


class IngestRequest(BaseModel):
    source_path: str
    metadata: Optional[Dict[str, Any]] = None


class MeetingResponse(BaseModel):
    meeting_id: str
    summary: str
    decisions: List[Dict[str, Any]]
    action_items: List[Dict[str, Any]]
    transcript: List[Dict[str, Any]]


class SearchResponseItem(BaseModel):
    document_id: str
    score: float
    text: str
    metadata: Optional[Dict[str, Any]] = None


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResponseItem]


class CorrectionRequest(BaseModel):
    original_text: str
    corrected_text: str
    correction_type: str
