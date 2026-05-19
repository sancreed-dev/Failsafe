import { useState } from "react"

import { api } from "../api"

function Upload({ onComplete }) {
  const [status, setStatus] = useState("")
  const [uploading, setUploading] = useState(false)

  async function uploadFiles(event) {
    const files = Array.from(event.target.files || [])
    const mathFile = files.find((file) => file.name === "student-mat.csv")
    const porFile = files.find((file) => file.name === "student-por.csv")

    if (!mathFile || !porFile) {
      setStatus("Select both student-mat.csv and student-por.csv.")
      return
    }

    const formData = new FormData()
    formData.append("math_file", mathFile)
    formData.append("por_file", porFile)

    setUploading(true)
    setStatus("Uploading datasets and retraining model...")

    try {
      const response = await api.post("/upload", formData)
      setStatus(`Model retrained. Accuracy: ${response.data.accuracy}`)
      await onComplete()
    } catch (err) {
      setStatus(err.response?.data?.detail || "Upload failed.")
    } finally {
      setUploading(false)
      event.target.value = ""
    }
  }

  return (
    <section className="upload-panel">
      <div>
        <h2>Upload Datasets</h2>
        <p>Accepts the original UCI CSV files and refreshes predictions.</p>
      </div>
      <label className="file-button">
        <input
          type="file"
          accept=".csv"
          multiple
          disabled={uploading}
          onChange={uploadFiles}
        />
        Choose CSVs
      </label>
      {status && <p className="status-text">{status}</p>}
    </section>
  )
}

export default Upload
