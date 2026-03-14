import { useState, useRef } from 'react'
import { uploadTranscription } from '../api/client'

const MODELS = ['tiny', 'base', 'small', 'medium', 'large-v3', 'turbo']

interface Props {
  onUploaded: () => void
}

export function UploadForm({ onUploaded }: Props) {
  const [file, setFile] = useState<File | null>(null)
  const [model, setModel] = useState('turbo')
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [dragging, setDragging] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleFile = (f: File) => {
    setFile(f)
    setError(null)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragging(false)
    const f = e.dataTransfer.files[0]
    if (f) handleFile(f)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) return
    setUploading(true)
    setError(null)
    try {
      await uploadTranscription(file, model)
      setFile(null)
      onUploaded()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="upload-form">
      <div
        className={`drop-zone ${dragging ? 'drag-over' : ''} ${file ? 'has-file' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".mp3,.mp4,.m4a,.wav,.ogg,.flac,.webm,.mkv"
          onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
          style={{ display: 'none' }}
        />
        {file ? (
          <p className="file-name">📎 {file.name}</p>
        ) : (
          <p>Drop an audio file here or click to browse</p>
        )}
      </div>

      <div className="upload-controls">
        <label>
          Model:
          <select value={model} onChange={(e) => setModel(e.target.value)}>
            {MODELS.map((m) => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
        </label>

        <button type="submit" disabled={!file || uploading}>
          {uploading ? 'Uploading…' : 'Transcribe'}
        </button>
      </div>

      {error && <p className="error">{error}</p>}
    </form>
  )
}
