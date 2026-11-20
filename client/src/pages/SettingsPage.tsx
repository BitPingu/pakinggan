import { useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import PageHeader from '../components/PageHeader/PageHeader'
import { useAuth } from '../hooks/useAuth'

// Displays account information and account management options.
function SettingsPage() {
  const { user, changePassword, deleteAccount } = useAuth()
  const navigate = useNavigate()

  // Tracks the current password, submission status, and deletion errors.
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Tracks password-change inputs, submission status, and errors.
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [passwordError, setPasswordError] = useState('')
  const [isChangingPassword, setIsChangingPassword] = useState(false)

  // Changes the password after validating the form inputs.
  async function handleChangePassword(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setPasswordError('')

    if (newPassword !== confirmPassword) {
      setPasswordError('New passwords do not match.')
      return
    }

    setIsChangingPassword(true)

    try {
      await changePassword(currentPassword, newPassword)
      navigate('/login', { replace: true })
    } catch (error) {
      setPasswordError(
        error instanceof Error
          ? error.message
          : 'Unable to change your password. Please try again.',
      )
    } finally {
      setIsChangingPassword(false)
    }
  }

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

      {/* Password change */}
      <section className="settings-section">
        <h2>Change Password</h2>
        <p>Update your password to keep your account secure.</p>

        <form
          className="settings-password-form"
          onSubmit={handleChangePassword}
        >
          <label htmlFor="change-current-password">Current Password</label>
          <input
            id="change-current-password"
            type="password"
            value={currentPassword}
            onChange={(event) => setCurrentPassword(event.target.value)}
            autoComplete="current-password"
            required
          />

          <label htmlFor="new-password">New Password</label>
          <input
            id="new-password"
            type="password"
            value={newPassword}
            onChange={(event) => setNewPassword(event.target.value)}
            autoComplete="new-password"
            minLength={8}
            maxLength={128}
            required
          />

          <label htmlFor="confirm-password">Confirm New Password</label>
          <input
            id="confirm-password"
            type="password"
            value={confirmPassword}
            onChange={(event) => setConfirmPassword(event.target.value)}
            autoComplete="new-password"
            minLength={8}
            maxLength={128}
            required
          />

          {passwordError && <p className="form-error">{passwordError}</p>}

          <button
            type="submit"
            disabled={
              isChangingPassword ||
              !currentPassword ||
              !newPassword ||
              !confirmPassword
            }
          >
            {isChangingPassword ? 'Changing Password...' : 'Change Password'}
          </button>
        </form>
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
