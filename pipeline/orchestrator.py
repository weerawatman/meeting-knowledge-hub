from __future__ import annotations

import json
import os
import threading
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional

from ingestion.processor import extract_audio
from llm.generator import generate_summary
from rag.store import MeetingStore
from speaker_id.diarize import diarize_audio
from speaker_id.models import SpeakerSegment
from stt.models import TranscriptSegment
from stt.pipeline import run_stt_pipeline

DATA_DIR = Path(os.getenv("DATA_DIR", "./data"))
RESULTS_DIR = DATA_DIR / "results"
WORK_DIR = DATA_DIR / "workdir"

_VIDEO_SUFFIXES = {".mp4", ".mkv", ".mov", ".avi"}


def _seconds_to_hms(seconds: float) -> str:
    h = int(seconds) // 3600
    m = (int(seconds) % 3600) // 60
    s = int(seconds) % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def _assign_speakers(
    transcript_segs: List[TranscriptSegment],
    diarization_segs: List[SpeakerSegment],
) -> List[Dict[str, Any]]:
    """Match each transcript segment to the diarization segment that best overlaps it."""
    merged: List[Dict[str, Any]] = []
    for tseg in transcript_segs:
        t_mid = (tseg.start_time + tseg.end_time) / 2.0
        speaker = "SPEAKER_01"
        for dseg in diarization_segs:
            if dseg.start_time <= t_mid <= dseg.end_time:
                speaker = dseg.speaker_id
                break
        merged.append({
            "text": tseg.text.strip(),
            "start_time": tseg.start_time,
            "end_time": tseg.end_time,
            "speaker": speaker,
        })
    return merged


class MeetingPipeline:
    def __init__(self, store: Optional[MeetingStore] = None):
        self._results: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        self._store = store or MeetingStore()
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        WORK_DIR.mkdir(parents=True, exist_ok=True)

    def submit(self, meeting_id: str, source_path: Path) -> str:
        with self._lock:
            self._results[meeting_id] = {"status": "queued", "stage": "waiting"}
        thread = threading.Thread(
            target=self._run,
            args=(meeting_id, source_path),
            daemon=True,
        )
        thread.start()
        return meeting_id

    def get_status(self, meeting_id: str) -> Dict[str, Any]:
        with self._lock:
            return dict(self._results.get(meeting_id, {"status": "not_found"}))

    def get_result(self, meeting_id: str) -> Optional[Dict[str, Any]]:
        result_file = RESULTS_DIR / f"{meeting_id}.json"
        if result_file.exists():
            return json.loads(result_file.read_text(encoding="utf-8"))
        return None

    def _set_stage(self, meeting_id: str, stage: str) -> None:
        with self._lock:
            self._results[meeting_id] = {"status": "processing", "stage": stage}

    def _run(self, meeting_id: str, source_path: Path) -> None:
        try:
            work_dir = WORK_DIR / meeting_id
            work_dir.mkdir(parents=True, exist_ok=True)

            # Step 1: Extract audio from video if needed
            self._set_stage(meeting_id, "audio_prep")
            if source_path.suffix.lower() in _VIDEO_SUFFIXES:
                audio_path = extract_audio(source_path, work_dir)
            else:
                audio_path = source_path

            # Step 2: STT — returns TranscriptResult
            self._set_stage(meeting_id, "stt")
            transcript_result = run_stt_pipeline(meeting_id, audio_path, work_dir)

            # Step 3: Speaker diarization using transcript segment dicts
            self._set_stage(meeting_id, "diarization")
            seg_dicts = [
                {"start_time": s.start_time, "end_time": s.end_time, "text": s.text}
                for s in transcript_result.segments
            ]
            diarization = diarize_audio(
                audio_path, meeting_id, transcript_segments=seg_dicts
            )

            # Step 4: Merge speaker labels
            merged = _assign_speakers(transcript_result.segments, diarization.segments)

            # Step 5: Format speaker-attributed transcript text
            lines = []
            for seg in merged:
                if seg["text"]:
                    ts = _seconds_to_hms(seg["start_time"])
                    lines.append(f"[{ts}] {seg['speaker']}: {seg['text']}")
            full_text = "\n".join(lines)

            # Step 6: LLM summarization
            self._set_stage(meeting_id, "summarizing")
            meeting_summary = generate_summary(full_text, meeting_id)

            # Step 7: Index in RAG store
            self._set_stage(meeting_id, "indexing")
            participants = ", ".join(sp.display_name for sp in diarization.speakers)
            self._store.upsert_meeting(
                meeting_id=meeting_id,
                title=meeting_summary.summary[:120] if meeting_summary.summary else meeting_id,
                date=None,
                participants=participants,
                status="done",
                transcript=full_text,
                metadata={"source": str(source_path)},
            )

            # Step 8: Persist complete result JSON
            result = {
                "meeting_id": meeting_id,
                "status": "done",
                "transcript": [
                    {
                        "timestamp": _seconds_to_hms(seg["start_time"]),
                        "speaker": seg["speaker"],
                        "text": seg["text"],
                    }
                    for seg in merged
                    if seg["text"]
                ],
                "summary": meeting_summary.summary,
                "decisions": [
                    {"decision": d.decision, "context": d.context, "speaker": d.speaker}
                    for d in meeting_summary.decisions
                ],
                "action_items": [
                    {"task": a.task, "assignee": a.assignee, "due": a.due}
                    for a in meeting_summary.action_items
                ],
                "speakers": [
                    {"speaker_id": sp.speaker_id, "display_name": sp.display_name}
                    for sp in diarization.speakers
                ],
            }
            result_path = RESULTS_DIR / f"{meeting_id}.json"
            result_path.write_text(
                json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
            )

            with self._lock:
                self._results[meeting_id] = {"status": "done", "stage": "complete"}

        except Exception:
            err = traceback.format_exc()
            with self._lock:
                self._results[meeting_id] = {
                    "status": "failed",
                    "stage": "error",
                    "error": err,
                }
