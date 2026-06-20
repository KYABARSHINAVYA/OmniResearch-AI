import { get } from './client'

export async function getAnalytics() {
  return get('/analytics')
}
