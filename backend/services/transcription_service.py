import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from faster_whisper import WhisperModel

from backend.config import detect_device
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
    """Background transcription worker — dispatches to the right backend."""
    try:
        existing = storage_service.read_transcription(transcription_id)
        existing["status"] = "processing"
        storage_service.write_transcription(transcription_id, existing)

        device, compute_type = detect_device()

        if device == "mlx":
            _run_mlx(transcription_id, audio_path, model_name, existing)
        else:
            _run_faster_whisper(transcription_id, audio_path, model_name, existing, device, compute_type)

    except Exception as e:
        _mark_failed(transcription_id, str(e))


def _run_faster_whisper(
    transcription_id: str,
    audio_path: Path,
    model_name: str,
    existing: dict,
    device: str,
    compute_type: str,
) -> None:
    """Transcribe with faster-whisper (CUDA or CPU).

    Segments are yielded lazily, so the progress bar updates in real-time.
    """
    try:
        model = WhisperModel(model_name, device=device, compute_type=compute_type)
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
            progress = min(segment.end / info.duration, 1.0) if info.duration > 0 else 0.0
            with _jobs_lock:
                if transcription_id in _jobs:
                    _jobs[transcription_id]["progress"] = progress

        _mark_completed(transcription_id, existing, collected_segments, info.language, info.duration)

    except Exception as e:
        _mark_failed(transcription_id, str(e))


def _run_mlx(
    transcription_id: str,
    audio_path: Path,
    model_name: str,
    existing: dict,
) -> None:
    """Transcribe with mlx-whisper (Apple Silicon GPU via Metal).

    mlx-whisper processes the full file at once and returns all segments
    together, so progress jumps from 0% to 100% on completion rather than
    filling in gradually. This is a known trade-off vs. faster-whisper.
    """
    try:
        import mlx_whisper  # type: ignore[import]

        # mlx-whisper uses Hugging Face model IDs; map short names to HF repos
        mlx_model_map = {
            "tiny": "mlx-community/whisper-tiny-mlx",
            "base": "mlx-community/whisper-base-mlx",
            "small": "mlx-community/whisper-small-mlx",
            "medium": "mlx-community/whisper-medium-mlx",
            "large-v3": "mlx-community/whisper-large-v3-mlx",
            "turbo": "mlx-community/whisper-large-v3-turbo",
        }
        hf_model = mlx_model_map.get(model_name, f"mlx-community/whisper-{model_name}-mlx")

        result = mlx_whisper.transcribe(
            str(audio_path),
            path_or_hf_repo=hf_model,
            word_timestamps=True,
        )

        collected_segments = []
        for i, seg in enumerate(result.get("segments", [])):
            words = []
            for w in seg.get("words", []):
                words.append({
                    "word": w["word"],
                    "start": round(w["start"], 3),
                    "end": round(w["end"], 3),
                })
            collected_segments.append({
                "id": i,
                "start": round(seg["start"], 3),
                "end": round(seg["end"], 3),
                "text": seg["text"],
                "words": words,
            })

        duration = result.get("segments", [{}])[-1].get("end", 0.0) if result.get("segments") else 0.0
        language = result.get("language")

        _mark_completed(transcription_id, existing, collected_segments, language, duration)

    except Exception as e:
        _mark_failed(transcription_id, str(e))


def _mark_completed(
    transcription_id: str,
    existing: dict,
    segments: list,
    language: Optional[str],
    duration: float,
) -> None:
    existing["status"] = "completed"
    existing["progress"] = 1.0
    existing["language"] = language
    existing["duration_seconds"] = round(duration, 3)
    existing["segments"] = segments
    existing["completed_at"] = datetime.now(timezone.utc).isoformat()
    storage_service.write_transcription(transcription_id, existing)

    with _jobs_lock:
        if transcription_id in _jobs:
            _jobs[transcription_id]["status"] = "completed"
            _jobs[transcription_id]["progress"] = 1.0


def _mark_failed(transcription_id: str, error_msg: str) -> None:
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
