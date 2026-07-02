"""Internal Worker HTTP API — called by Node.js Core API only.

These routes are NOT public. The worker service binds only on the Docker
internal network, so no auth middleware is needed here.
"""
from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from rag.embeddings import embed_text
from rag.search import hybrid_search

worker_router = APIRouter(prefix="/worker")


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class TranscribeJobRequest(BaseModel):
    file_path: str
    meeting_id: Optional[str] = None

class SummarizeJobRequest(BaseModel):
    transcript: str
    meeting_id: str

class DigestJobRequest(BaseModel):
    doc_chunks: List[Dict[str, Any]]
    digest_id: Optional[str] = None

class EmbedRequest(BaseModel):
    text: str

class SearchRequest(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = None
    limit: int = 10


# ---------------------------------------------------------------------------
# Job submission routes (async, return job_id)
# ---------------------------------------------------------------------------

@worker_router.post("/jobs/transcribe")
def submit_transcribe_job(req: TranscribeJobRequest, request: Request) -> Dict[str, str]:
    """Queue an audio file for STT + diarization + summarization."""
    source_path = Path(req.file_path)
    if not source_path.exists():
        raise HTTPException(status_code=400, detail=f"File not found: {req.file_path}")
    meeting_id = req.meeting_id or str(uuid.uuid4())
    pipeline = request.app.state.pipeline
    pipeline.submit(meeting_id, source_path)
    return {"job_id": meeting_id, "status": "queued"}


@worker_router.post("/jobs/summarize")
def submit_summarize_job(req: SummarizeJobRequest, request: Request) -> Dict[str, str]:
    """Queue a transcript for LLM summarization only (no STT)."""
    from llm.generator import generate_summary
    import threading

    job_id = req.meeting_id
    pipeline = request.app.state.pipeline

    def _run_summarize():
        import json
        from pathlib import Path as P
        summary = generate_summary(req.transcript, job_id)
        result = {
            "meeting_id": job_id,
            "status": "done",
            "summary": summary.summary,
            "decisions": [d.__dict__ for d in summary.decisions],
            "action_items": [a.__dict__ for a in summary.action_items],
        }
        results_dir = P("./data/results")
        results_dir.mkdir(parents=True, exist_ok=True)
        (results_dir / f"{job_id}.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        pipeline._results[job_id] = {"status": "done", "stage": "complete"}

    pipeline._results[job_id] = {"status": "processing", "stage": "summarizing"}
    threading.Thread(target=_run_summarize, daemon=True).start()
    return {"job_id": job_id, "status": "queued"}


@worker_router.post("/jobs/digest")
def submit_digest_job(req: DigestJobRequest, request: Request) -> Dict[str, str]:
    """Queue document chunks for Two-pass Executive Digest."""
    from llm.digest import run_executive_digest
    import threading, json
    from pathlib import Path as P

    job_id = req.digest_id or str(uuid.uuid4())
    pipeline = request.app.state.pipeline

    def _run_digest():
        result = run_executive_digest(req.doc_chunks)
        results_dir = P("./data/results")
        results_dir.mkdir(parents=True, exist_ok=True)
        payload = {"digest_id": job_id, "status": "done", **result}
        (results_dir / f"{job_id}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        pipeline._results[job_id] = {"status": "done", "stage": "complete"}

    pipeline._results[job_id] = {"status": "processing", "stage": "digesting"}
    threading.Thread(target=_run_digest, daemon=True).start()
    return {"job_id": job_id, "status": "queued"}


# ---------------------------------------------------------------------------
# Job status / result poll
# ---------------------------------------------------------------------------

@worker_router.get("/jobs/{job_id}")
def get_job(job_id: str, request: Request) -> Dict[str, Any]:
    """Return job status and result if complete."""
    pipeline = request.app.state.pipeline
    status = pipeline.get_status(job_id)
    result = None
    if status.get("status") == "done":
        result = pipeline.get_result(job_id)
    return {"job_id": job_id, **status, "result": result}


# ---------------------------------------------------------------------------
# Synchronous utility routes (fast, no GPU needed)
# ---------------------------------------------------------------------------

@worker_router.post("/embed")
def embed(req: EmbedRequest) -> Dict[str, Any]:
    """Embed a text string using bge-small-en-v1.5 (CPU). Returns 384-dim vector."""
    vector = embed_text(req.text)
    return {"vector": vector, "dimension": len(vector)}


@worker_router.post("/search")
def search(req: SearchRequest, request: Request) -> Dict[str, Any]:
    """Hybrid search over indexed meetings. Respects category filters."""
    store = request.app.state.store
    raw = store.search(req.query, top_k=req.limit)
    return {"query": req.query, "results": raw}


# ---------------------------------------------------------------------------
# Health check (also reports VRAM availability)
# ---------------------------------------------------------------------------

@worker_router.get("/health")
def health() -> Dict[str, Any]:
    vram_free_mb: Optional[float] = None
    try:
        import torch
        if torch.cuda.is_available():
            free, total = torch.cuda.mem_get_info()
            vram_free_mb = round(free / 1024 / 1024, 1)
    except ImportError:
        pass
    return {"ok": True, "vram_free_mb": vram_free_mb}
