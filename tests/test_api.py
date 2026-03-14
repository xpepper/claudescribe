import io
import json
import wave
from datetime import datetime, timezone
from unittest.mock import patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

import backend.services.storage_service as storage_service
from backend.app import app


def make_wav_bytes(duration_seconds: float = 1.0, sample_rate: int = 8000) -> bytes:
    """Create a minimal valid WAV file in memory."""
    buf = io.BytesIO()
    num_frames = int(sample_rate * duration_seconds)
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(b"\x00\x00" * num_frames)
    return buf.getvalue()


@pytest.fixture(autouse=True)
def override_data_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(storage_service, "DATA_DIR", tmp_path)


@pytest.fixture
def wav_bytes():
    return make_wav_bytes()


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_list_transcriptions_empty(client):
    response = await client.get("/api/transcriptions")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_upload_transcription_returns_201(client, wav_bytes):
    with patch("backend.routes.jobs.transcription_service.enqueue"):
        response = await client.post(
            "/api/transcriptions",
            files={"file": ("lecture.wav", wav_bytes, "audio/wav")},
            data={"model": "turbo"},
        )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "pending"
    assert "id" in body


@pytest.mark.asyncio
async def test_upload_transcription_rejects_unsupported_extension(client):
    response = await client.post(
        "/api/transcriptions",
        files={"file": ("notes.txt", b"hello", "text/plain")},
        data={"model": "turbo"},
    )
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_status_after_upload(client, wav_bytes):
    with patch("backend.routes.jobs.transcription_service.enqueue"):
        upload = await client.post(
            "/api/transcriptions",
            files={"file": ("lecture.wav", wav_bytes, "audio/wav")},
        )
    transcription_id = upload.json()["id"]

    with patch("backend.routes.jobs.transcription_service.get_status") as mock_status:
        mock_status.return_value = {
            "id": transcription_id,
            "status": "pending",
            "progress": 0.0,
            "error": None,
        }
        response = await client.get(f"/api/transcriptions/{transcription_id}/status")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == transcription_id
    assert body["status"] == "pending"


@pytest.mark.asyncio
async def test_get_status_not_found(client):
    with patch("backend.routes.jobs.transcription_service.get_status") as mock_status:
        mock_status.return_value = None
        response = await client.get("/api/transcriptions/nonexistent-id/status")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_rename_transcription(client, tmp_path, wav_bytes):
    with patch("backend.routes.jobs.transcription_service.enqueue"):
        upload = await client.post(
            "/api/transcriptions",
            files={"file": ("lecture.wav", wav_bytes, "audio/wav")},
        )
    transcription_id = upload.json()["id"]

    response = await client.patch(
        f"/api/transcriptions/{transcription_id}",
        json={"title": "My Renamed Lecture"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "My Renamed Lecture"
    assert body["id"] == transcription_id

    # Verify it persisted
    data = storage_service.read_transcription(transcription_id)
    assert data["title"] == "My Renamed Lecture"


@pytest.mark.asyncio
async def test_rename_transcription_not_found(client):
    response = await client.patch(
        "/api/transcriptions/nonexistent-id",
        json={"title": "New Title"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_transcription(client, wav_bytes):
    with patch("backend.routes.jobs.transcription_service.enqueue"):
        upload = await client.post(
            "/api/transcriptions",
            files={"file": ("lecture.wav", wav_bytes, "audio/wav")},
        )
    transcription_id = upload.json()["id"]

    response = await client.delete(f"/api/transcriptions/{transcription_id}")
    assert response.status_code == 204

    # Verify it is gone
    list_response = await client.get("/api/transcriptions")
    ids = [item["id"] for item in list_response.json()]
    assert transcription_id not in ids


@pytest.mark.asyncio
async def test_export_txt_on_completed_transcription(client, tmp_path):
    """Write a completed transcription directly and test the export endpoint."""
    transcription_id = "export-test-id"
    storage_service.create_transcription_dir(transcription_id)
    now = datetime.now(timezone.utc).isoformat()
    completed_data = {
        "id": transcription_id,
        "title": "My Lecture",
        "original_filename": "lecture.wav",
        "model": "turbo",
        "language": "en",
        "status": "completed",
        "progress": 1.0,
        "created_at": now,
        "completed_at": now,
        "error": None,
        "duration_seconds": 2.5,
        "segments": [
            {"id": 0, "start": 0.0, "end": 1.0, "text": "Hello world.", "words": []},
            {"id": 1, "start": 1.0, "end": 2.5, "text": "This is a test.", "words": []},
        ],
    }
    storage_service.write_transcription(transcription_id, completed_data)

    response = await client.get(f"/api/transcriptions/{transcription_id}/export?format=txt")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    text = response.text
    assert "Hello world." in text
    assert "This is a test." in text


@pytest.mark.asyncio
async def test_export_srt_on_completed_transcription(client):
    transcription_id = "export-srt-id"
    storage_service.create_transcription_dir(transcription_id)
    now = datetime.now(timezone.utc).isoformat()
    completed_data = {
        "id": transcription_id,
        "title": "SRT Lecture",
        "original_filename": "lecture.wav",
        "model": "turbo",
        "language": "en",
        "status": "completed",
        "progress": 1.0,
        "created_at": now,
        "completed_at": now,
        "error": None,
        "duration_seconds": 2.5,
        "segments": [
            {"id": 0, "start": 0.0, "end": 1.25, "text": "Hello world.", "words": []},
        ],
    }
    storage_service.write_transcription(transcription_id, completed_data)

    response = await client.get(f"/api/transcriptions/{transcription_id}/export?format=srt")
    assert response.status_code == 200
    text = response.text
    assert "00:00:00,000 --> 00:00:01,250" in text
    assert "Hello world." in text


@pytest.mark.asyncio
async def test_export_on_pending_transcription_returns_400(client, wav_bytes):
    with patch("backend.routes.jobs.transcription_service.enqueue"):
        upload = await client.post(
            "/api/transcriptions",
            files={"file": ("lecture.wav", wav_bytes, "audio/wav")},
        )
    transcription_id = upload.json()["id"]

    response = await client.get(f"/api/transcriptions/{transcription_id}/export?format=txt")
    assert response.status_code == 400
    assert "not yet completed" in response.json()["detail"]


@pytest.mark.asyncio
async def test_export_invalid_format_returns_400(client):
    transcription_id = "export-bad-format-id"
    storage_service.create_transcription_dir(transcription_id)
    now = datetime.now(timezone.utc).isoformat()
    completed_data = {
        "id": transcription_id,
        "title": "Lecture",
        "original_filename": "lecture.wav",
        "model": "turbo",
        "language": "en",
        "status": "completed",
        "progress": 1.0,
        "created_at": now,
        "completed_at": now,
        "error": None,
        "duration_seconds": 1.0,
        "segments": [],
    }
    storage_service.write_transcription(transcription_id, completed_data)

    response = await client.get(f"/api/transcriptions/{transcription_id}/export?format=pdf")
    assert response.status_code == 400
