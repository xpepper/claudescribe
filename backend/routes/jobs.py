import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from backend.models.schemas import TranscriptionStatusResponse
from backend.services import storage_service, transcription_service

router = APIRouter()

ALLOWED_EXTENSIONS = {".mp3", ".mp4", ".m4a", ".wav", ".ogg", ".flac", ".webm", ".mkv"}


@router.post("/api/transcriptions", status_code=201)
async def upload_transcription(
    file: UploadFile = File(...),
    model: str = Form(default="turbo"),
):
    # Validate extension
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {suffix}")

    transcription_id = str(uuid.uuid4())

    # Create directory and save audio
    storage_service.create_transcription_dir(transcription_id)
    file_bytes = await file.read()
    audio_path = storage_service.save_audio(transcription_id, file_bytes, suffix.lstrip("."))

    # Write initial JSON
    now = datetime.now(timezone.utc).isoformat()
    initial_data = {
        "id": transcription_id,
        "title": file.filename,
        "original_filename": file.filename,
        "model": model,
        "language": None,
        "status": "pending",
        "progress": 0.0,
        "created_at": now,
        "completed_at": None,
        "error": None,
        "duration_seconds": None,
        "segments": [],
    }
    storage_service.write_transcription(transcription_id, initial_data)

    # Enqueue transcription
    transcription_service.enqueue(transcription_id, audio_path, model)

    return JSONResponse(
        status_code=201,
        content={"id": transcription_id, "status": "pending"},
    )


@router.get("/api/transcriptions/{transcription_id}/status", response_model=TranscriptionStatusResponse)
def get_status(transcription_id: str):
    status = transcription_service.get_status(transcription_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Transcription not found")
    return status
