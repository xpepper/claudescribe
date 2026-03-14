import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional

from backend.config import DATA_DIR


def create_transcription_dir(transcription_id: str) -> Path:
    path = DATA_DIR / transcription_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_audio(transcription_id: str, file_bytes: bytes, ext: str) -> Path:
    path = DATA_DIR / transcription_id / f"audio.{ext}"
    path.write_bytes(file_bytes)
    return path


def write_transcription(transcription_id: str, data: dict) -> None:
    target = DATA_DIR / transcription_id / "transcription.json"
    with tempfile.NamedTemporaryFile("w", dir=target.parent, delete=False, suffix=".tmp") as f:
        json.dump(data, f, indent=2)
        tmp_path = f.name
    os.replace(tmp_path, target)


def read_transcription(transcription_id: str) -> dict:
    path = DATA_DIR / transcription_id / "transcription.json"
    return json.loads(path.read_text())


def list_transcriptions() -> list[dict]:
    records = []
    if not DATA_DIR.exists():
        return records
    for entry in DATA_DIR.iterdir():
        if not entry.is_dir():
            continue
        json_path = entry / "transcription.json"
        if json_path.exists():
            records.append(json.loads(json_path.read_text()))
    records.sort(key=lambda r: r.get("created_at", ""), reverse=True)
    return records


def delete_transcription(transcription_id: str) -> None:
    path = DATA_DIR / transcription_id
    shutil.rmtree(path)


def get_audio_path(transcription_id: str) -> Optional[Path]:
    directory = DATA_DIR / transcription_id
    for candidate in directory.glob("audio.*"):
        return candidate
    return None
