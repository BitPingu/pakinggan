import { useEffect, useState } from 'react'
import { History } from 'lucide-react'
import PageHeader from '../components/PageHeader/PageHeader'
import EmptyState from '../components/EmptyState/EmptyState'
import {
  getListeningHistory,
  syncListeningHistory,
} from '../api/listening-history'
import { getLastFMStatus } from '../api/lastfm'
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
  // Stores the user's listening history entries.
  const [history, setHistory] = useState<ListeningHistoryEntry[]>([])

  // Tracks whether the initial listening history is loading.
  const [isLoading, setIsLoading] = useState(true)

  // Tracks whether additional listening history is loading.
  const [isLoadingMore, setIsLoadingMore] = useState(false)

  // Stores an error from fetching the initial listening history.
  const [error, setError] = useState<string | null>(null)

  // Stores an error from fetching additional listening history.
  const [loadMoreError, setLoadMoreError] = useState<string | null>(null)

  // Tracks whether more listening history entries are available.
  const [hasMore, setHasMore] = useState(true)

  // Tracks the next Last.fm page to import.
  const [nextLastFMPage, setNextLastFMPage] = useState(2)

  // Tracks whether the user has connected their Last.fm account.
  const [isLastFMConnected, setIsLastFMConnected] = useState(false)

  // Tracks whether listening history is currently syncing.
  const [isSyncing, setIsSyncing] = useState(false)

  // Stores the result of a successful listening-history sync.
  const [syncMessage, setSyncMessage] = useState<string | null>(null)

  // Stores an error from a failed listening-history sync.
  const [syncError, setSyncError] = useState<string | null>(null)

  // Stores an error from refreshing history after a successful sync.
  const [refreshError, setRefreshError] = useState<string | null>(null)

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
      // Imports the next page of listening history from Last.fm.
      if (isLastFMConnected) {
        await syncListeningHistory(nextLastFMPage)
        setNextLastFMPage((currentPage) => currentPage + 1)
      }

      // Fetches the newly imported listening history entries.
      const entries = await getListeningHistory(PAGE_SIZE, history.length)

      setHistory((currentHistory) => [...currentHistory, ...entries])
      setHasMore(entries.length === PAGE_SIZE)
    } catch {
      setLoadMoreError('Unable to load more history. Please try again.')
    } finally {
      setIsLoadingMore(false)
    }
  }

  // Syncs the user's listening history with Last.fm.
  async function handleSync() {
    setIsSyncing(true)
    setSyncMessage(null)
    setSyncError(null)
    setRefreshError(null)

    try {
      const result = await syncListeningHistory()
      setNextLastFMPage(2)

      setSyncMessage(
        result.imported === 0
          ? 'Your listening history is already up to date.'
          : `Successfully imported ${result.imported} ${
              result.imported === 1 ? 'track' : 'tracks'
            }.`,
      )

      // Refreshes the listening history after syncing.
      try {
        const entries = await getListeningHistory(PAGE_SIZE)

        setHistory(entries)
        setHasMore(entries.length === PAGE_SIZE)
      } catch {
        setRefreshError(
          'History was synced, but the displayed entries could not be refreshed.',
        )
      }
    } catch {
      setSyncError('Unable to sync listening history. Please try again.')
    } finally {
      setIsSyncing(false)
    }
  }

  // Fetches the user's Last.fm connection status.
  useEffect(() => {
    async function fetchLastFMStatus() {
      try {
        const status = await getLastFMStatus()
        setIsLastFMConnected(status.connected)
      } catch {
        setIsLastFMConnected(false)
      }
    }

    fetchLastFMStatus()
  }, [])

  return (
    <>
      <div className="history-header">
        <div className="history-header-top">
          <PageHeader
            eyebrow="YOUR LISTENING"
            title="Listening History"
            description="Look back on the music you've been listening to."
          />
          {isLastFMConnected && (
            <button
              type="button"
              className="sync-button"
              onClick={handleSync}
              disabled={isSyncing || isLoadingMore}
            >
              {isSyncing ? 'Syncing…' : 'Sync with Last.fm'}
            </button>
          )}
        </div>

        {syncMessage && <p className="form-success">{syncMessage}</p>}
        {syncError && <p className="form-error">{syncError}</p>}
        {refreshError && <p className="form-error">{refreshError}</p>}
      </div>

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
                className="load-more-button"
                onClick={handleLoadMore}
                disabled={isLoadingMore || isSyncing}
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
