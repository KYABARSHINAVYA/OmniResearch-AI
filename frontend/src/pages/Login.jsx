import { useState } from 'react'
import { loginUser } from '../api/authApi'

export default function Login({ onNavigate, onLogin }) {
  const [form, setForm] = useState({ email: '', password: '' })
  const [status, setStatus] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleChange = (event) => {
    setForm((current) => ({
      ...current,
      [event.target.name]: event.target.value,
    }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setStatus('')
    setIsSubmitting(true)

    try {
      const data = await loginUser(form)

      if (!data.access_token) {
        setStatus(data.message || 'Login failed. Check your username and password.')
        return
      }

      localStorage.setItem('omniresearch_token', data.access_token)
      setStatus('Login successful.')
      onLogin()
    } catch (error) {
      setStatus(error.message || 'Login failed. Try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <section className="auth-layout">
      <div className="auth-copy">
        <p className="eyebrow">Secure access</p>
        <h2>Welcome back to OmniResearch.</h2>
        <p>
          Sign in to return to your research console, monitor agents, and continue
          active workflows.
        </p>
      </div>

      <form className="auth-form" onSubmit={handleSubmit}>
        <div className="panel-header">
          <div>
            <h2>Login</h2>
            <span>Use your registered email</span>
          </div>
        </div>

        <label>
          <span>Email</span>
          <input
            name="email"
            type="email"
            value={form.email}
            onChange={handleChange}
            autoComplete="email"
            required
          />
        </label>

        <label>
          <span>Password</span>
          <input
            name="password"
            type="password"
            value={form.password}
            onChange={handleChange}
            autoComplete="current-password"
            required
          />
        </label>

        {status && <p className="inline-error">{status}</p>}

        <button type="submit" className="primary-button" disabled={isSubmitting}>
          {isSubmitting ? 'Signing in...' : 'Sign in'}
        </button>

        <button type="button" className="ghost-button" onClick={() => onNavigate('register')}>
          Create account
        </button>
      </form>
    </section>
  )
}
