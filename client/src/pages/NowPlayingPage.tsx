import { useEffect, useState } from 'react'
import { getNowPlaying } from '../api/lastfm'
import type { LastFMTrack } from '../types/lastfm'
import PageHeader from '../components/PageHeader/PageHeader'
import '../styles/now-playing.css'

// Displays the immersive Now Playing experience.
function NowPlayingPage() {
  const [nowPlaying, setNowPlaying] = useState<LastFMTrack | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [hasError, setHasError] = useState(false)

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
          <div className="listening-track">
            <div className="listening-artwork-container">
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
        </section>
      )}
    </>
  )
}

export default NowPlayingPage
