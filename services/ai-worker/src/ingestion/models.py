from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional


class JobStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    DONE = "DONE"
    FAILED = "FAILED"


@dataclass
class IngestionJob:
    job_id: str
    source_path: str
    created_at: str
    status: JobStatus = JobStatus.PENDING
    checksum: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(cls, source_path: Path, checksum: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> "IngestionJob":
        return cls(
            job_id=str(datetime.utcnow().timestamp()).replace(".", ""),
            source_path=str(source_path.resolve()),
            created_at=datetime.utcnow().isoformat() + "Z",
            checksum=checksum,
            metadata=metadata or {},
        )

    @classmethod
    def load(cls, data: Dict[str, Any]) -> "IngestionJob":
        data = data.copy()
        data["status"] = JobStatus(data["status"])
        return cls(**data)

    def serialize(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)

    @classmethod
    def deserialize(cls, payload: str) -> "IngestionJob":
        data = json.loads(payload)
        return cls.load(data)
