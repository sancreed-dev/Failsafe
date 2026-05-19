import { useState } from "react"

import { api, setAuthToken } from "../api"

function LoginPanel({ onLogin }) {
  const [email, setEmail] = useState("faculty@failsafe.edu")
  const [password, setPassword] = useState("failsafe123")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setLoading(true)
    setError("")

    try {
      const response = await api.post("/auth/login", { email, password })
      setAuthToken(response.data.access_token)
      localStorage.setItem("failsafe_token", response.data.access_token)
      localStorage.setItem("failsafe_user", JSON.stringify(response.data.user))
      onLogin(response.data.user, response.data.access_token)
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed")
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="login-shell">
      <nav className="login-nav" aria-label="Login page navigation">
        <div className="brand-mark">
          <span>F</span>
          <strong>FAILSAFE</strong>
        </div>
        <div className="nav-links">
          <span>Predict</span>
          <span>Explain</span>
          <span>Intervene</span>
        </div>
      </nav>

      <section className="login-content">
        <div className="login-hero">
          <p className="eyebrow">Faculty risk intelligence</p>
          <h1>Find at-risk students before the final result.</h1>
          <p>
            FAILSAFE turns uploaded student performance data into early risk
            signals, SHAP-backed explanations, and intervention plans faculty can
            act on with confidence.
          </p>

          <div className="login-stats" aria-label="Platform highlights">
            <article>
              <strong>1,044</strong>
              <span>merged student records</span>
            </article>
            <article>
              <strong>90.43%</strong>
              <span>latest model accuracy</span>
            </article>
            <article>
              <strong>SHAP</strong>
              <span>transparent predictions</span>
            </article>
          </div>
        </div>

        <form className="login-card" onSubmit={handleSubmit}>
          <div className="login-card-head">
            <p className="eyebrow">Secure faculty access</p>
            <h2>Sign in to dashboard</h2>
            <p>Use the demo account to review uploads, risk cards, reports, and explanations.</p>
          </div>

          <label>
            Email
            <input
              autoComplete="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
            />
          </label>
          <label>
            Password
            <input
              autoComplete="current-password"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
          </label>
          {error && <div className="alert">{error}</div>}
          <button className="primary-button" disabled={loading} type="submit">
            {loading ? "Signing in..." : "Open Faculty Dashboard"}
          </button>
          <div className="demo-strip">
            <span>Demo credentials</span>
            <code>faculty@failsafe.edu</code>
            <code>failsafe123</code>
          </div>
        </form>
      </section>
    </main>
  )
}

export default LoginPanel
