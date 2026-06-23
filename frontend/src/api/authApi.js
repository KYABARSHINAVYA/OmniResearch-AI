import { post } from './client'

export function loginUser(credentials) {
  return post('/login', credentials)
}

export function registerUser(credentials) {
  return post('/signup', credentials)
}
