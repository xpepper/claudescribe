from enum import Enum
from typing import Optional
from pydantic import BaseModel


class TranscriptionStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class Word(BaseModel):
    word: str
    start: float
    end: float


class Segment(BaseModel):
    id: int
    start: float
    end: float
    text: str
    words: list[Word]


class TranscriptionRecord(BaseModel):
    id: str
    title: str
    original_filename: str
    model: str
    language: Optional[str] = None
    status: TranscriptionStatus
    progress: float = 0.0
    created_at: str
    completed_at: Optional[str] = None
    error: Optional[str] = None
    duration_seconds: Optional[float] = None
    segments: list[Segment] = []


class TranscriptionListItem(BaseModel):
    id: str
    title: str
    original_filename: str
    model: str
    language: Optional[str] = None
    status: TranscriptionStatus
    progress: float = 0.0
    created_at: str
    completed_at: Optional[str] = None
    error: Optional[str] = None
    duration_seconds: Optional[float] = None


class TranscriptionStatusResponse(BaseModel):
    id: str
    status: TranscriptionStatus
    progress: float
    error: Optional[str] = None
