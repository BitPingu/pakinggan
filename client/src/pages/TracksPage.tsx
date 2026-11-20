import { useEffect, useState } from 'react'
import type { SubmitEvent } from 'react'
import { createTrack, deleteTrack, getTracks, updateTrack } from '../api/tracks'
import { getAlbums } from '../api/albums'
import { getArtists } from '../api/artists'
import type { Album, Artist, Track } from '../types/music'
import PageHeader from '../components/PageHeader/PageHeader'
import EmptyState from '../components/EmptyState/EmptyState'
import LibrarySectionHeader from '../components/LibrarySectionHeader/LibrarySectionHeader'
import { Music2, Pencil, Plus, Save, Trash2, X } from 'lucide-react'

// Displays and manages the tracks in the user's music library.
function TracksPage() {
  const [tracks, setTracks] = useState<Track[]>([])
  const [albums, setAlbums] = useState<Album[]>([])
  const [artists, setArtists] = useState<Artist[]>([])

  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [trackTitle, setTrackTitle] = useState('')
  const [trackDuration, setTrackDuration] = useState('')
  const [selectedAlbumId, setSelectedAlbumId] = useState('')
  const [isCreating, setIsCreating] = useState(false)
  const [createError, setCreateError] = useState<string | null>(null)

  const [editingTrackId, setEditingTrackId] = useState<number | null>(null)
  const [editedTrackTitle, setEditedTrackTitle] = useState('')
  const [editedTrackDuration, setEditedTrackDuration] = useState('')
  const [editedAlbumId, setEditedAlbumId] = useState('')
  const [isUpdating, setIsUpdating] = useState(false)
  const [editError, setEditError] = useState<string | null>(null)

  const [deletingTrackId, setDeletingTrackId] = useState<number | null>(null)
  const [deleteError, setDeleteError] = useState<string | null>(null)

  // Fetches tracks, albums, and artists when the page first loads.
  useEffect(() => {
    async function fetchLibrary() {
      try {
        const [trackData, albumData, artistData] = await Promise.all([
          getTracks(),
          getAlbums(),
          getArtists(),
        ])

        setTracks(trackData)
        setAlbums(albumData)
        setArtists(artistData)
      } catch {
        setError('Unable to load tracks. Please try again later.')
      } finally {
        setIsLoading(false)
      }
    }

    fetchLibrary()
  }, [])

  // Creates a new track through the backend.
  async function handleCreateTrack(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault()

    const trimmedTitle = trackTitle.trim()

    if (!trimmedTitle || !selectedAlbumId) return

    const duration = trackDuration.trim() ? Number(trackDuration) : null

    if (duration !== null && (!Number.isInteger(duration) || duration < 0)) {
      setCreateError('Duration must be a non-negative whole number.')
      return
    }

    setIsCreating(true)
    setCreateError(null)

    try {
      const newTrack = await createTrack(
        trimmedTitle,
        duration,
        Number(selectedAlbumId),
      )

      setTracks((currentTracks) => [...currentTracks, newTrack])
      setTrackTitle('')
      setTrackDuration('')
      setSelectedAlbumId('')
    } catch {
      setCreateError('Unable to create track. Please try again.')
    } finally {
      setIsCreating(false)
    }
  }

  // Starts editing a track.
  function handleEditClick(track: Track) {
    setEditingTrackId(track.id)
    setEditedTrackTitle(track.title)
    setEditedTrackDuration(
      track.duration === null ? '' : String(track.duration),
    )
    setEditedAlbumId(String(track.album_id))
    setEditError(null)
  }

  // Cancels editing and clears the edit form.
  function handleCancelEdit() {
    setEditingTrackId(null)
    setEditedTrackTitle('')
    setEditedTrackDuration('')
    setEditedAlbumId('')
    setEditError(null)
  }

  // Saves the updated track through the backend.
  async function handleUpdateTrack(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault()

    const trimmedTitle = editedTrackTitle.trim()

    if (!trimmedTitle || !editedAlbumId || editingTrackId === null) return

    const duration = editedTrackDuration.trim()
      ? Number(editedTrackDuration)
      : null

    if (duration !== null && (!Number.isInteger(duration) || duration < 0)) {
      setEditError('Duration must be a non-negative whole number.')
      return
    }

    setIsUpdating(true)
    setEditError(null)

    try {
      const updatedTrack = await updateTrack(
        editingTrackId,
        trimmedTitle,
        duration,
        Number(editedAlbumId),
      )

      setTracks((currentTracks) =>
        currentTracks.map((track) =>
          track.id === updatedTrack.id ? updatedTrack : track,
        ),
      )

      handleCancelEdit()
    } catch {
      setEditError('Unable to update track. Please try again.')
    } finally {
      setIsUpdating(false)
    }
  }

  // Deletes a track through the backend.
  async function handleDeleteTrack(track: Track) {
    const confirmed = window.confirm(
      `Are you sure you want to delete ${track.title}?`,
    )

    if (!confirmed) return

    setDeletingTrackId(track.id)
    setDeleteError(null)

    try {
      await deleteTrack(track.id)

      setTracks((currentTracks) =>
        currentTracks.filter((currentTrack) => currentTrack.id !== track.id),
      )
    } catch {
      setDeleteError('Unable to delete track. Please try again.')
    } finally {
      setDeletingTrackId(null)
    }
  }

  // Formats a track duration as minutes and seconds.
  function formatDuration(duration: number | null) {
    if (duration === null) return 'Unknown duration'

    const minutes = Math.floor(duration / 60)
    const seconds = String(duration % 60).padStart(2, '0')

    return `${minutes}:${seconds}`
  }

  return (
    <>
      <PageHeader
        eyebrow="YOUR LIBRARY"
        title="Tracks"
        description="Explore and manage the tracks in your music library."
      />

      <section className="library-section">
        <LibrarySectionHeader
          title="Your Tracks"
          count={
            isLoading
              ? '…'
              : error
                ? '—'
                : `${tracks.length} ${tracks.length === 1 ? 'track' : 'tracks'}`
          }
        />

        <form onSubmit={handleCreateTrack} className="library-form">
          <div className="library-form-controls">
            <input
              type="text"
              placeholder="Enter track title..."
              value={trackTitle}
              onChange={(event) => setTrackTitle(event.target.value)}
              disabled={isCreating}
            />

            <input
              type="number"
              min="0"
              step="1"
              placeholder="Duration (seconds, optional)"
              value={trackDuration}
              onChange={(event) => setTrackDuration(event.target.value)}
              disabled={isCreating}
            />

            <select
              value={selectedAlbumId}
              onChange={(event) => setSelectedAlbumId(event.target.value)}
              disabled={isCreating || albums.length === 0}
            >
              <option value="">Select an album...</option>
              {albums.map((album) => (
                <option key={album.id} value={album.id}>
                  {album.title}
                </option>
              ))}
            </select>

            <button
              type="submit"
              disabled={
                isCreating ||
                isUpdating ||
                deletingTrackId !== null ||
                !trackTitle.trim() ||
                !selectedAlbumId ||
                (trackDuration.trim() !== '' &&
                  (!Number.isInteger(Number(trackDuration)) ||
                    Number(trackDuration) < 0))
              }
            >
              <Plus size={16} strokeWidth={1.8} aria-hidden="true" />
              {isCreating ? 'Adding…' : 'Add Track'}
            </button>
          </div>

          {trackTitle.length > 0 && !trackTitle.trim() && (
            <p className="form-error">Track title cannot be empty.</p>
          )}
        </form>

        {createError && <p className="form-error">{createError}</p>}

        {deleteError && <p className="form-error">{deleteError}</p>}

        {isLoading ? (
          <EmptyState message="Loading tracks…" />
        ) : error ? (
          <EmptyState message={error} />
        ) : tracks.length === 0 ? (
          <EmptyState
            icon={Music2}
            title="No tracks yet"
            description="Tracks you add to your library will appear here."
          />
        ) : (
          <div className="library-list">
            {tracks.map((track) => {
              const album = albums.find(
                (currentAlbum) => currentAlbum.id === track.album_id,
              )

              const artist = artists.find(
                (currentArtist) => currentArtist.id === album?.artist_id,
              )

              return (
                <div
                  className={`stat-card ${editingTrackId === track.id ? 'editing' : ''}`}
                  key={track.id}
                >
                  {editingTrackId === track.id ? (
                    <form
                      onSubmit={handleUpdateTrack}
                      className="library-edit-form"
                    >
                      <input
                        type="text"
                        value={editedTrackTitle}
                        onChange={(event) =>
                          setEditedTrackTitle(event.target.value)
                        }
                        disabled={isUpdating}
                      />

                      <input
                        type="number"
                        min="0"
                        step="1"
                        placeholder="Duration (seconds, optional)"
                        value={editedTrackDuration}
                        onChange={(event) =>
                          setEditedTrackDuration(event.target.value)
                        }
                        disabled={isUpdating}
                      />

                      <select
                        value={editedAlbumId}
                        onChange={(event) =>
                          setEditedAlbumId(event.target.value)
                        }
                        disabled={isUpdating}
                      >
                        {albums.map((currentAlbum) => (
                          <option key={currentAlbum.id} value={currentAlbum.id}>
                            {currentAlbum.title}
                          </option>
                        ))}
                      </select>

                      <div className="library-edit-form-actions">
                        <button
                          type="submit"
                          className="save-button"
                          disabled={
                            isUpdating ||
                            !editedTrackTitle.trim() ||
                            !editedAlbumId ||
                            (editedTrackDuration.trim() !== '' &&
                              (!Number.isInteger(Number(editedTrackDuration)) ||
                                Number(editedTrackDuration) < 0))
                          }
                        >
                          <Save
                            size={16}
                            strokeWidth={1.8}
                            aria-hidden="true"
                          />
                          {isUpdating ? 'Saving…' : 'Save'}
                        </button>

                        <button
                          type="button"
                          className="cancel-button"
                          onClick={handleCancelEdit}
                          disabled={isUpdating}
                        >
                          <X size={16} strokeWidth={1.8} aria-hidden="true" />
                          Cancel
                        </button>
                      </div>

                      {editError && <p className="form-error">{editError}</p>}
                    </form>
                  ) : (
                    <>
                      <h3>{track.title}</h3>
                      <span className="album-card-artist">
                        {album?.title ?? 'Unknown album'}
                        {artist ? ` · ${artist.name}` : ''}
                        {' · '}
                        {formatDuration(track.duration)}
                      </span>

                      <div className="library-card-actions">
                        <button
                          type="button"
                          className="edit-button"
                          onClick={() => handleEditClick(track)}
                          disabled={editingTrackId !== null}
                        >
                          <Pencil
                            size={16}
                            strokeWidth={1.8}
                            aria-hidden="true"
                          />
                          Edit
                        </button>

                        <button
                          type="button"
                          className="delete-button"
                          onClick={() => handleDeleteTrack(track)}
                          disabled={deletingTrackId !== null || isUpdating}
                        >
                          <Trash2
                            size={16}
                            strokeWidth={1.8}
                            aria-hidden="true"
                          />
                          {deletingTrackId === track.id
                            ? 'Deleting…'
                            : 'Delete'}
                        </button>
                      </div>
                    </>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </section>
    </>
  )
}

export default TracksPage
