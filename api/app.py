from fastapi import FastAPI

app = FastAPI(title="Meeting Knowledge Hub")


@app.get("/")
def root() -> dict:
    return {"status": "ok", "service": "Meeting Knowledge Hub"}
