import { useRef, useImperativeHandle, forwardRef } from 'react'

export interface AudioPlayerHandle {
  seekTo: (time: number) => void
}

interface Props {
  src: string
  onTimeUpdate: (time: number) => void
}

export const AudioPlayer = forwardRef<AudioPlayerHandle, Props>(function AudioPlayer(
  { src, onTimeUpdate },
  ref
) {
  const audioRef = useRef<HTMLAudioElement>(null)

  useImperativeHandle(ref, () => ({
    seekTo(time: number) {
      if (audioRef.current) {
        audioRef.current.currentTime = time
      }
    },
  }))

  return (
    <div className="audio-player">
      <audio
        ref={audioRef}
        src={src}
        controls
        onTimeUpdate={(e) => onTimeUpdate((e.target as HTMLAudioElement).currentTime)}
        className="audio-element"
      />
    </div>
  )
})
