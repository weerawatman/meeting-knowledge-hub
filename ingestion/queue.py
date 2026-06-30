from __future__ import annotations

import json
from pathlib import Path
from shutil import move
from typing import Iterator, Optional

from ingestion.models import IngestionJob, JobStatus


class FileQueue:
    def __init__(self, queue_root: Path):
        self.queue_root = queue_root
        self.pending_dir = queue_root / "pending"
        self.processing_dir = queue_root / "processing"
        self.failed_dir = queue_root / "failed"
        self.done_dir = queue_root / "done"
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        for target in (
            self.pending_dir,
            self.processing_dir,
            self.failed_dir,
            self.done_dir,
        ):
            target.mkdir(parents=True, exist_ok=True)

    def enqueue(self, job: IngestionJob) -> Path:
        job_path = self.pending_dir / f"{job.job_id}.json"
        job_path.write_text(job.serialize(), encoding="utf-8")
        return job_path

    def dequeue(self) -> Optional[IngestionJob]:
        pending_jobs = sorted(self.pending_dir.glob("*.json"))
        if not pending_jobs:
            return None
        job_file = pending_jobs[0]
        processing_file = self.processing_dir / job_file.name
        move(str(job_file), str(processing_file))
        return self._load_job(processing_file)

    def mark_done(self, job: IngestionJob) -> None:
        job.status = JobStatus.DONE
        self._update_job_file(job, self.done_dir)

    def mark_failed(self, job: IngestionJob, error: str) -> None:
        job.status = JobStatus.FAILED
        job.error = error
        self._update_job_file(job, self.failed_dir)

    def list_pending(self) -> Iterator[IngestionJob]:
        for job_file in sorted(self.pending_dir.glob("*.json")):
            yield self._load_job(job_file)

    def find_by_source(self, source_path: Path) -> Optional[IngestionJob]:
        query = str(source_path.resolve())
        for directory in (self.pending_dir, self.processing_dir, self.done_dir, self.failed_dir):
            for job_file in directory.glob("*.json"):
                job = self._load_job(job_file)
                if job.source_path == query:
                    return job
        return None

    def _load_job(self, path: Path) -> IngestionJob:
        payload = path.read_text(encoding="utf-8")
        return IngestionJob.deserialize(payload)

    def _update_job_file(self, job: IngestionJob, target_directory: Path) -> Path:
        target_path = target_directory / f"{job.job_id}.json"
        if target_path.exists():
            target_path.unlink()
        target_path.write_text(job.serialize(), encoding="utf-8")
        return target_path
