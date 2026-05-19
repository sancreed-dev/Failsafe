import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"

const COLORS = {
  HIGH: "#dc2626",
  MEDIUM: "#f59e0b",
  LOW: "#16a34a",
}

function Dashboard({ data }) {
  const metrics = data.model_metrics || {}
  const metricCards = [
    ["Accuracy", metrics.accuracy],
    ["Precision", metrics.precision],
    ["Recall", metrics.recall],
    ["F1 Score", metrics.f1],
  ]

  return (
    <section className="grid dashboard-grid">
      <div className="panel">
        <div className="section-heading">
          <h2>Risk Distribution</h2>
          <p>Current model predictions across both subjects.</p>
        </div>
        <div className="chart-box">
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={data.risk_distribution}
                dataKey="value"
                nameKey="name"
                innerRadius={72}
                outerRadius={104}
                paddingAngle={3}
              >
                {data.risk_distribution.map((entry) => (
                  <Cell key={entry.name} fill={COLORS[entry.name]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="panel">
        <div className="section-heading">
          <h2>Model Quality</h2>
          <p>Evaluation metrics from the latest retraining run.</p>
        </div>
        <div className="quality-grid">
          {metricCards.map(([label, value]) => (
            <div className="quality-card" key={label}>
              <span>{label}</span>
              <strong>{value ?? "N/A"}</strong>
            </div>
          ))}
        </div>
        {metrics.confusion_matrix && (
          <div className="confusion-box">
            <span>Confusion matrix</span>
            <code>{JSON.stringify(metrics.confusion_matrix)}</code>
          </div>
        )}
      </div>

      <div className="panel">
        <div className="section-heading">
          <h2>Subject Breakdown</h2>
          <p>High-risk students by dataset after merge.</p>
        </div>
        <div className="chart-box">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={data.subject_summary}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="subject" />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="high_risk" name="High risk" fill="#dc2626" radius={[6, 6, 0, 0]} />
              <Bar dataKey="medium_risk" name="Medium risk" fill="#f59e0b" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </section>
  )
}

export default Dashboard
