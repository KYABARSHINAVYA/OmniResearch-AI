import { post } from './client'

export async function sendMessage(message) {
  return post('/chat', { question: message.question || message, mode: message.mode || 'balanced' })
}

export async function runAutonomousResearch(topic, urls = []) {
  return post('/research/autonomous', { topic, urls })
}
