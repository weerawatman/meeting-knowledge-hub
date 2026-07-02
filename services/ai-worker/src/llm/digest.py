"""Executive Digest — Two-Pass Map-Reduce for multi-document analysis.

Pass 1 (Map): For each document chunk, ask LLM to extract structured items
  tagged with chunk_type: "decision" | "task" | "info"

Pass 2 (Reduce): Collect ALL decision/task chunks (no semantic filtering —
  metadata-driven to guarantee 100% recall) and synthesize final report.

Usage:
    from llm.digest import run_executive_digest
    result = run_executive_digest(doc_chunks)
    # result = { "resolutions": [...], "pending_tasks": [...], "summary": "..." }
"""
from __future__ import annotations

import json
from typing import Any, Dict, List

from llm.summarize import _call_ollama

# ---------------------------------------------------------------------------
# Pass 1 prompt — map each chunk
# ---------------------------------------------------------------------------
PASS1_PROMPT = """You are an executive meeting analyst. Analyze this document excerpt and extract structured items.
Respond ONLY with valid JSON — no markdown, no explanation.

Return this exact structure:
{{
  "items": [
    {{
      "chunk_type": "decision",
      "content": "The specific resolution or decision made",
      "context": "brief context (who, what project)"
    }},
    {{
      "chunk_type": "task",
      "content": "The specific task or pending deliverable",
      "assignee": "person responsible or UNKNOWN",
      "due": "deadline or null"
    }}
  ]
}}

If no decisions or tasks are found, return {{"items": []}}.

Document excerpt (page {page}, source: {source}):
{text}"""

# ---------------------------------------------------------------------------
# Pass 2 prompt — reduce all tagged items into final digest
# ---------------------------------------------------------------------------
PASS2_PROMPT = """You are an executive report writer. Synthesize these pre-extracted items into a final Executive Digest.
Respond ONLY with valid JSON — no markdown, no explanation.

Return this exact structure:
{{
  "summary": "2-3 sentence executive overview in Thai covering all documents",
  "resolutions": [
    {{"resolution": "complete statement of decision", "context": "source document and context"}}
  ],
  "pending_tasks": [
    {{"task": "complete task description", "assignee": "person or UNKNOWN", "due": "deadline or null", "source": "document name"}}
  ]
}}

Rules:
- Include ALL decisions and tasks — do NOT omit any item
- Resolutions must capture the exact commitment made, not a paraphrase
- Pending tasks must be actionable and assigned where possible

Extracted items from {doc_count} document(s):
{items_json}"""


def _run_pass1_chunk(page: int, source: str, text: str) -> List[Dict[str, Any]]:
    """Run Pass 1 on a single document chunk. Returns list of tagged items."""
    prompt = PASS1_PROMPT.format(page=page, source=source, text=text[:6000])
    raw = _call_ollama(prompt, format_json=True)
    if raw is None:
        return []
    try:
        data = json.loads(raw)
        return data.get("items", [])
    except json.JSONDecodeError:
        return []


def _run_pass2_reduce(all_items: List[Dict[str, Any]], doc_count: int) -> Dict[str, Any]:
    """Run Pass 2: synthesize all tagged items into final Executive Digest."""
    if not all_items:
        return {
            "summary": "เอกสารที่อัปโหลดไม่พบมติหรืองานค้างส่งที่ชัดเจน",
            "resolutions": [],
            "pending_tasks": [],
        }

    # Filter to only decision and task items (guaranteed recall)
    decisions = [i for i in all_items if i.get("chunk_type") == "decision"]
    tasks = [i for i in all_items if i.get("chunk_type") == "task"]
    combined = decisions + tasks

    items_json = json.dumps(combined, ensure_ascii=False, indent=2)
    prompt = PASS2_PROMPT.format(doc_count=doc_count, items_json=items_json)
    raw = _call_ollama(prompt, format_json=True)
    if raw is not None:
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass
    # Fallback when Ollama unavailable: return raw extracted items directly
    return {
        "summary": f"สังเคราะห์จาก {doc_count} เอกสาร พบ {len(decisions)} มติ และ {len(tasks)} งาน",
        "resolutions": [{"resolution": d.get("content", ""), "context": d.get("context", "")} for d in decisions],
        "pending_tasks": [{"task": t.get("content", ""), "assignee": t.get("assignee", "UNKNOWN"), "due": t.get("due"), "source": t.get("source", "")} for t in tasks],
    }


def run_executive_digest(
    doc_chunks: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Run Two-Pass Executive Digest on a list of document page chunks.

    Args:
        doc_chunks: list of { page, text, source } dicts from doc_extractor

    Returns:
        { summary, resolutions, pending_tasks, pass1_item_count }
    """
    doc_sources = set(c.get("source", "unknown") for c in doc_chunks)
    doc_count = len(doc_sources)

    # Pass 1: map each chunk in parallel (sequential for VRAM simplicity)
    all_items: List[Dict[str, Any]] = []
    for chunk in doc_chunks:
        items = _run_pass1_chunk(
            page=chunk.get("page", 0),
            source=chunk.get("source", "unknown"),
            text=chunk.get("text", ""),
        )
        # Attach source to task items for traceability
        for item in items:
            if "source" not in item:
                item["source"] = chunk.get("source", "unknown")
        all_items.extend(items)

    # Pass 2: reduce
    result = _run_pass2_reduce(all_items, doc_count)
    result["pass1_item_count"] = len(all_items)
    return result
