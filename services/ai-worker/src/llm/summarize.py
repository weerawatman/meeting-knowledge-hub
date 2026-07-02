from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

import httpx

from llm.prompting import build_summary_json_prompt

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")


def _call_ollama(prompt: str, format_json: bool = False) -> Optional[str]:
    """Low-level Ollama call. Returns raw content string or None on failure."""
    try:
        payload: Dict[str, Any] = {
            "model": OLLAMA_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {"temperature": 0.1},
        }
        if format_json:
            payload["format"] = "json"
        response = httpx.post(
            f"{OLLAMA_HOST}/api/chat",
            json=payload,
            timeout=120.0,
        )
        response.raise_for_status()
        return response.json()["message"]["content"]
    except (httpx.ConnectError, httpx.ConnectTimeout, httpx.HTTPError, KeyError):
        return None


def summarize_transcript(transcript: str) -> Dict[str, Any]:
    """Call Ollama LLM to summarize transcript. Falls back to raw excerpt on failure."""
    if not transcript or not transcript.strip():
        return {"summary": "", "decisions": [], "action_items": []}

    prompt = build_summary_json_prompt(transcript)
    try:
        response = httpx.post(
            f"{OLLAMA_HOST}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "format": "json",
                "options": {"temperature": 0.1},
            },
            timeout=120.0,
        )
        response.raise_for_status()
        content = response.json()["message"]["content"]
        result = json.loads(content)
        return {
            "summary": result.get("summary", ""),
            "decisions": result.get("decisions", []),
            "action_items": result.get("action_items", []),
        }
    except (httpx.ConnectError, httpx.ConnectTimeout):
        excerpt = transcript[:500].strip()
        return {
            "summary": f"[Ollama ไม่พร้อมใช้งาน — แสดงส่วนย่อของการประชุม]\n\n{excerpt}",
            "decisions": [],
            "action_items": [],
        }
    except (json.JSONDecodeError, KeyError):
        excerpt = transcript[:500].strip()
        return {
            "summary": excerpt,
            "decisions": [],
            "action_items": [],
        }
    except Exception:
        return {"summary": transcript[:300], "decisions": [], "action_items": []}
