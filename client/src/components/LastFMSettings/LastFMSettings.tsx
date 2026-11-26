import { useEffect, useState } from 'react'
import {
  connectLastFM,
  disconnectLastFM,
  getLastFMStatus,
} from '../../api/lastfm'
import type { LastFMStatus } from '../../types/lastfm'
import './LastFMSettings.css'

interface LastFMSettingsProps {
  successMessage: {
    text: string
    type: 'success' | 'error' | 'warning'
  } | null
}

// Displays and manages the user's Last.fm connection.
function LastFMSettings({ successMessage }: LastFMSettingsProps) {
  const [connection, setConnection] = useState<LastFMStatus | null>(null)
  const [error, setError] = useState('')
  const [isDisconnecting, setIsDisconnecting] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  // Fetches the user's Last.fm connection status.
  useEffect(() => {
    getLastFMStatus()
      .then(setConnection)
      .catch(() => setError('Unable to retrieve Last.fm connection status.'))
      .finally(() => setIsLoading(false))
  }, [])

  // Connects the user's Last.fm account.
  async function handleConnect() {
    setError('')

    try {
      await connectLastFM()
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : 'Unable to connect your Last.fm account.',
      )
    }
  }

  // Disconnects the user's Last.fm account.
  async function handleDisconnect() {
    setError('')
    setIsDisconnecting(true)

    try {
      await disconnectLastFM()
      setConnection({ connected: false, lastfm_username: null })
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : 'Unable to disconnect your Last.fm account.',
      )
    } finally {
      setIsDisconnecting(false)
    }
  }

  return (
    <section className="settings-section">
      <h2>Last.fm Integration</h2>
      <p className="lastfm-description">
        Connect your Last.fm account to track your listening activity.
      </p>

      {isLoading ? (
        // Displays a loading message while retrieving connection status.
        <p>Loading connection status...</p>
      ) : connection === null ? null : connection.connected ? (
        // Displays the disconnect button and connected account information.
        <div className="lastfm-connection">
          <button
            className="lastfm-button lastfm-disconnect-button"
            onClick={handleDisconnect}
            disabled={isDisconnecting}
          >
            {isDisconnecting ? 'Disconnecting...' : 'Disconnect Last.fm'}
          </button>
          <p className="lastfm-status lastfm-status-connected">
            <span className="lastfm-status-indicator" />
            Connected as <strong>{connection.lastfm_username}</strong>
          </p>
        </div>
      ) : (
        // Displays the connect button when no Last.fm account is connected.
        <div className="lastfm-connection">
          <button
            className="lastfm-button lastfm-connect-button"
            onClick={handleConnect}
          >
            Connect Last.fm
          </button>
        </div>
      )}

      {/* Displays an error if a connection operation fails. */}
      {error && <p className="form-error">{error}</p>}

      {/* Displays feedback after Last.fm authorization. */}
      {successMessage && (
        <p
          className={
            successMessage.type === 'success'
              ? 'form-success'
              : successMessage.type === 'error'
                ? 'form-error'
                : 'lastfm-warning'
          }
        >
          {successMessage.text}
        </p>
      )}
    </section>
  )
}

export default LastFMSettings
