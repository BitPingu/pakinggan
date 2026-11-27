import { useEffect, useRef, useState } from 'react'
import { Clock, Disc3, History, Music, Music2, Users } from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'

import { getLastFMStatus, getNowPlaying } from '../api/lastfm'
import {
  getListeningHistory,
  syncListeningHistory,
} from '../api/listening-history'
import type { ListeningHistoryEntry } from '../types/listening-history'
import EmptyState from '../components/EmptyState/EmptyState'
import PageHeader from '../components/PageHeader/PageHeader'
import { useLibrary } from '../hooks/useLibrary'

import type { LastFMTrack } from '../types/lastfm'

// Formats a timestamp into a readable date and time.
function formatPlayedAt(timestamp: string) {
  return new Date(timestamp).toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

// Displays the dashboard and library statistics.
function DashboardPage() {
  const { artists, albums, tracks, isLoading, error } = useLibrary()
  const location = useLocation()

  // Stores the user's currently playing Last.fm track.
  const [nowPlaying, setNowPlaying] = useState<LastFMTrack | null>(null)

  // Tracks whether the currently playing track is loading.
  const [isNowPlayingLoading, setIsNowPlayingLoading] = useState(true)

  // Stores the identifier of the previously detected Now Playing track.
  const previousTrack = useRef<string | null>(null)

  // Stores the pending listening history refresh timeout.
  const historyRefreshTimeout = useRef<ReturnType<typeof setTimeout> | null>(
    null,
  )

  // Tracks whether listening history is currently being refreshed.
  const isRefreshingHistory = useRef(false)

  // Stores the user's five most recently played tracks.
  const [recentHistory, setRecentHistory] = useState<ListeningHistoryEntry[]>(
    [],
  )

  // Tracks whether the recent listening history is loading.
  const [isRecentHistoryLoading, setIsRecentHistoryLoading] = useState(true)

  // Fetches the user's currently playing Last.fm track.
  useEffect(() => {
    let isFetching = false

    async function fetchNowPlaying() {
      if (isFetching) return

      isFetching = true

      try {
        const result = await getNowPlaying()
        const track = result.track

        setNowPlaying(track)

        // Identifies the currently playing track.
        const trackIdentifier = track
          ? `${track.artist.toLowerCase()}-${track.name.toLowerCase()}`
          : null

        // Detects when the currently playing track changes.
        if (trackIdentifier && previousTrack.current !== trackIdentifier) {
          const hasPreviousTrack = previousTrack.current !== null
          previousTrack.current = trackIdentifier

          // Refreshes listening history after a new track starts.
          if (hasPreviousTrack) {
            // Clears any previously scheduled refresh.
            if (historyRefreshTimeout.current) {
              clearTimeout(historyRefreshTimeout.current)
            }

            historyRefreshTimeout.current = setTimeout(async () => {
              historyRefreshTimeout.current = null

              if (isRefreshingHistory.current) return

              isRefreshingHistory.current = true

              try {
                const status = await getLastFMStatus()

                if (status.connected) {
                  await syncListeningHistory()
                }

                const entries = await getListeningHistory(5)
                setRecentHistory(entries)
              } catch {
                // Keeps the currently displayed listening history.
              } finally {
                isRefreshingHistory.current = false
              }
            }, 30_000)
          }
        }
      } catch {
        setNowPlaying(null)
      } finally {
        isFetching = false
        setIsNowPlayingLoading(false)
      }
    }

    fetchNowPlaying()

    const interval = setInterval(fetchNowPlaying, 15_000)

    return () => {
      clearInterval(interval)

      if (historyRefreshTimeout.current) {
        clearTimeout(historyRefreshTimeout.current)
      }
    }
  }, [])

  // Syncs Last.fm and fetches the user's five most recently played tracks.
  useEffect(() => {
    let isMounted = true

    async function fetchRecentHistory() {
      setIsRecentHistoryLoading(true)

      // Prevents overlapping Last.fm synchronization requests.
      const shouldRefresh = !isRefreshingHistory.current

      if (shouldRefresh) {
        isRefreshingHistory.current = true
      }

      // Checks whether the user has connected their Last.fm account.
      try {
        if (shouldRefresh) {
          const status = await getLastFMStatus()

          // Imports the latest listening activity from Last.fm.
          if (status.connected) {
            await syncListeningHistory()
          }
        }
      } catch {
        // Continues using the listening history already stored locally.
      }

      // Fetches the latest listening history from PostgreSQL.
      try {
        const entries = await getListeningHistory(5)

        if (isMounted) {
          setRecentHistory(entries)
        }
      } catch {
        if (isMounted) {
          setRecentHistory([])
        }
      } finally {
        if (shouldRefresh) {
          isRefreshingHistory.current = false
        }

        if (isMounted) {
          setIsRecentHistoryLoading(false)
        }
      }
    }

    fetchRecentHistory()

    return () => {
      isMounted = false
    }
  }, [location.key])

  // Dashboard statistics displayed in the stat cards.
  const statistics = [
    {
      label: 'Total Tracks',
      value: isLoading ? '…' : error ? '—' : tracks.length.toString(),
      icon: Music,
    },
    {
      label: 'Artists',
      value: isLoading ? '…' : error ? '—' : artists.length.toString(),
      icon: Users,
    },
    {
      label: 'Albums',
      value: isLoading ? '…' : error ? '—' : albums.length.toString(),
      icon: Disc3,
    },
    { label: 'Listening Time', value: '—', icon: Clock },
  ]

  return (
    <>
      {/* Dashboard page heading */}
      <PageHeader
        eyebrow="YOUR MUSIC"
        title="Dashboard"
        description="Your listening activity, all in one place."
      />

      {/* Library statistics */}
      <section className="dashboard-stats">
        {statistics.map((stat) => (
          <div className="stat-card" key={stat.label}>
            <div className="stat-card-header">
              <span>{stat.label}</span>
              <stat.icon size={18} strokeWidth={1.8} aria-hidden="true" />
            </div>
            <h2>{stat.value}</h2>
          </div>
        ))}
      </section>

      {/* Currently playing track */}
      <section className="dashboard-section">
        <div className="dashboard-section-header">
          <h2>Now Playing</h2>

          <Link to="/now-playing" className="dashboard-section-link">
            <Music size={16} />
            Explore Track
          </Link>
        </div>

        {isNowPlayingLoading ? (
          <EmptyState message="Checking what you're listening to…" />
        ) : nowPlaying ? (
          <div className="now-playing-card">
            {nowPlaying.image && (
              <img
                src={nowPlaying.image}
                alt={`${nowPlaying.album ?? nowPlaying.name} album artwork`}
                className="now-playing-artwork"
              />
            )}

            <div className="now-playing-info">
              <span className="now-playing-indicator">
                <span className="now-playing-dot" />
                NOW PLAYING
              </span>

              <h3>{nowPlaying.name}</h3>

              <p>{nowPlaying.artist}</p>

              {nowPlaying.album && <span>{nowPlaying.album}</span>}
            </div>
          </div>
        ) : (
          <EmptyState
            icon={Music2}
            title="Nothing playing right now"
            description="Your currently playing track will appear here when you listen to music on Last.fm."
          />
        )}
      </section>

      {/* Dashboard loading error */}
      {error && <p className="form-error">{error}</p>}

      {/* Recently played tracks section */}
      <section className="dashboard-section">
        <div className="dashboard-section-header">
          <h2>Recently Played</h2>

          <Link to="/history" className="dashboard-section-link">
            <History size={16} />
            View History
          </Link>
        </div>

        {isRecentHistoryLoading ? (
          <EmptyState message="Loading listening history…" />
        ) : recentHistory.length === 0 ? (
          <EmptyState
            icon={Music2}
            title="No listening history yet"
            description="Your recently played tracks will appear here once you start tracking your listening activity."
          />
        ) : (
          <div className="history-list">
            {recentHistory.map((entry) => (
              <div className="history-entry" key={entry.id}>
                <div className="history-entry-info">
                  <h3>{entry.track.title}</h3>

                  <p>
                    {entry.track.artist.name}
                    {entry.track.album && ` · ${entry.track.album.title}`}
                  </p>
                </div>

                <span className="history-entry-date">
                  {formatPlayedAt(entry.played_at)}
                </span>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Top artists section */}
      <section className="dashboard-section">
        <h2>Top Artists</h2>
        <EmptyState
          icon={Users}
          title="No listening data yet"
          description="Your most listened-to artists will appear here once you start tracking your listening activity."
        />
      </section>
    </>
  )
}

export default DashboardPage
