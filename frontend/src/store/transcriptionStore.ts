import { create } from 'zustand'
import type { TranscriptionListItem, TranscriptionStatus } from '../types'

interface TranscriptionStore {
  transcriptions: TranscriptionListItem[]
  setTranscriptions: (items: TranscriptionListItem[]) => void
  updateStatus: (id: string, status: TranscriptionStatus, progress: number) => void
}

export const useTranscriptionStore = create<TranscriptionStore>((set) => ({
  transcriptions: [],
  setTranscriptions: (items) => set({ transcriptions: items }),
  updateStatus: (id, status, progress) =>
    set((state) => ({
      transcriptions: state.transcriptions.map((t) =>
        t.id === id ? { ...t, status, progress } : t
      ),
    })),
}))
