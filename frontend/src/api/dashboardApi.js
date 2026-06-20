import { get } from './client'

export async function getDashboard() {
  return get('/dashboard')
}

export async function getCheckpoint() {
  return get('/checkpoint')
}

export async function requestPause() {
  return get('/pause')
}

export async function approveWorkflow() {
  return get('/approve')
}

export async function getArchitecture() {
  return get('/architecture')
}

export async function getLlmStatus() {
  return get('/llm/status')
}
