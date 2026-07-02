from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from llm.models import ActionItem, DecisionItem, MeetingSummary
from llm.prompting import build_summary_prompt, split_transcript
from llm.summarize import summarize_transcript


def generate_summary(transcript_text: str, meeting_id: str) -> MeetingSummary:
    chunks = split_transcript(transcript_text)
    all_decisions: List[DecisionItem] = []
    all_action_items: List[ActionItem] = []
    summaries: List[str] = []

    for chunk in chunks:
        result = summarize_transcript(chunk)
        if result.get("summary"):
            summaries.append(result["summary"])
        for d in result.get("decisions", []):
            all_decisions.append(DecisionItem(
                decision=d.get("decision", ""),
                context=d.get("context", ""),
                speaker=d.get("speaker", "UNKNOWN"),
            ))
        for a in result.get("action_items", []):
            all_action_items.append(ActionItem(
                task=a.get("task", ""),
                assignee=a.get("assignee", "UNKNOWN"),
                due=a.get("due"),
            ))

    combined_summary = " ".join(summaries) if summaries else transcript_text[:300]

    return MeetingSummary(
        meeting_id=meeting_id,
        summary=combined_summary,
        decisions=all_decisions,
        action_items=all_action_items,
        transcript=[{"speaker": "UNKNOWN", "text": transcript_text, "timestamp": "00:00:00"}],
    )


def generate_summary_prompted(transcript_text: str) -> str:
    return build_summary_prompt(transcript_text)
