import { useEffect, useState } from 'react'
import { getArtists } from '../api/artists'
import type { Artist } from '../types/music'

function ArtistsPage() {
  // Stores the artists returned by the backend.
  const [artists, setArtists] = useState<Artist[]>([])

  // Tracks whether the request is still loading.
  const [isLoading, setIsLoading] = useState(true)

  // Stores an error message if the request fails.
  const [error, setError] = useState<string | null>(null)

  // Fetches artists when the page first loads.
  useEffect(() => {
    async function fetchArtists() {
      try {
        // call endpoint from fastapi
        const data = await getArtists()
        // save artists in react state
        setArtists(data)
      } catch {
        setError('Unable to load artists. Please try again later.')
      } finally {
        // end the loading state
        setIsLoading(false)
      }
    }

    fetchArtists()
  }, [])

  return (
    <>
      <header className="page-header">
        <span className="page-eyebrow">YOUR LIBRARY</span>
        <h1>Artists</h1>
        <p className="page-description">
          Explore and manage the artists in your music library.
        </p>
      </header>

      <section className="artists-section">
        <div className="artists-section-header">
          <h2>Your Artists</h2>
          <span className="artists-count">
            {artists.length} {artists.length === 1 ? 'artist' : 'artists'}
          </span>
        </div>

        {isLoading ? (
          <div className="dashboard-empty-state">
            <p>Loading artists...</p>
          </div>
        ) : error ? (
          <div className="dashboard-empty-state">
            <p>{error}</p>
          </div>
        ) : artists.length === 0 ? (
          <div className="dashboard-empty-state">
            <span className="empty-state-icon">♫</span>
            <h3>No artists yet</h3>
            <p>
              Artists you add to your library will appear here.
            </p>
          </div>
        ) : (
          <div className="artists-list">
            {artists.map((artist) => (
              <div className="stat-card" key={artist.id}>
                <h3>{artist.name}</h3>
              </div>
            ))}
          </div>
        )}
      </section>
    </>
  )
}

export default ArtistsPage
