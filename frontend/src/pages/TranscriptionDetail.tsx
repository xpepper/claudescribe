import { useState, useEffect, useRef, useCallback } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { getTranscription, getAudioUrl, getExportUrl, renameTranscription, deleteTranscription } from '../api/client'
import { AudioPlayer, type AudioPlayerHandle } from '../components/AudioPlayer'
import { TranscriptView } from '../components/TranscriptView'
import { findActiveWordIndex } from '../hooks/useAudioSync'
import type { Transcription, Word } from '../types'

export function TranscriptionDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const [transcription, setTranscription] = useState<Transcription | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeWordIndex, setActiveWordIndex] = useState(-1)
  const [editingTitle, setEditingTitle] = useState(false)
  const [editTitle, setEditTitle] = useState('')

  const currentTimeRef = useRef(0)
  const audioRef = useRef<AudioPlayerHandle>(null)
  const flatWordsRef = useRef<Word[]>([])

  useEffect(() => {
    if (!id) return
    getTranscription(id)
      .then((t) => {
        setTranscription(t)
        // Flatten words once
        flatWordsRef.current = t.segments.flatMap((s) => s.words)
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [id])

  const handleTimeUpdate = useCallback((time: number) => {
    currentTimeRef.current = time
    const idx = findActiveWordIndex(flatWordsRef.current, time)
    setActiveWordIndex((prev) => (prev !== idx ? idx : prev))
  }, [])

  const handleWordClick = useCallback((start: number) => {
    audioRef.current?.seekTo(start)
  }, [])

  const handleExport = (format: 'txt' | 'srt') => {
    if (!id) return
    const a = document.createElement('a')
    a.href = getExportUrl(id, format)
    a.download = ''
    a.click()
  }

  const startEditTitle = () => {
    if (!transcription) return
    setEditTitle(transcription.title)
    setEditingTitle(true)
  }

  const commitEditTitle = async () => {
    setEditingTitle(false)
    if (!id || !transcription || !editTitle.trim() || editTitle === transcription.title) return
    try {
      await renameTranscription(id, editTitle.trim())
      setTranscription({ ...transcription, title: editTitle.trim() })
    } catch {
      // ignore
    }
  }

  const handleDelete = async () => {
    if (!id || !transcription) return
    if (!confirm(`Delete "${transcription.title}"?`)) return
    try {
      await deleteTranscription(id)
      navigate('/')
    } catch {
      alert('Delete failed')
    }
  }

  const formatDuration = (seconds: number | null) => {
    if (seconds === null) return ''
    const m = Math.floor(seconds / 60)
    const s = Math.floor(seconds % 60)
    return `${m}:${s.toString().padStart(2, '0')}`
  }

  if (loading) return <div className="page"><p>Loading…</p></div>
  if (error) return <div className="page"><p className="error">{error}</p></div>
  if (!transcription) return null

  return (
    <div className="page detail-page">
      <header className="detail-header">
        <Link to="/" className="back-link">← Back</Link>

        <div className="detail-title-row">
          {editingTitle ? (
            <input
              className="title-input"
              value={editTitle}
              onChange={(e) => setEditTitle(e.target.value)}
              onBlur={commitEditTitle}
              onKeyDown={(e) => {
                if (e.key === 'Enter') commitEditTitle()
                if (e.key === 'Escape') setEditingTitle(false)
              }}
              autoFocus
            />
          ) : (
            <h1 onDoubleClick={startEditTitle}>{transcription.title}</h1>
          )}
        </div>

        <div className="detail-meta">
          <span>Model: {transcription.model}</span>
          {transcription.language && <span>Language: {transcription.language}</span>}
          {transcription.duration_seconds !== null && (
            <span>Duration: {formatDuration(transcription.duration_seconds)}</span>
          )}
        </div>

        <div className="detail-actions">
          <button onClick={() => handleExport('txt')}>Export TXT</button>
          <button onClick={() => handleExport('srt')}>Export SRT</button>
          <button className="btn-delete" onClick={handleDelete}>Delete</button>
        </div>
      </header>

      <AudioPlayer
        ref={audioRef}
        src={getAudioUrl(id!)}
        onTimeUpdate={handleTimeUpdate}
      />

      <TranscriptView
        segments={transcription.segments}
        currentTime={currentTimeRef.current}
        activeWordIndex={activeWordIndex}
        onWordClick={handleWordClick}
      />
    </div>
  )
}
