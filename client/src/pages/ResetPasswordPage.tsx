import { useState, type FormEvent } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { resetPassword } from '../api/auth'

// Allows users to reset their password using an emailed token.
function ResetPasswordPage() {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token')

  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Validates and submits the new password.
  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setMessage('')
    setError('')

    if (!token) {
      setError('This password-reset link is invalid or expired.')
      return
    }

    if (password.length < 8 || password.length > 128) {
      setError('Password must be between 8 and 128 characters.')
      return
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match.')
      return
    }

    setIsSubmitting(true)

    try {
      const response = await resetPassword(token, password)
      setMessage(response.message)
      setPassword('')
      setConfirmPassword('')
    } catch {
      setError('This password-reset link is invalid or expired.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="login-page">
      <form className="login-form" onSubmit={handleSubmit}>
        <h1>Reset password</h1>
        <p className="login-description">
          Enter a new password for your pakinggan account.
        </p>

        {!message && (
          <>
            <label htmlFor="password">New password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              autoComplete="new-password"
              required
            />

            <label htmlFor="confirm-password">Confirm new password</label>
            <input
              id="confirm-password"
              type="password"
              value={confirmPassword}
              onChange={(event) => setConfirmPassword(event.target.value)}
              autoComplete="new-password"
              required
            />
          </>
        )}

        {message && <p className="login-description">{message}</p>}
        {error && <p className="form-error">{error}</p>}

        {!message && (
          <button
            type="submit"
            disabled={isSubmitting || !password || !confirmPassword || !token}
          >
            {isSubmitting ? 'Resetting password...' : 'Reset password'}
          </button>
        )}

        <p className="login-description">
          <Link to="/login">Back to login</Link>
        </p>
      </form>
    </main>
  )
}

export default ResetPasswordPage
