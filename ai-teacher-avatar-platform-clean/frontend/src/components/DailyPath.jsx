const STEPS = [
  { key: 'warmup', label: 'Warm-up' },
  { key: 'vocabulary', label: 'Vocabulary' },
  { key: 'grammar', label: 'Grammar' },
  { key: 'speaking_test', label: 'Speaking Test' },
  { key: 'homework', label: 'Homework' },
]

export default function DailyPath({ stageIndex }) {
  return (
    <div className="daily-path">
      {STEPS.map((step, i) => (
        <div
          key={step.key}
          className={`path-step ${i < stageIndex ? 'done' : i === stageIndex ? 'active' : ''}`}
        >
          <div className="path-dot">{i < stageIndex ? '✓' : i + 1}</div>
          <span className="path-label">{step.label}</span>
          {i < STEPS.length - 1 && <div className="path-line" />}
        </div>
      ))}
    </div>
  )
}
