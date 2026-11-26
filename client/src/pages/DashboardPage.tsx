import { useEffect, useState } from 'react'
import { Clock, Disc3, Music, Music2, Users } from 'lucide-react'

import { getNowPlaying } from '../api/lastfm'
import EmptyState from '../components/EmptyState/EmptyState'
import PageHeader from '../components/PageHeader/PageHeader'
import { useLibrary } from '../hooks/useLibrary'

import type { LastFMTrack } from '../types/lastfm'

// Displays the dashboard and library statistics.
function DashboardPage() {
  const { artists, albums, tracks, isLoading, error } = useLibrary()

  // Stores the user's currently playing Last.fm track.
  const [nowPlaying, setNowPlaying] = useState<LastFMTrack | null>(null)

  // Tracks whether the currently playing track is loading.
  const [isNowPlayingLoading, setIsNowPlayingLoading] = useState(true)

  // Fetches the user's currently playing Last.fm track.
  useEffect(() => {
    let isFetching = false

    async function fetchNowPlaying() {
      if (isFetching) return

      isFetching = true

      try {
        const result = await getNowPlaying()
        setNowPlaying(result.track)
      } catch {
        setNowPlaying(null)
      } finally {
        isFetching = false
        setIsNowPlayingLoading(false)
      }
    }

    fetchNowPlaying()

    const interval = setInterval(fetchNowPlaying, 15_000)

    return () => clearInterval(interval)
  }, [])

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
        <h2>Now Playing</h2>

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
        <h2>Recently Played</h2>
        <EmptyState
          icon={Music2}
          title="No listening history yet"
          description="Your recently played tracks will appear here once you start tracking your listening activity."
        />
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
