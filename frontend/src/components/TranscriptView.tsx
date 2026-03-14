import { useMemo, useEffect, useRef } from 'react'
import type { Segment, Word } from '../types'

interface FlatWord extends Word {
  segmentIndex: number
  wordIndex: number
  globalIndex: number
}

interface Props {
  segments: Segment[]
  currentTime: number
  activeWordIndex: number
  onWordClick: (start: number) => void
}

export function TranscriptView({ segments, currentTime: _currentTime, activeWordIndex, onWordClick }: Props) {
  const activeRef = useRef<HTMLSpanElement>(null)

  // Flatten all words with their positions (memoized, doesn't change)
  const { flatWords, wordMap } = useMemo(() => {
    const flat: FlatWord[] = []
    const map: Map<string, number> = new Map() // "segIdx-wordIdx" -> globalIndex
    let globalIndex = 0
    for (let si = 0; si < segments.length; si++) {
      for (let wi = 0; wi < segments[si].words.length; wi++) {
        flat.push({ ...segments[si].words[wi], segmentIndex: si, wordIndex: wi, globalIndex })
        map.set(`${si}-${wi}`, globalIndex)
        globalIndex++
      }
    }
    return { flatWords: flat, wordMap: map }
  }, [segments])

  // Scroll active word into view when it changes
  useEffect(() => {
    if (activeRef.current) {
      activeRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    }
  }, [activeWordIndex])

  // Suppress unused warning - flatWords used internally via wordMap
  void flatWords

  return (
    <div className="transcript-view">
      {segments.map((segment, si) => (
        <p key={segment.id} className="transcript-segment">
          {segment.words.map((word, wi) => {
            const globalIdx = wordMap.get(`${si}-${wi}`) ?? -1
            const isActive = globalIdx === activeWordIndex
            return (
              <span
                key={wi}
                ref={isActive ? activeRef : null}
                className={`word ${isActive ? 'active' : ''}`}
                onClick={() => onWordClick(word.start)}
              >
                {word.word}
              </span>
            )
          })}
        </p>
      ))}
    </div>
  )
}
