import pytest
from pathlib import Path

import backend.services.storage_service as storage_service


@pytest.fixture(autouse=True)
def override_data_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(storage_service, "DATA_DIR", tmp_path)


def test_create_transcription_dir(tmp_path, monkeypatch):
    tid = "abc-123"
    result = storage_service.create_transcription_dir(tid)
    assert result == storage_service.DATA_DIR / tid
    assert result.is_dir()


def test_write_and_read_transcription_round_trip():
    tid = "round-trip-id"
    storage_service.create_transcription_dir(tid)
    data = {"id": tid, "title": "Test", "status": "pending", "created_at": "2024-01-01T00:00:00"}
    storage_service.write_transcription(tid, data)
    result = storage_service.read_transcription(tid)
    assert result == data


def test_list_transcriptions_sorted_descending():
    records = [
        {"id": "a", "created_at": "2024-01-01T00:00:00"},
        {"id": "b", "created_at": "2024-03-01T00:00:00"},
        {"id": "c", "created_at": "2024-02-01T00:00:00"},
    ]
    for record in records:
        tid = record["id"]
        storage_service.create_transcription_dir(tid)
        storage_service.write_transcription(tid, record)

    result = storage_service.list_transcriptions()
    assert [r["id"] for r in result] == ["b", "c", "a"]


def test_delete_transcription_removes_directory():
    tid = "to-delete"
    storage_service.create_transcription_dir(tid)
    storage_service.write_transcription(tid, {"id": tid, "created_at": "2024-01-01T00:00:00"})
    assert (storage_service.DATA_DIR / tid).is_dir()
    storage_service.delete_transcription(tid)
    assert not (storage_service.DATA_DIR / tid).exists()


def test_save_audio_writes_bytes():
    tid = "audio-test"
    storage_service.create_transcription_dir(tid)
    content = b"fake audio bytes"
    path = storage_service.save_audio(tid, content, "mp3")
    assert path.exists()
    assert path.name == "audio.mp3"
    assert path.read_bytes() == content


def test_get_audio_path_returns_path_when_exists():
    tid = "audio-path-test"
    storage_service.create_transcription_dir(tid)
    storage_service.save_audio(tid, b"data", "wav")
    result = storage_service.get_audio_path(tid)
    assert result is not None
    assert result.name == "audio.wav"


def test_get_audio_path_returns_none_when_missing():
    tid = "no-audio"
    storage_service.create_transcription_dir(tid)
    result = storage_service.get_audio_path(tid)
    assert result is None
