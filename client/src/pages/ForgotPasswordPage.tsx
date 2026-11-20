import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { forgotPassword } from '../api/auth'

// Allows users to request a password-reset email.
function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Requests a password-reset link for the submitted email.
  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setMessage('')
    setError('')
    setIsSubmitting(true)

    try {
      const response = await forgotPassword(email.trim().toLowerCase())
      setMessage(response.message)
    } catch {
      setError('Unable to process your request. Please try again later.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="login-page">
      <form className="login-form" onSubmit={handleSubmit}>
        <h1>Forgot password?</h1>
        <p className="login-description">
          Enter the email address associated with your account. If an account
          exists, we'll send you a link to reset your password.
        </p>

        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          autoComplete="email"
          required
        />

        {message && <p className="login-description">{message}</p>}
        {error && <p className="form-error">{error}</p>}

        <button type="submit" disabled={isSubmitting || !email.trim()}>
          {isSubmitting ? 'Sending...' : 'Send reset link'}
        </button>

        <p className="login-description">
          Remember your password? <Link to="/login">Log in</Link>
        </p>
      </form>
    </main>
  )
}

export default ForgotPasswordPage
