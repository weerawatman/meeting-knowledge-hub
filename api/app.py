from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from api.endpoints import router

app = FastAPI(title="Meeting Knowledge Hub")
app.include_router(router)
app.mount("/ui", StaticFiles(directory="ui", html=True), name="ui")


@app.get("/")
def root() -> dict:
    return {"status": "ok", "service": "Meeting Knowledge Hub"}
