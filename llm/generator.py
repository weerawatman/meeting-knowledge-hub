from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from llm.models import ActionItem, DecisionItem, MeetingSummary
from llm.prompting import build_summary_prompt, split_transcript


def generate_summary(transcript_text: str, meeting_id: str) -> MeetingSummary:
    chunks = split_transcript(transcript_text)
    decisions: List[DecisionItem] = []
    action_items: List[ActionItem] = []
    for chunk in chunks:
        # Placeholder: actual inference would call an LLM service
        decisions.append(DecisionItem(decision="Example decision", context=chunk[:100], speaker="SPEAKER_01"))
        action_items.append(ActionItem(task="Example action item", assignee="Unknown", due=None))

    return MeetingSummary(
        meeting_id=meeting_id,
        summary="This is a placeholder summary.",
        decisions=decisions,
        action_items=action_items,
        transcript=[{"speaker": "SPEAKER_01", "text": transcript_text, "timestamp": "00:00:00"}],
    )


def generate_summary_prompted(transcript_text: str) -> str:
    return build_summary_prompt(transcript_text)
