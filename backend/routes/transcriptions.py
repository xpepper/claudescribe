import json
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel

from backend.models.schemas import TranscriptionListItem, TranscriptionRecord
from backend.services import storage_service

router = APIRouter()


class RenameRequest(BaseModel):
    title: str


@router.get("/api/transcriptions", response_model=list[TranscriptionListItem])
def list_transcriptions():
    return storage_service.list_transcriptions()


@router.get("/api/transcriptions/{transcription_id}", response_model=TranscriptionRecord)
def get_transcription(transcription_id: str):
    try:
        return storage_service.read_transcription(transcription_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Transcription not found")


@router.patch("/api/transcriptions/{transcription_id}")
def rename_transcription(transcription_id: str, body: RenameRequest):
    try:
        data = storage_service.read_transcription(transcription_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Transcription not found")
    data["title"] = body.title
    storage_service.write_transcription(transcription_id, data)
    return {"id": transcription_id, "title": body.title}


@router.delete("/api/transcriptions/{transcription_id}", status_code=204)
def delete_transcription(transcription_id: str):
    storage_service.delete_transcription(transcription_id)
    return Response(status_code=204)


@router.get("/api/transcriptions/{transcription_id}/audio")
def get_audio(transcription_id: str):
    audio_path = storage_service.get_audio_path(transcription_id)
    if audio_path is None:
        raise HTTPException(status_code=404, detail="Audio file not found")

    # Determine media type from extension
    ext = audio_path.suffix.lower()
    media_types = {
        ".mp3": "audio/mpeg",
        ".mp4": "video/mp4",
        ".m4a": "audio/mp4",
        ".wav": "audio/wav",
        ".ogg": "audio/ogg",
        ".flac": "audio/flac",
        ".webm": "audio/webm",
        ".mkv": "video/x-matroska",
    }
    media_type = media_types.get(ext, "application/octet-stream")
    return FileResponse(str(audio_path), media_type=media_type)


@router.get("/api/transcriptions/{transcription_id}/export")
def export_transcription(transcription_id: str, format: str = "txt"):
    try:
        data = storage_service.read_transcription(transcription_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Transcription not found")

    if data.get("status") != "completed":
        raise HTTPException(status_code=400, detail="Transcription not yet completed")

    if format == "txt":
        lines = []
        for seg in data.get("segments", []):
            lines.append(seg["text"].strip())
        content = "\n".join(lines)
        filename = f"{data['title']}.txt"
        return Response(
            content=content,
            media_type="text/plain",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    elif format == "srt":
        lines = []
        for i, seg in enumerate(data.get("segments", []), start=1):
            start = _seconds_to_srt_time(seg["start"])
            end = _seconds_to_srt_time(seg["end"])
            lines.append(str(i))
            lines.append(f"{start} --> {end}")
            lines.append(seg["text"].strip())
            lines.append("")
        content = "\n".join(lines)
        filename = f"{data['title']}.srt"
        return Response(
            content=content,
            media_type="text/srt",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    else:
        raise HTTPException(status_code=400, detail="format must be 'txt' or 'srt'")


def _seconds_to_srt_time(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
