from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class DecisionItem:
    decision: str
    context: Optional[str] = None
    speaker: Optional[str] = None


@dataclass
class ActionItem:
    task: str
    assignee: Optional[str] = None
    due: Optional[str] = None


@dataclass
class MeetingSummary:
    meeting_id: str
    summary: str
    decisions: List[DecisionItem] = field(default_factory=list)
    action_items: List[ActionItem] = field(default_factory=list)
    transcript: List[Dict[str, Any]] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "meeting_id": self.meeting_id,
            "summary": self.summary,
            "decisions": [
                {
                    "decision": item.decision,
                    "context": item.context,
                    "speaker": item.speaker,
                }
                for item in self.decisions
            ],
            "action_items": [
                {
                    "task": item.task,
                    "assignee": item.assignee,
                    "due": item.due,
                }
                for item in self.action_items
            ],
            "transcript": self.transcript,
            "created_at": self.created_at,
        }
