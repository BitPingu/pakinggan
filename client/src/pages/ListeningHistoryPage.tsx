import { useEffect, useState } from 'react'
import { History } from 'lucide-react'
import PageHeader from '../components/PageHeader/PageHeader'
import EmptyState from '../components/EmptyState/EmptyState'
import { getListeningHistory } from '../api/listening-history'
import type { ListeningHistoryEntry } from '../types/listening-history'

const PAGE_SIZE = 20

// Formats a timestamp into a readable date and time.
function formatPlayedAt(timestamp: string) {
  return new Date(timestamp).toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

// Formats a track duration as minutes and seconds.
function formatDuration(duration: number | null) {
  if (duration === null) return null

  const minutes = Math.floor(duration / 60)
  const seconds = String(duration % 60).padStart(2, '0')

  return `${minutes}:${seconds}`
}

// Displays the user's listening history.
function ListeningHistoryPage() {
  const [history, setHistory] = useState<ListeningHistoryEntry[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isLoadingMore, setIsLoadingMore] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [loadMoreError, setLoadMoreError] = useState<string | null>(null)
  const [hasMore, setHasMore] = useState(true)

  // Fetches the initial listening history.
  useEffect(() => {
    async function fetchHistory() {
      try {
        const entries = await getListeningHistory(PAGE_SIZE)

        setHistory(entries)
        setHasMore(entries.length === PAGE_SIZE)
      } catch {
        setError('Unable to load listening history. Please try again.')
      } finally {
        setIsLoading(false)
      }
    }

    fetchHistory()
  }, [])

  // Fetches the next page of listening history.
  async function handleLoadMore() {
    setIsLoadingMore(true)
    setLoadMoreError(null)

    try {
      const entries = await getListeningHistory(PAGE_SIZE, history.length)

      setHistory((currentHistory) => [...currentHistory, ...entries])
      setHasMore(entries.length === PAGE_SIZE)
    } catch {
      setLoadMoreError('Unable to load more history. Please try again.')
    } finally {
      setIsLoadingMore(false)
    }
  }

  return (
    <>
      <PageHeader
        eyebrow="YOUR LISTENING"
        title="Listening History"
        description="Look back on the music you've been listening to."
      />

      <section className="library-section">
        {isLoading ? (
          <EmptyState message="Loading listening history…" />
        ) : error ? (
          <EmptyState message={error} />
        ) : history.length === 0 ? (
          <EmptyState
            icon={History}
            title="No listening history yet"
            description="Your recently played tracks will appear here once you start listening."
          />
        ) : (
          <div>
            {/* Displays the user's listening history entries. */}
            <div className="history-list">
              {history.map((entry) => {
                const duration = formatDuration(entry.track.duration)

                return (
                  <div className="history-entry" key={entry.id}>
                    {/* Displays the track information. */}
                    <div className="history-entry-info">
                      <h3>{entry.track.title}</h3>

                      <p>
                        {entry.track.artist.name}
                        {entry.track.album && ` · ${entry.track.album.title}`}
                        {duration && ` · ${duration}`}
                      </p>
                    </div>

                    {/* Displays when the track was played. */}
                    <span className="history-entry-date">
                      {formatPlayedAt(entry.played_at)}
                    </span>
                  </div>
                )
              })}
            </div>

            {loadMoreError && <p className="form-error">{loadMoreError}</p>}

            {hasMore && (
              <button
                type="button"
                onClick={handleLoadMore}
                disabled={isLoadingMore}
              >
                {isLoadingMore ? 'Loading…' : 'Load More'}
              </button>
            )}
          </div>
        )}
      </section>
    </>
  )
}

export default ListeningHistoryPage
