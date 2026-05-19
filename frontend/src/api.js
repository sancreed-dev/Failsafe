import axios from "axios"

import { API_BASE_URL } from "./config/api"

export { API_BASE_URL } from "./config/api"

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000,
})

export function setAuthToken(token) {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`
  } else {
    delete api.defaults.headers.common.Authorization
  }
}

export function chartUrl(path, cacheKey) {
  let url

  if (!path) {
    url = `${API_BASE_URL}/charts/shap_summary.png`
  } else if (path.startsWith("http://") || path.startsWith("https://")) {
    url = path.startsWith("http://") && import.meta.env.PROD
      ? path.replace(/^http:\/\//, "https://")
      : path
  } else {
    const normalizedPath = path.startsWith("/") ? path : `/${path}`
    url = `${API_BASE_URL}${normalizedPath}`
  }

  if (cacheKey) {
    const separator = url.includes("?") ? "&" : "?"
    return `${url}${separator}v=${encodeURIComponent(cacheKey)}`
  }

  return url
}
