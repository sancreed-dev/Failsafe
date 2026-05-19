import {
  CartesianGrid,
  Line,
  LineChart,
  Area,
  AreaChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"

function TrendGraph({ data, snapshots }) {
  const chartData = data.map((item) => ({
    subject: item.subject,
    average_grade: item.average_grade,
    average_absences: item.average_absences,
  }))
  const snapshotData = snapshots.map((item, index) => ({
    run: `Run ${index + 1}`,
    high: item.high_risk,
    medium: item.medium_risk,
  }))

  return (
    <section className="grid two-columns">
      <div className="panel">
        <div className="section-heading">
          <h2>Faculty Analytics</h2>
          <p>Grade and attendance signals faculty can act on.</p>
        </div>
        <div className="chart-box">
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="subject" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="average_grade" stroke="#2563eb" strokeWidth={3} />
              <Line type="monotone" dataKey="average_absences" stroke="#dc2626" strokeWidth={3} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="panel">
        <div className="section-heading">
          <h2>Risk Snapshot History</h2>
          <p>Stored after uploads and model retraining.</p>
        </div>
        <div className="chart-box">
          <ResponsiveContainer width="100%" height={260}>
            <AreaChart data={snapshotData}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="run" />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Area dataKey="high" stroke="#dc2626" fill="#fecaca" />
              <Area dataKey="medium" stroke="#f59e0b" fill="#fde68a" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </section>
  )
}

export default TrendGraph
