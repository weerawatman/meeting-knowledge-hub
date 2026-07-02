"""VRAM Model Lifecycle Manager for RTX 4060 (8GB) constraint.

Sequential loading strategy:
  1. Load Whisper → STT → flush VRAM → unload
  2. Load LLaMA via Ollama → Summarize → done

Embedding model (bge-small) always runs on CPU — never touches VRAM.
Live Capture sessions hold HIGH priority and block Batch jobs from loading Whisper.
"""
from __future__ import annotations

import threading
from enum import Enum
from typing import Optional

_whisper_model = None
_whisper_lock = threading.Lock()

# Priority levels: lower number = higher priority
PRIORITY_LIVE = 1
PRIORITY_BATCH = 5
PRIORITY_DIGEST = 9


class ModelState(Enum):
    UNLOADED = "unloaded"
    LOADED = "loaded"
    RESERVED_LIVE = "reserved_live"


_whisper_state = ModelState.UNLOADED
_state_lock = threading.Lock()


def reserve_for_live_capture() -> bool:
    """Mark Whisper slot as reserved for a Live Capture session.
    Returns True if reservation succeeded (no other session active)."""
    with _state_lock:
        if _whisper_state == ModelState.RESERVED_LIVE:
            return False
        globals()["_whisper_state"] = ModelState.RESERVED_LIVE
        return True


def release_live_capture() -> None:
    """Release Live Capture reservation so Batch jobs can proceed."""
    with _state_lock:
        globals()["_whisper_state"] = ModelState.UNLOADED
    _flush_vram()


def is_vram_available_for_batch() -> bool:
    """Batch jobs may only load Whisper if no Live session holds the slot."""
    with _state_lock:
        return _whisper_state != ModelState.RESERVED_LIVE


def load_whisper(model_name: str = "small"):
    """Load Whisper into VRAM (or CPU int8 if no CUDA). Thread-safe singleton."""
    global _whisper_model, _whisper_state
    with _whisper_lock:
        if _whisper_model is not None:
            return _whisper_model
        from faster_whisper import WhisperModel
        try:
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
        except ImportError:
            device = "cpu"
        compute = "float16" if device == "cuda" else "int8"
        _whisper_model = WhisperModel(model_name, device=device, compute_type=compute)
        with _state_lock:
            _whisper_state = ModelState.LOADED
        return _whisper_model


def unload_whisper() -> None:
    """Unload Whisper from VRAM and flush GPU memory."""
    global _whisper_model, _whisper_state
    with _whisper_lock:
        _whisper_model = None
        with _state_lock:
            _whisper_state = ModelState.UNLOADED
    _flush_vram()


def _flush_vram() -> None:
    """Release GPU memory after model unload."""
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except ImportError:
        pass


def get_whisper_model(model_name: str = "small"):
    """Get (or lazily load) the Whisper model instance."""
    global _whisper_model
    if _whisper_model is None:
        return load_whisper(model_name)
    return _whisper_model
