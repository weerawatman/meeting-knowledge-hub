from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.endpoints import router
from api.worker_routes import worker_router
from pipeline.orchestrator import MeetingPipeline
from rag.store import MeetingStore


@asynccontextmanager
async def lifespan(app: FastAPI):
    store = MeetingStore()
    app.state.pipeline = MeetingPipeline(store=store)
    app.state.store = store
    yield


# Internal worker service — not mounted with StaticFiles (no UI served here)
app = FastAPI(title="Meeting Knowledge Hub — AI Worker", lifespan=lifespan)
app.include_router(router)          # existing routes (upload, search, etc.)
app.include_router(worker_router)   # new Node.js-facing worker routes


@app.get("/")
def root() -> dict:
    return {"status": "ok", "service": "AI Worker"}
