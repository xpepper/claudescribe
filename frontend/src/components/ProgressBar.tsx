interface Props {
  progress: number // 0 to 1
}

export function ProgressBar({ progress }: Props) {
  const pct = Math.round(progress * 100)
  return (
    <div className="progress-bar-container">
      <div className="progress-bar-fill" style={{ width: `${pct}%` }} />
      <span className="progress-bar-label">{pct}%</span>
    </div>
  )
}
