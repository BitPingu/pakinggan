import { useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import PageHeader from '../components/PageHeader/PageHeader'
import { useAuth } from '../hooks/useAuth'

// Displays account information and account management options.
function SettingsPage() {
  const { user, deleteAccount } = useAuth()
  const navigate = useNavigate()

  // Tracks the current password, submission status, and deletion errors.
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Deletes the account after password verification and final confirmation.
  async function handleDeleteAccount(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')

    const confirmed = window.confirm(
      'Are you sure you want to permanently delete your account? This action cannot be undone.',
    )

    if (!confirmed) {
      return
    }

    setIsSubmitting(true)

    try {
      await deleteAccount(password)
      navigate('/login', { replace: true })
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : 'Unable to delete your account. Please try again.',
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <>
      <PageHeader
        eyebrow="YOUR ACCOUNT"
        title="Settings"
        description="Manage your account information and preferences."
      />

      {/* Account information */}
      <section className="settings-section">
        <h2>Account Information</h2>

        <div className="settings-info">
          <div>
            <span>Username</span>
            <p>{user?.username}</p>
          </div>

          <div>
            <span>Email</span>
            <p>{user?.email}</p>
          </div>
        </div>
      </section>

      {/* Account deletion */}
      <section className="settings-section settings-danger">
        <h2>Delete Account</h2>
        <p>
          Permanently delete your pakinggan account. This action cannot be
          undone. Your account will be removed, but the shared music library
          will remain unaffected.
        </p>

        <form className="settings-delete-form" onSubmit={handleDeleteAccount}>
          <label htmlFor="current-password">Current Password</label>
          <input
            id="current-password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            autoComplete="current-password"
            required
          />

          {error && <p className="form-error">{error}</p>}

          <button type="submit" disabled={isSubmitting || !password}>
            {isSubmitting ? 'Deleting Account...' : 'Delete Account'}
          </button>
        </form>
      </section>
    </>
  )
}

export default SettingsPage
