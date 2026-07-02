from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlmodel import Session, select

from rag.db import init_db
from rag.embeddings import embed_text
from rag.models import DocumentEntry, FeedbackEntry, MeetingMetadata
from rag.vector_store import VectorStore

DEFAULT_DB_URL = "sqlite:///./meeting_knowledge_hub.db"


class MeetingStore:
    def __init__(self, db_url: str = DEFAULT_DB_URL, vector_host: str = "127.0.0.1", vector_port: int = 6333):
        self.engine = init_db(db_url)
        self.vector_store = VectorStore(host=vector_host, port=vector_port)

    def upsert_meeting(
        self,
        meeting_id: str,
        title: Optional[str] = None,
        date: Optional[str] = None,
        participants: Optional[str] = None,
        status: Optional[str] = None,
        transcript: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        metadata = metadata or {}
        with Session(self.engine) as session:
            statement = select(MeetingMetadata).where(MeetingMetadata.meeting_id == meeting_id)
            result = session.exec(statement).first()
            if result is None:
                result = MeetingMetadata(
                    meeting_id=meeting_id,
                    title=title,
                    date=date,
                    participants=participants,
                    status=status,
                )
                session.add(result)
            else:
                result.title = title or result.title
                result.date = date or result.date
                result.participants = participants or result.participants
                result.status = status or result.status
            session.commit()

            if transcript is not None:
                document_id = f"{meeting_id}::transcript"
                document = session.exec(
                    select(DocumentEntry).where(DocumentEntry.document_id == document_id)
                ).first()
                if document is None:
                    document = DocumentEntry(
                        meeting_id=meeting_id,
                        document_id=document_id,
                        content=transcript,
                        metadata_json=str(metadata),
                    )
                    session.add(document)
                else:
                    document.content = transcript
                    document.metadata_json = str(metadata)
                session.commit()
                self.vector_store.upsert(document_id, transcript, metadata, embed_text(transcript))

    def add_feedback(
        self,
        meeting_id: str,
        original_text: str,
        corrected_text: str,
        correction_type: str,
    ) -> FeedbackEntry:
        with Session(self.engine) as session:
            feedback = FeedbackEntry(
                meeting_id=meeting_id,
                original_text=original_text,
                corrected_text=corrected_text,
                correction_type=correction_type,
            )
            session.add(feedback)
            session.commit()
            session.refresh(feedback)
            return feedback

    def get_meeting(self, meeting_id: str) -> Dict[str, Any]:
        with Session(self.engine) as session:
            metadata = session.exec(
                select(MeetingMetadata).where(MeetingMetadata.meeting_id == meeting_id)
            ).first()
            if metadata is None:
                return {
                    "meeting_id": meeting_id,
                    "summary": "",
                    "decisions": [],
                    "action_items": [],
                    "transcript": [],
                }
            docs = session.exec(select(DocumentEntry).where(DocumentEntry.meeting_id == meeting_id)).all()
            transcript = []
            for doc in docs:
                transcript.append({"document_id": doc.document_id, "content": doc.content, "metadata": doc.metadata_json})
            return {
                "meeting_id": meeting_id,
                "summary": metadata.title or "",
                "decisions": [],
                "action_items": [],
                "transcript": transcript,
            }

    def search(self, query: str, top_k: int = 5, metadata_filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        return self.vector_store.search(embed_text(query), top_k=top_k, metadata_filter=metadata_filter)
