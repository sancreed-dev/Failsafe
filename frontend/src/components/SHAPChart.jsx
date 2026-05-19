import { useState } from "react"

import { chartUrl } from "../api"

function ShapImage({ src, alt }) {
  const [failed, setFailed] = useState(false)

  if (failed) {
    return (
      <p className="status-text">
        Chart image failed to load.{" "}
        <a href={src} target="_blank" rel="noreferrer">
          Open image directly
        </a>
      </p>
    )
  }

  return (
    <img
      src={src}
      alt={alt}
      loading="lazy"
      referrerPolicy="no-referrer"
      onError={() => setFailed(true)}
    />
  )
}

function SHAPChart({ path, explanation, loading, cacheKey }) {
  const summarySrc = chartUrl(path, cacheKey)
  const studentSrc = explanation?.image_url
    ? chartUrl(explanation.image_url, cacheKey)
    : null

  return (
    <section className="grid two-columns">
      <div className="panel">
        <div className="section-heading">
          <h2>Global SHAP Summary</h2>
          <p>Feature impact summary from the retrained XGBoost model.</p>
        </div>
        <div className="shap-frame">
          <ShapImage
            src={summarySrc}
            alt="SHAP summary for failure risk model"
          />
        </div>
      </div>

      <div className="panel">
        <div className="section-heading">
          <h2>Student Explanation</h2>
          <p>Plain-English drivers for the selected student.</p>
        </div>

        {loading && <div className="loading slim">Loading student explanation...</div>}

        {!loading && explanation && (
          <div className="student-explanation">
            <div className="explanation-callout">
              <strong>Student #{explanation.student}</strong>
              <p>{explanation.plain_english}</p>
            </div>
            <div className="mini-shap-frame">
              {studentSrc && (
                <ShapImage
                  src={studentSrc}
                  alt="Student SHAP explanation"
                />
              )}
            </div>
            <div className="reason-list">
              {explanation.top_reasons.slice(0, 3).map((reason) => (
                <article key={reason.feature}>
                  <span>{reason.label}</span>
                  <strong>{reason.value}</strong>
                  <p>{reason.summary}</p>
                </article>
              ))}
            </div>
          </div>
        )}
      </div>
    </section>
  )
}

export default SHAPChart
