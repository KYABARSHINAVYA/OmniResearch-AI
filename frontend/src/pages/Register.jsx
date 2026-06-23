import { useState } from 'react'
import { registerUser } from '../api/authApi'

export default function Register({ onNavigate }) {
  const [form, setForm] = useState({ email: '', password: '', confirmPassword: '' })
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

    if (form.password !== form.confirmPassword) {
      setStatus('Passwords do not match.')
      return
    }

    setIsSubmitting(true)

    try {
      const data = await registerUser({
        email: form.email,
        password: form.password,
      })

      if (data.message === 'User already exists') {
        setStatus(data.message)
        return
      }

      setStatus(data.message || 'Signup successful.')
      onNavigate('login')
    } catch (error) {
      setStatus(error.message || 'Registration failed. Try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <section className="auth-layout">
      <div className="auth-copy">
        <p className="eyebrow">New workspace</p>
        <h2>Create an OmniResearch account.</h2>
        <p>
          Register to start tracking research sessions, approvals, dashboards,
          and saved checkpoints from one console.
        </p>
      </div>

      <form className="auth-form" onSubmit={handleSubmit}>
        <div className="panel-header">
          <div>
            <h2>Register</h2>
            <span>Register with your email</span>
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
            autoComplete="new-password"
            minLength="6"
            required
          />
        </label>

        <label>
          <span>Confirm password</span>
          <input
            name="confirmPassword"
            type="password"
            value={form.confirmPassword}
            onChange={handleChange}
            autoComplete="new-password"
            minLength="6"
            required
          />
        </label>

        {status && <p className="inline-error">{status}</p>}

        <button type="submit" className="primary-button" disabled={isSubmitting}>
          {isSubmitting ? 'Creating...' : 'Create account'}
        </button>

        <button type="button" className="ghost-button" onClick={() => onNavigate('login')}>
          Back to login
        </button>
      </form>
    </section>
  )
}
