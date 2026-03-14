import { useEffect, useCallback } from 'react'
import { listTranscriptions, getStatus } from '../api/client'
import { useTranscriptionStore } from '../store/transcriptionStore'
import { TranscriptionCard } from '../components/TranscriptionCard'
import { UploadForm } from '../components/UploadForm'
import { usePolling } from '../hooks/usePolling'
import type { TranscriptionListItem } from '../types'

export function TranscriptionList() {
  const { transcriptions, setTranscriptions, updateStatus } = useTranscriptionStore()

  const hasActive = transcriptions.some(
    (t) => t.status === 'pending' || t.status === 'processing'
  )

  const fetchList = useCallback(async () => {
    try {
      const items = await listTranscriptions()
      setTranscriptions(items)
    } catch (err) {
      console.error('Failed to fetch transcriptions', err)
    }
  }, [setTranscriptions])

  const pollActive = useCallback(async () => {
    const active = transcriptions.filter(
      (t) => t.status === 'pending' || t.status === 'processing'
    )
    await Promise.all(
      active.map(async (t) => {
        try {
          const s = await getStatus(t.id)
          updateStatus(t.id, s.status, s.progress)
          // When completed/failed, refresh full list to get updated data
          if (s.status === 'completed' || s.status === 'failed') {
            fetchList()
          }
        } catch {
          // ignore polling errors
        }
      })
    )
  }, [transcriptions, updateStatus, fetchList])

  useEffect(() => {
    fetchList()
  }, [fetchList])

  usePolling(pollActive, 2000, hasActive)

  const handleDeleted = (id: string) => {
    setTranscriptions(transcriptions.filter((t) => t.id !== id))
  }

  const handleRenamed = (id: string, title: string) => {
    setTranscriptions(
      transcriptions.map((t) => (t.id === id ? { ...t, title } : t))
    )
  }

  return (
    <div className="page">
      <header className="page-header">
        <h1>Claudescribe</h1>
        <p className="subtitle">Local lecture transcription</p>
      </header>

      <UploadForm onUploaded={fetchList} />

      <section className="transcription-list">
        {transcriptions.length === 0 ? (
          <p className="empty-state">No transcriptions yet. Upload an audio file to get started.</p>
        ) : (
          transcriptions.map((item: TranscriptionListItem) => (
            <TranscriptionCard
              key={item.id}
              item={item}
              onDeleted={handleDeleted}
              onRenamed={handleRenamed}
            />
          ))
        )}
      </section>
    </div>
  )
}
