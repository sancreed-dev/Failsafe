import { useCallback, useEffect, useMemo, useState } from "react"

import Dashboard from "./pages/Dashboard"
import StudentView from "./pages/StudentView"
import Upload from "./pages/Upload"
import HODPanel from "./components/HODPanel"
import LoginPanel from "./components/LoginPanel"
import SHAPChart from "./components/SHAPChart"
import TrendGraph from "./components/TrendGraph"
import { api, API_BASE_URL, setAuthToken } from "./api"

function App() {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem("failsafe_user")
    return saved ? JSON.parse(saved) : null
  })
  const [dashboard, setDashboard] = useState(null)
  const [analytics, setAnalytics] = useState(null)
  const [students, setStudents] = useState([])
  const [selectedStudent, setSelectedStudent] = useState(null)
  const [studentExplanation, setStudentExplanation] = useState(null)
  const [loading, setLoading] = useState(Boolean(user))
  const [detailLoading, setDetailLoading] = useState(false)
  const [error, setError] = useState("")

  useEffect(() => {
    const token = localStorage.getItem("failsafe_token")
    if (token) setAuthToken(token)
  }, [])

  const loadData = useCallback(async () => {
    setLoading(true)
    setError("")

    try {
      const [dashboardRes, analyticsRes, studentsRes] = await Promise.all([
        api.get("/dashboard"),
        api.get("/faculty/analytics"),
        api.post("/predict"),
      ])

      setDashboard(dashboardRes.data)
      setAnalytics(analyticsRes.data)
      setStudents(studentsRes.data)
      setSelectedStudent((current) => current || studentsRes.data[0] || null)
    } catch (err) {
      if (err.response?.status === 401) {
        logout()
        return
      }
      setError(
        err.response?.data?.detail ||
          `Could not reach the FAILSAFE API at ${API_BASE_URL}.`,
      )
    } finally {
      setLoading(false)
    }
  }, [])

  const loadExplanation = useCallback(async (student) => {
    if (!student) return
    setSelectedStudent(student)
    setDetailLoading(true)

    try {
      const response = await api.get(`/students/${student.student}/explanation`)
      setStudentExplanation(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || "Could not load SHAP explanation.")
    } finally {
      setDetailLoading(false)
    }
  }, [])

  useEffect(() => {
    if (!user) return undefined
    const timer = window.setTimeout(loadData, 0)
    return () => window.clearTimeout(timer)
  }, [loadData, user])

  useEffect(() => {
    if (!selectedStudent) return undefined
    const timer = window.setTimeout(() => loadExplanation(selectedStudent), 0)
    return () => window.clearTimeout(timer)
  }, [loadExplanation, selectedStudent])

  const visibleStudents = useMemo(
    () =>
      [...students]
        .sort((a, b) => b.probability - a.probability)
        .slice(0, 18),
    [students],
  )

  async function downloadReport() {
    const response = await api.get("/report", { responseType: "blob" })
    const url = URL.createObjectURL(response.data)
    const link = document.createElement("a")
    link.href = url
    link.download = "failsafe_report.pdf"
    link.click()
    URL.revokeObjectURL(url)
  }

  function handleLogin(nextUser) {
    setUser(nextUser)
  }

  function logout() {
    localStorage.removeItem("failsafe_token")
    localStorage.removeItem("failsafe_user")
    setAuthToken("")
    setUser(null)
    setDashboard(null)
    setAnalytics(null)
    setStudents([])
    setSelectedStudent(null)
    setStudentExplanation(null)
  }

  if (!user) {
    return <LoginPanel onLogin={handleLogin} />
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Student failure prediction system</p>
          <h1>FAILSAFE</h1>
        </div>
        <div className="header-actions">
          <span>{user.name}</span>
          <button className="secondary-button" type="button" onClick={downloadReport}>
            PDF Report
          </button>
          <button className="ghost-button" type="button" onClick={logout}>
            Logout
          </button>
        </div>
      </header>

      <Upload onComplete={loadData} />

      {error && <div className="alert">{error}</div>}
      {loading && <div className="loading">Loading latest predictions...</div>}

      {!loading && dashboard && (
        <>
          <HODPanel dashboard={dashboard} analytics={analytics} />
          <Dashboard data={dashboard} />
          <TrendGraph data={dashboard.subject_summary || []} snapshots={dashboard.snapshots || []} />
          <SHAPChart path={dashboard.shap_url} explanation={studentExplanation} loading={detailLoading} />
          <StudentView
            students={visibleStudents}
            selectedStudent={selectedStudent}
            onSelectStudent={loadExplanation}
          />
        </>
      )}
    </main>
  )
}

export default App
