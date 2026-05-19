function normalizeBaseUrl(raw) {
  const value = (raw || "").trim()
  if (!value) {
    return "http://127.0.0.1:8000"
  }

  const withoutTrailingSlash = value.replace(/\/+$/, "")

  if (import.meta.env.PROD && withoutTrailingSlash.startsWith("http://")) {
    return withoutTrailingSlash.replace(/^http:\/\//, "https://")
  }

  return withoutTrailingSlash
}

export const API_BASE_URL = normalizeBaseUrl(
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000",
)
