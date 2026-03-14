import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from faster_whisper import WhisperModel

from backend.services import storage_service

# In-memory job progress tracking
_jobs: dict[str, dict] = {}
_jobs_lock = threading.Lock()


def enqueue(transcription_id: str, audio_path: Path, model_name: str) -> None:
    """Spawn a background thread to run transcription."""
    with _jobs_lock:
        _jobs[transcription_id] = {
            "id": transcription_id,
            "status": "processing",
            "progress": 0.0,
            "error": None,
        }
    thread = threading.Thread(
        target=_run,
        args=(transcription_id, audio_path, model_name),
        daemon=True,
    )
    thread.start()


def get_status(transcription_id: str) -> Optional[dict]:
    """Return live progress if in memory, else fall back to JSON file."""
    with _jobs_lock:
        if transcription_id in _jobs:
            return dict(_jobs[transcription_id])
    # Fall back to reading the JSON file
    try:
        data = storage_service.read_transcription(transcription_id)
        return {
            "id": data["id"],
            "status": data["status"],
            "progress": data.get("progress", 0.0),
            "error": data.get("error"),
        }
    except FileNotFoundError:
        return None


def _run(transcription_id: str, audio_path: Path, model_name: str) -> None:
    """Background transcription worker."""
    try:
        # Read existing metadata to preserve title/filename/etc.
        existing = storage_service.read_transcription(transcription_id)

        # Update status to processing
        existing["status"] = "processing"
        storage_service.write_transcription(transcription_id, existing)

        # Load model
        model = WhisperModel(model_name, device="cpu", compute_type="int8")

        # Transcribe with word timestamps
        segments_iter, info = model.transcribe(str(audio_path), word_timestamps=True)

        collected_segments = []
        for segment in segments_iter:
            words = []
            if segment.words:
                for w in segment.words:
                    words.append({
                        "word": w.word,
                        "start": round(w.start, 3),
                        "end": round(w.end, 3),
                    })
            collected_segments.append({
                "id": segment.id,
                "start": round(segment.start, 3),
                "end": round(segment.end, 3),
                "text": segment.text,
                "words": words,
            })
            # Update progress
            progress = min(segment.end / info.duration, 1.0) if info.duration > 0 else 0.0
            with _jobs_lock:
                if transcription_id in _jobs:
                    _jobs[transcription_id]["progress"] = progress

        # Write completed transcription
        existing["status"] = "completed"
        existing["progress"] = 1.0
        existing["language"] = info.language
        existing["duration_seconds"] = round(info.duration, 3)
        existing["segments"] = collected_segments
        existing["completed_at"] = datetime.now(timezone.utc).isoformat()
        storage_service.write_transcription(transcription_id, existing)

        with _jobs_lock:
            if transcription_id in _jobs:
                _jobs[transcription_id]["status"] = "completed"
                _jobs[transcription_id]["progress"] = 1.0

    except Exception as e:
        error_msg = str(e)
        try:
            existing = storage_service.read_transcription(transcription_id)
            existing["status"] = "failed"
            existing["error"] = error_msg
            storage_service.write_transcription(transcription_id, existing)
        except Exception:
            pass
        with _jobs_lock:
            if transcription_id in _jobs:
                _jobs[transcription_id]["status"] = "failed"
                _jobs[transcription_id]["error"] = error_msg
