import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { ApiError } from '../api/request'

// Allows users to create a pakinggan account.
function RegisterPage() {
  const { register } = useAuth()
  const navigate = useNavigate()

  // Tracks form inputs, submission status, and registration errors.
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Registers the user and redirects to the login page.
  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')

    // Validates registration inputs before submitting the request.
    const trimmedUsername = username.trim()

    if (trimmedUsername.length < 3 || trimmedUsername.length > 30) {
      setError('Username must be between 3 and 30 characters.')
      return
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match.')
      return
    }

    if (password.length < 8 || password.length > 128) {
      setError('Password must be between 8 and 128 characters.')
      return
    }

    setIsSubmitting(true)

    try {
      await register(trimmedUsername, email.trim().toLowerCase(), password)
      navigate('/login')
    } catch (error) {
      if (error instanceof ApiError && error.status === 409) {
        setError(
          'That username or email is already registered. Please try another.',
        )
      } else {
        setError('Unable to create your account. Please try again.')
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="login-page">
      <form className="login-form" onSubmit={handleSubmit}>
        <h1>Create an account</h1>
        <p className="login-description">Sign up for your pakinggan account.</p>

        <label htmlFor="username">Username</label>
        <input
          id="username"
          type="text"
          value={username}
          onChange={(event) => setUsername(event.target.value)}
          autoComplete="username"
          required
        />

        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          autoComplete="email"
          required
        />

        <label htmlFor="password">Password</label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          autoComplete="new-password"
          required
        />

        <label htmlFor="confirm-password">Confirm password</label>
        <input
          id="confirm-password"
          type="password"
          value={confirmPassword}
          onChange={(event) => setConfirmPassword(event.target.value)}
          autoComplete="new-password"
          required
        />

        {error && <p className="form-error">{error}</p>}

        <button
          type="submit"
          disabled={
            isSubmitting ||
            !username.trim() ||
            !email.trim() ||
            !confirmPassword
          }
        >
          {isSubmitting ? 'Creating account...' : 'Create account'}
        </button>

        <p className="login-description">
          Already have an account? <Link to="/login">Log in</Link>
        </p>
      </form>
    </main>
  )
}

export default RegisterPage
