from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.routes import jobs, transcriptions
from backend.services import storage_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Reset orphaned processing transcriptions on startup
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
