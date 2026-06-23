import { get, post } from './client'

export async function sendMessage(message) {
  return post('/chat', { question: message.question || message, mode: message.mode || 'balanced' })
}

export async function getResearchHistory() {
  return get('/chat/history')
}

export async function runAutonomousResearch(topic, urls = []) {
  return post('/research/autonomous', { topic, urls })
}
