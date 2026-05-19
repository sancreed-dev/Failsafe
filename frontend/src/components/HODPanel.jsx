function HODPanel({ dashboard, analytics }) {
  const cards = [
    ["Total Students", dashboard.students],
    ["High Risk", dashboard.high_risk],
    ["Medium Risk", dashboard.medium],
    ["Interventions", analytics?.interventions_required ?? 0],
    ["Failure Rate", `${dashboard.failure_rate}%`],
    ["Avg Grade", dashboard.average_grade],
  ]

  return (
    <section className="metric-grid">
      {cards.map(([label, value]) => (
        <article className="metric-card" key={label}>
          <span>{label}</span>
          <strong>{value}</strong>
        </article>
      ))}
    </section>
  )
}

export default HODPanel
