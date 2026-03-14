import type { Word } from '../types'

/**
 * Binary search: find rightmost word where word.start <= currentTime.
 * Returns -1 if no word has started yet.
 */
export function findActiveWordIndex(words: Word[], currentTime: number): number {
  if (words.length === 0 || currentTime < words[0].start) return -1
  let lo = 0
  let hi = words.length - 1
  while (lo < hi) {
    const mid = Math.ceil((lo + hi) / 2)
    if (words[mid].start <= currentTime) {
      lo = mid
    } else {
      hi = mid - 1
    }
  }
  return lo
}
