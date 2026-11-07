import { useEffect, useState } from 'react'
import { getArtists } from '../api/artists'
import type { Artist } from '../types/music'

// Displays the dashboard overview and library statistics.
function DashboardPage() {
  // Stores the artists retrieved from the backend.
  const [artists, setArtists] = useState<Artist[]>([])

  // Tracks whether the artist request is still running.
  const [isLoading, setIsLoading] = useState(true)

  // Fetches artists when the dashboard first loads.
  useEffect(() => {
    async function fetchArtists() {
      try {
        // Retrieve all artists from the API.
        const data = await getArtists()

        // Update the artist list with the API response.
        setArtists(data)
      } catch (error) {
        // Log an error if the artist request fails.
        console.error('Unable to load artists:', error)
      } finally {
        // Stop displaying the loading state.
        setIsLoading(false)
      }
    }

    fetchArtists()
  }, [])

  // Dashboard statistics displayed in the overview cards.
  const statistics = [
    { label: 'Total Tracks', value: '0' },
    {
      label: 'Artists',
      value: isLoading ? '...' : artists.length.toString(),
    },
    { label: 'Albums', value: '0' },
    { label: 'Listening Time', value: '0 hrs' },
  ]

  return (
    <>
      {/* Dashboard page heading */}
      <header className="page-header">
        <span className="page-eyebrow">YOUR MUSIC</span>
        <h1>Overview</h1>
        <p className="page-description">
          Your listening activity, all in one place.
        </p>
      </header>

      {/* Library statistics */}
      <section className="dashboard-stats">
        {statistics.map((stat) => (
          <div className="stat-card" key={stat.label}>
            <span>{stat.label}</span>
            <h2>{stat.value}</h2>
          </div>
        ))}
      </section>

      {/* Recently played tracks section */}
      <section className="dashboard-section">
        <h2>Recently Played</h2>
        <div className="dashboard-empty-state">
          <span className="empty-state-icon">♫</span>
          <h3>No listening history yet</h3>
          <p>
            Your recently played tracks will appear here once you start tracking
            your listening activity.
          </p>
        </div>
      </section>

      {/* Top artists section */}
      <section className="dashboard-section">
        <h2>Top Artists</h2>
        <div className="dashboard-empty-state">
          <span className="empty-state-icon">♪</span>
          <h3>No listening data yet</h3>
          <p>
            Your most listened-to artists will appear here once you start
            tracking your listening activity.
          </p>
        </div>
      </section>
    </>
  )
}

export default DashboardPage
