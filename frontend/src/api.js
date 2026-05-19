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

export function chartUrl(path) {
  if (!path) return `${API_BASE_URL}/charts/shap_summary.png`
  if (path.startsWith("http")) return path
  return `${API_BASE_URL}${path}`
}
