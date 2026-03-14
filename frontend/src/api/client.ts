import type { Transcription, TranscriptionListItem, StatusResponse } from '../types'

const BASE = '/api'

export async function uploadTranscription(file: File, model: string): Promise<{ id: string; status: string }> {
  const form = new FormData()
  form.append('file', file)
  form.append('model', model)
  const res = await fetch(`${BASE}/transcriptions`, { method: 'POST', body: form })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function listTranscriptions(): Promise<TranscriptionListItem[]> {
  const res = await fetch(`${BASE}/transcriptions`)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function getTranscription(id: string): Promise<Transcription> {
  const res = await fetch(`${BASE}/transcriptions/${id}`)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function getStatus(id: string): Promise<StatusResponse> {
  const res = await fetch(`${BASE}/transcriptions/${id}/status`)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function renameTranscription(id: string, title: string): Promise<void> {
  const res = await fetch(`${BASE}/transcriptions/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title }),
  })
  if (!res.ok) throw new Error(await res.text())
}

export async function deleteTranscription(id: string): Promise<void> {
  const res = await fetch(`${BASE}/transcriptions/${id}`, { method: 'DELETE' })
  if (!res.ok) throw new Error(await res.text())
}

export function getAudioUrl(id: string): string {
  return `${BASE}/transcriptions/${id}/audio`
}

export function getExportUrl(id: string, format: 'txt' | 'srt'): string {
  return `${BASE}/transcriptions/${id}/export?format=${format}`
}
