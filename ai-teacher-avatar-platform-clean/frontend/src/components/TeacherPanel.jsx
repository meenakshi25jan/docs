export default function TeacherPanel({ lesson, speaking, onEditProfile }) {
  if (!lesson) return null

  const {
    teacher_name,
    student_name,
    day_number,
    lesson_topic,
    stage_index,
    goal_checklist,
    streak_days,
    words_learned,
    level,
    target_band,
    latest_band_score,
    focus_weakness,
  } = lesson

  return (
    <div className="teacher-panel">
      <div className={`avatar ${speaking ? 'speaking' : ''}`}>
        <span className="avatar-emoji">👨‍🏫</span>
      </div>
      <h3 className="teacher-name">{teacher_name}</h3>
      <p className="teacher-subtitle">Your English Teacher</p>

      <div className="panel-block">
        <p className="panel-label">Lesson</p>
        <p className="panel-value">{lesson_topic}</p>
        <p className="panel-sub">Day {day_number} · for {student_name} · {level}</p>
      </div>

      {focus_weakness && (
        <div className="panel-block focus-block">
          <p className="panel-label">Focus area today</p>
          <p className="panel-value">{focus_weakness}</p>
        </div>
      )}

      <div className="panel-block">
        <p className="panel-label">Today's Goal</p>
        <ul className="goal-list">
          {goal_checklist.map((goal, i) => (
            <li key={i} className={i < stage_index ? 'done' : i === stage_index ? 'active' : ''}>
              <span className="goal-check">{i < stage_index ? '✓' : i === stage_index ? '➤' : '○'}</span>
              {goal}
            </li>
          ))}
        </ul>
      </div>

      <div className="panel-stats">
        <div>
          <span className="stat-num">{streak_days}</span>
          <span className="stat-label">day streak</span>
        </div>
        <div>
          <span className="stat-num">{words_learned}</span>
          <span className="stat-label">words learned</span>
        </div>
      </div>

      {(latest_band_score != null || target_band != null) && (
        <div className="panel-block band-block">
          <p className="panel-label">Band Score</p>
          <div className="band-row">
            <span className="stat-num">{latest_band_score != null ? latest_band_score.toFixed(1) : '—'}</span>
            {target_band != null && (
              <>
                <span className="band-arrow">→</span>
                <span className="stat-num target">{target_band.toFixed(1)}</span>
              </>
            )}
          </div>
          {target_band != null && (
            <p className="panel-sub">
              {latest_band_score != null
                ? `${Math.max(0, target_band - latest_band_score).toFixed(1)} to go`
                : 'Take the Band Score test in Free Practice to track this'}
            </p>
          )}
        </div>
      )}

      {onEditProfile && (
        <button className="link edit-profile-btn" onClick={onEditProfile}>
          Edit my profile
        </button>
      )}
    </div>
  )
}
