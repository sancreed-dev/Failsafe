const riskClass = {
  HIGH: "risk-high",
  MEDIUM: "risk-medium",
  LOW: "risk-low",
}

function StudentView({ students, selectedStudent, onSelectStudent }) {
  return (
    <section className="panel">
      <div className="section-heading">
        <h2>Priority Student Cards</h2>
        <p>Sorted by predicted failure probability.</p>
      </div>

      <div className="student-grid">
        {students.map((student) => (
          <article
            className={`student-card ${
              selectedStudent?.student === student.student ? "student-card-active" : ""
            }`}
            key={`${student.subject}-${student.student}`}
            role="button"
            tabIndex={0}
            onClick={() => onSelectStudent(student)}
            onKeyDown={(event) => {
              if (event.key === "Enter" || event.key === " ") onSelectStudent(student)
            }}
          >
            <div className="student-card-header">
              <div>
                <span>Student #{student.student}</span>
                <strong>{student.subject}</strong>
              </div>
              <span className={`risk-pill ${riskClass[student.risk]}`}>{student.risk}</span>
            </div>

            <dl className="student-stats">
              <div>
                <dt>Probability</dt>
                <dd>{Math.round(student.probability * 100)}%</dd>
              </div>
              <div>
                <dt>Grade</dt>
                <dd>{student.grade}</dd>
              </div>
              <div>
                <dt>Absences</dt>
                <dd>{student.absences}</dd>
              </div>
            </dl>

            <ul className="action-list">
              {student.actions.map((action) => (
                <li key={action}>{action}</li>
              ))}
            </ul>
          </article>
        ))}
      </div>
    </section>
  )
}

export default StudentView
