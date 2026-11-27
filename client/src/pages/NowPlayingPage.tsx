import { useEffect, useState } from 'react'
import { getNowPlaying } from '../api/lastfm'
import type { LastFMTrack } from '../types/lastfm'
import { mockTrackMetadata } from '../data/mockTrackMetadata'
import { mockArtistMetadata } from '../data/mockArtistMetadata'
import PageHeader from '../components/PageHeader/PageHeader'
import '../styles/now-playing.css'

// Displays the immersive Now Playing experience.
function NowPlayingPage() {
  const [nowPlaying, setNowPlaying] = useState<LastFMTrack | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [hasError, setHasError] = useState(false)
  const trackKey = nowPlaying ? `${nowPlaying.artist}-${nowPlaying.name}` : ''

  // Fetches the currently playing track from Last.fm.
  useEffect(() => {
    let isMounted = true
    let isFetching = false

    async function fetchNowPlaying() {
      if (isFetching) return

      isFetching = true

      try {
        const result = await getNowPlaying()

        if (isMounted) {
          setNowPlaying(result.track?.nowplaying ? result.track : null)
          setHasError(false)
        }
      } catch {
        if (isMounted) {
          setHasError(true)
        }
      } finally {
        isFetching = false

        if (isMounted) {
          setIsLoading(false)
        }
      }
    }

    fetchNowPlaying()

    const interval = setInterval(fetchNowPlaying, 15000)

    return () => {
      isMounted = false
      clearInterval(interval)
    }
  }, [])

  return (
    <>
      {/* Now Playing page heading */}
      <PageHeader
        eyebrow="YOUR MUSIC"
        title="Now Playing"
        description="Discover more about the music you're listening to."
      />

      {/* Main listening experience */}
      <section className="listening-experience">
        {isLoading ? (
          <p>Loading current track...</p>
        ) : nowPlaying ? (
          <div className="listening-track" key={trackKey}>
            <div className="listening-artwork-container">
              {nowPlaying.image && (
                <img
                  src={nowPlaying.image}
                  alt=""
                  aria-hidden="true"
                  className="listening-artwork-glow"
                />
              )}
              {nowPlaying.image ? (
                <img
                  src={nowPlaying.image}
                  alt={`${nowPlaying.album ?? nowPlaying.name} album artwork`}
                  className="listening-artwork"
                />
              ) : (
                <div
                  className="listening-artwork"
                  role="img"
                  aria-label="Album artwork unavailable"
                />
              )}
            </div>

            <div className="listening-track-info">
              <span className="listening-status">
                <span className="now-playing-dot" />
                NOW PLAYING
              </span>

              <h2>{nowPlaying.name}</h2>
              <p className="listening-artist">{nowPlaying.artist}</p>

              {nowPlaying.album && (
                <p className="listening-album">{nowPlaying.album}</p>
              )}
            </div>
          </div>
        ) : (
          <div className="listening-empty-state">
            <p>
              {hasError
                ? 'Unable to retrieve your currently playing track.'
                : 'Nothing is playing right now.'}
            </p>
            <span>
              {hasError
                ? 'Please try again in a moment.'
                : 'Start listening on a connected music player and your track will appear here.'}
            </span>
          </div>
        )}
      </section>

      {/* Song information */}
      {nowPlaying && (
        <section className="now-playing-section">
          <h2>About This Track</h2>

          <div className="track-metadata">
            <div className="metadata-item">
              <span className="metadata-label">Genres</span>
              <div className="metadata-genres">
                {mockTrackMetadata.genres.map((genre) => (
                  <span className="metadata-genre" key={genre}>
                    {genre}
                  </span>
                ))}
              </div>
            </div>

            <div className="metadata-item">
              <span className="metadata-label">Release Date</span>
              <span className="metadata-value">
                {mockTrackMetadata.releaseDate
                  ? new Date(
                      `${mockTrackMetadata.releaseDate}T00:00:00`,
                    ).toLocaleDateString('en-CA', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                    })
                  : 'Unknown'}
              </span>
            </div>

            <div className="metadata-item">
              <span className="metadata-label">Duration</span>
              <span className="metadata-value">
                {mockTrackMetadata.duration !== null
                  ? `${Math.floor(mockTrackMetadata.duration / 60)}:${String(
                      mockTrackMetadata.duration % 60,
                    ).padStart(2, '0')}`
                  : 'Unknown'}
              </span>
            </div>
          </div>
          <div className="track-about">
            <h3>About</h3>
            <p>
              {mockTrackMetadata.description ?? 'No description available.'}
            </p>
          </div>
          <div className="artist-section">
            <h2>About the Artist</h2>

            <div className="artist-card">
              {mockArtistMetadata.image && (
                <img
                  src={mockArtistMetadata.image}
                  alt={`${nowPlaying.artist} portrait`}
                  className="artist-image"
                />
              )}

              <div className="artist-info">
                <h3>{nowPlaying.artist}</h3>

                <p>
                  {mockArtistMetadata.biography ??
                    'No artist biography available.'}
                </p>

                <div className="artist-genres">
                  {mockArtistMetadata.genres.map((genre) => (
                    <span className="metadata-genre" key={genre}>
                      {genre}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>
      )}
    </>
  )
}

export default NowPlayingPage
