from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from api.endpoints import router
from pipeline.orchestrator import MeetingPipeline
from rag.store import MeetingStore


@asynccontextmanager
async def lifespan(app: FastAPI):
    store = MeetingStore()
    app.state.pipeline = MeetingPipeline(store=store)
    app.state.store = store
    yield


app = FastAPI(title="Meeting Knowledge Hub", lifespan=lifespan)
app.include_router(router)
app.mount("/ui", StaticFiles(directory="ui", html=True), name="ui")


@app.get("/")
def root() -> dict:
    return {"status": "ok", "service": "Meeting Knowledge Hub"}
