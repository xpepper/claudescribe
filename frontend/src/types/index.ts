export type TranscriptionStatus = 'pending' | 'processing' | 'completed' | 'failed'

export interface Word {
  word: string
  start: number
  end: number
}

export interface Segment {
  id: number
  start: number
  end: number
  text: string
  words: Word[]
}

export interface Transcription {
  id: string
  title: string
  original_filename: string
  model: string
  language: string | null
  status: TranscriptionStatus
  progress: number
  created_at: string
  completed_at: string | null
  error: string | null
  duration_seconds: number | null
  segments: Segment[]
}

export interface TranscriptionListItem {
  id: string
  title: string
  original_filename: string
  model: string
  language: string | null
  status: TranscriptionStatus
  progress: number
  created_at: string
  completed_at: string | null
  error: string | null
  duration_seconds: number | null
}

export interface StatusResponse {
  id: string
  status: TranscriptionStatus
  progress: number
  error: string | null
}
