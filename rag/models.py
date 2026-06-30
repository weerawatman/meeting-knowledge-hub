from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class MeetingMetadata(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    meeting_id: str = Field(index=True, unique=True)
    title: Optional[str] = None
    date: Optional[str] = None
    participants: Optional[str] = None
    status: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class DocumentEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    meeting_id: str = Field(index=True)
    document_id: str = Field(index=True)
    content: str
    metadata: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class FeedbackEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    meeting_id: str = Field(index=True)
    original_text: str
    corrected_text: str
    correction_type: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
