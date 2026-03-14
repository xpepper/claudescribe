"""Tests for transcription_service status/bookkeeping (no model download)."""

import threading
from pathlib import Path
from unittest.mock import patch

import pytest

import backend.services.transcription_service as svc


def _clear_jobs():
    """Helper to reset the in-memory _jobs dict between tests."""
    with svc._jobs_lock:
        svc._jobs.clear()


@pytest.fixture(autouse=True)
def reset_jobs():
    _clear_jobs()
    yield
    _clear_jobs()


class TestGetStatusUnknownId:
    def test_returns_none_when_no_in_memory_job_and_no_file(self):
        with patch(
            "backend.services.transcription_service.storage_service.read_transcription",
            side_effect=FileNotFoundError,
        ):
            result = svc.get_status("nonexistent-id")

        assert result is None


class TestGetStatusInMemory:
    def test_returns_in_memory_status_when_job_is_active(self):
        transcription_id = "active-job-id"
        with svc._jobs_lock:
            svc._jobs[transcription_id] = {
                "id": transcription_id,
                "status": "processing",
                "progress": 0.42,
                "error": None,
            }

        result = svc.get_status(transcription_id)

        assert result is not None
        assert result["id"] == transcription_id
        assert result["status"] == "processing"
        assert result["progress"] == 0.42
        assert result["error"] is None

    def test_in_memory_result_is_a_copy(self):
        transcription_id = "copy-test-id"
        with svc._jobs_lock:
            svc._jobs[transcription_id] = {
                "id": transcription_id,
                "status": "processing",
                "progress": 0.0,
                "error": None,
            }

        result = svc.get_status(transcription_id)
        result["status"] = "mutated"

        with svc._jobs_lock:
            assert svc._jobs[transcription_id]["status"] == "processing"


class TestGetStatusFallbackToFile:
    def test_falls_back_to_json_file_when_not_in_memory(self):
        transcription_id = "file-only-id"
        file_data = {
            "id": transcription_id,
            "status": "completed",
            "progress": 1.0,
            "error": None,
        }

        with patch(
            "backend.services.transcription_service.storage_service.read_transcription",
            return_value=file_data,
        ) as mock_read:
            result = svc.get_status(transcription_id)
            mock_read.assert_called_once_with(transcription_id)

        assert result is not None
        assert result["id"] == transcription_id
        assert result["status"] == "completed"
        assert result["progress"] == 1.0
        assert result["error"] is None

    def test_fallback_uses_default_progress_when_missing_from_file(self):
        transcription_id = "no-progress-id"
        file_data = {
            "id": transcription_id,
            "status": "completed",
        }

        with patch(
            "backend.services.transcription_service.storage_service.read_transcription",
            return_value=file_data,
        ):
            result = svc.get_status(transcription_id)

        assert result["progress"] == 0.0

    def test_in_memory_takes_priority_over_file(self):
        transcription_id = "priority-test-id"
        with svc._jobs_lock:
            svc._jobs[transcription_id] = {
                "id": transcription_id,
                "status": "processing",
                "progress": 0.5,
                "error": None,
            }

        with patch(
            "backend.services.transcription_service.storage_service.read_transcription",
        ) as mock_read:
            result = svc.get_status(transcription_id)
            mock_read.assert_not_called()

        assert result["status"] == "processing"


class TestEnqueueBookkeeping:
    def test_enqueue_registers_job_in_memory(self):
        transcription_id = "enqueue-test-id"
        audio_path = Path("/fake/audio.mp3")

        # Patch Thread.start so no actual thread runs
        with patch("threading.Thread.start"):
            svc.enqueue(transcription_id, audio_path, "tiny")

        with svc._jobs_lock:
            assert transcription_id in svc._jobs
            job = svc._jobs[transcription_id]

        assert job["id"] == transcription_id
        assert job["status"] == "processing"
        assert job["progress"] == 0.0
        assert job["error"] is None
