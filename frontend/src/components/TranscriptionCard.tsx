import { useState, useRef } from 'react'
import { Link } from 'react-router-dom'
import { renameTranscription, deleteTranscription } from '../api/client'
import { ProgressBar } from './ProgressBar'
import type { TranscriptionListItem } from '../types'

interface Props {
  item: TranscriptionListItem
  onDeleted: (id: string) => void
  onRenamed: (id: string, title: string) => void
}

export function TranscriptionCard({ item, onDeleted, onRenamed }: Props) {
  const [editing, setEditing] = useState(false)
  const [editTitle, setEditTitle] = useState(item.title)
  const inputRef = useRef<HTMLInputElement>(null)

  const startEdit = () => {
    setEditTitle(item.title)
    setEditing(true)
    setTimeout(() => inputRef.current?.select(), 0)
  }

  const commitEdit = async () => {
    setEditing(false)
    if (editTitle.trim() && editTitle !== item.title) {
      try {
        await renameTranscription(item.id, editTitle.trim())
        onRenamed(item.id, editTitle.trim())
      } catch {
        // revert on failure
      }
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') commitEdit()
    if (e.key === 'Escape') setEditing(false)
  }

  const handleDelete = async () => {
    if (!confirm(`Delete "${item.title}"?`)) return
    try {
      await deleteTranscription(item.id)
      onDeleted(item.id)
    } catch {
      alert('Delete failed')
    }
  }

  const statusLabel: Record<string, string> = {
    pending: 'Pending',
    processing: 'Processing',
    completed: 'Done',
    failed: 'Failed',
  }

  const formattedDate = new Date(item.created_at).toLocaleString()

  return (
    <div className={`card status-${item.status}`}>
      <div className="card-header">
        {editing ? (
          <input
            ref={inputRef}
            className="title-input"
            value={editTitle}
            onChange={(e) => setEditTitle(e.target.value)}
            onBlur={commitEdit}
            onKeyDown={handleKeyDown}
            autoFocus
          />
        ) : (
          <h3 className="card-title" onDoubleClick={startEdit}>
            {item.status === 'completed' ? (
              <Link to={`/transcriptions/${item.id}`}>{item.title}</Link>
            ) : (
              item.title
            )}
          </h3>
        )}
        <span className={`badge badge-${item.status}`}>{statusLabel[item.status]}</span>
      </div>

      {(item.status === 'processing' || item.status === 'pending') && (
        <ProgressBar progress={item.progress} />
      )}

      {item.status === 'failed' && item.error && (
        <p className="error-text">{item.error}</p>
      )}

      <div className="card-footer">
        <span className="meta">{formattedDate} · {item.model}</span>
        {item.language && <span className="meta">· {item.language}</span>}
        <button className="btn-delete" onClick={handleDelete}>Delete</button>
      </div>
    </div>
  )
}
