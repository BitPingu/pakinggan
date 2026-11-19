import { useEffect, useState } from 'react'
import { getArtists } from '../api/artists'
import { getAlbums } from '../api/albums'
import type { Album, Artist } from '../types/music'
import PageHeader from '../components/common/PageHeader'
import EmptyState from '../components/common/EmptyState'
import { Clock, Disc3, Music, Music2, Users } from 'lucide-react'

// Displays the dashboard and library statistics.
function DashboardPage() {
  // Stores the artists retrieved from the backend.
  const [artists, setArtists] = useState<Artist[]>([])

  // Stores the albums retrieved from the backend.
  const [albums, setAlbums] = useState<Album[]>([])

  // Tracks whether dashboard data is still loading.
  const [isLoading, setIsLoading] = useState(true)

  // Stores an error if dashboard data cannot be retrieved.
  const [error, setError] = useState<string | null>(null)

  // Fetches dashboard data when the page first loads.
  useEffect(() => {
    async function fetchDashboardData() {
      try {
        // Retrieve artists and albums concurrently.
        const [artistData, albumData] = await Promise.all([
          getArtists(),
          getAlbums(),
        ])

        // Update the dashboard data.
        setArtists(artistData)
        setAlbums(albumData)
      } catch (error) {
        // Log the error for debugging.
        console.error('Unable to load dashboard data:', error)

        // Display an error message on the dashboard.
        setError('Unable to load dashboard data. Please try again.')
      } finally {
        // Stop displaying the loading state.
        setIsLoading(false)
      }
    }

    fetchDashboardData()
  }, [])

  // Dashboard statistics displayed in the stat cards.
  const statistics = [
    { label: 'Total Tracks', value: '—', icon: Music },
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
