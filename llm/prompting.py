from __future__ import annotations

from typing import Dict, List


SUMMARY_PROMPT_TEMPLATE = """
You are a meeting intelligence assistant. Summarize the transcript in Thai.
Provide:
- A concise meeting summary
- A list of decisions
- A list of action items with assignee and due date if available

Transcript:
{transcript}
"""

SUMMARY_JSON_PROMPT_TEMPLATE = """You are a meeting intelligence assistant. Analyze the following meeting transcript and respond ONLY with valid JSON — no explanation, no markdown, no extra text.

Return this exact JSON structure:
{{
  "summary": "concise paragraph summary of the meeting in Thai",
  "decisions": [
    {{"decision": "what was decided", "context": "brief context", "speaker": "who decided or UNKNOWN"}}
  ],
  "action_items": [
    {{"task": "what needs to be done", "assignee": "who is responsible or UNKNOWN", "due": "due date or null"}}
  ]
}}

Transcript:
{transcript}"""


def build_summary_prompt(transcript: str) -> str:
    return SUMMARY_PROMPT_TEMPLATE.format(transcript=transcript)


def build_summary_json_prompt(transcript: str) -> str:
    return SUMMARY_JSON_PROMPT_TEMPLATE.format(transcript=transcript)


def split_transcript(transcript: str, max_chunk_chars: int = 8000) -> List[str]:
    chunks: List[str] = []
    start = 0
    while start < len(transcript):
        end = min(len(transcript), start + max_chunk_chars)
        chunks.append(transcript[start:end])
        start = end
    return chunks
