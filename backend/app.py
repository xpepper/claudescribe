from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from backend.routes import jobs, transcriptions
from backend.services import storage_service


DIST_DIR = Path(__file__).parent.parent / "frontend" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    for item in storage_service.list_transcriptions():
        if item.get("status") == "processing":
            item["status"] = "failed"
            item["error"] = "Server restarted during transcription"
            storage_service.write_transcription(item["id"], item)
    yield


app = FastAPI(title="Claudescribe", lifespan=lifespan)

app.include_router(jobs.router)
app.include_router(transcriptions.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


def _serve_spa() -> FileResponse | dict:
    index = DIST_DIR / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return {"error": "Frontend not built. Run: make build"}


@app.get("/", include_in_schema=False)
def root():
    return _serve_spa()


@app.get("/{full_path:path}", include_in_schema=False)
def spa_fallback(full_path: str):
    # Serve static file if it exists
    candidate = DIST_DIR / full_path
    if candidate.is_file():
        return FileResponse(str(candidate))
    # SPA fallback: serve index.html
    index = DIST_DIR / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return {"error": "Frontend not built. Run: make build"}
