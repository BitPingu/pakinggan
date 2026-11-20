import { useState } from 'react'
import type { SubmitEvent } from 'react'
import { useLibrary } from '../hooks/useLibrary'
import type { Album } from '../types/music'
import PageHeader from '../components/PageHeader/PageHeader'
import EmptyState from '../components/EmptyState/EmptyState'
import LibrarySectionHeader from '../components/LibrarySectionHeader/LibrarySectionHeader'
import { Disc3, Pencil, Plus, Save, Trash2, X } from 'lucide-react'

// Displays and manages the albums in the user's music library.
function AlbumsPage() {
  const {
    albums,
    artists,
    isLoading,
    error,
    addAlbum,
    editAlbum,
    removeAlbum,
  } = useLibrary()

  // Stores the album title entered when creating a new album.
  const [albumTitle, setAlbumTitle] = useState('')

  // Stores the artist selected for the new album.
  const [selectedArtistId, setSelectedArtistId] = useState('')

  // Tracks whether an album is currently being created.
  const [isCreating, setIsCreating] = useState(false)

  // Stores any error that occurs while creating an album.
  const [createError, setCreateError] = useState<string | null>(null)

  // Tracks which album is currently being edited.
  const [editingAlbumId, setEditingAlbumId] = useState<number | null>(null)

  // Stores the album title entered in the edit form.
  const [editedAlbumTitle, setEditedAlbumTitle] = useState('')

  // Stores the artist selected in the edit form.
  const [editedArtistId, setEditedArtistId] = useState('')

  // Tracks whether an album update is in progress.
  const [isUpdating, setIsUpdating] = useState(false)

  // Stores any error that occurs while updating an album.
  const [editError, setEditError] = useState<string | null>(null)

  // Tracks which album is currently being deleted.
  const [deletingAlbumId, setDeletingAlbumId] = useState<number | null>(null)

  // Stores any error that occurs while deleting an album.
  const [deleteError, setDeleteError] = useState<string | null>(null)

  // Creates a new album through the backend.
  async function handleCreateAlbum(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault()

    // Remove leading and trailing whitespace.
    const trimmedTitle = albumTitle.trim()

    // Prevent submission if the title or artist selection is invalid.
    if (!trimmedTitle || !selectedArtistId) return

    setIsCreating(true)
    setCreateError(null)

    try {
      // Add the new album to the shared collection.
      await addAlbum(trimmedTitle, Number(selectedArtistId))

      // Clear the form after successful creation.
      setAlbumTitle('')
      setSelectedArtistId('')
    } catch {
      setCreateError('Unable to create album. Please try again.')
    } finally {
      setIsCreating(false)
    }
  }

  // Starts editing an album.
  function handleEditClick(album: Album) {
    setEditingAlbumId(album.id)
    setEditedAlbumTitle(album.title)
    setEditedArtistId(String(album.artist_id))
    setEditError(null)
  }

  // Cancels editing and clears the edit form.
  function handleCancelEdit() {
    setEditingAlbumId(null)
    setEditedAlbumTitle('')
    setEditedArtistId('')
    setEditError(null)
  }

  // Saves the updated album through the backend.
  async function handleUpdateAlbum(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault()

    // Remove leading and trailing whitespace.
    const trimmedTitle = editedAlbumTitle.trim()

    // Prevent submission if the title, artist selection, or album ID is invalid.
    if (!trimmedTitle || !editedArtistId || editingAlbumId === null) return

    setIsUpdating(true)
    setEditError(null)

    try {
      // Update the album in the shared collection.
      await editAlbum(editingAlbumId, trimmedTitle, Number(editedArtistId))

      // Exit edit mode after a successful update.
      handleCancelEdit()
    } catch {
      setEditError('Unable to update album. Please try again.')
    } finally {
      setIsUpdating(false)
    }
  }

  // Deletes an album through the backend.
  async function handleDeleteAlbum(album: Album) {
    // Ask the user to confirm before deleting.
    const confirmed = window.confirm(
      `Are you sure you want to delete ${album.title}?`,
    )

    if (!confirmed) return

    setDeletingAlbumId(album.id)
    setDeleteError(null)

    try {
      // Remove the album from the shared collection.
      await removeAlbum(album.id)
    } catch (error) {
      setDeleteError(
        error instanceof Error
          ? error.message
          : 'Unable to delete album. Please try again.',
      )
    } finally {
      setDeletingAlbumId(null)
    }
  }

  return (
    <>
      {/* Page heading */}
      <PageHeader
        eyebrow="YOUR LIBRARY"
        title="Albums"
        description="Explore and manage the albums in your music library."
      />

      <section className="library-section">
        <LibrarySectionHeader
          title="Your Albums"
          count={
            isLoading
              ? '…'
              : error
                ? '—'
                : `${albums.length} ${albums.length === 1 ? 'album' : 'albums'}`
          }
        />

        {/* Form for creating a new album */}
        <form onSubmit={handleCreateAlbum} className="library-form">
          <div className="library-form-controls">
            <input
              type="text"
              placeholder="Enter album title..."
              value={albumTitle}
              onChange={(event) => setAlbumTitle(event.target.value)}
              disabled={isCreating}
            />

            <select
              value={selectedArtistId}
              onChange={(event) => setSelectedArtistId(event.target.value)}
              disabled={isCreating || artists.length === 0}
            >
              <option value="">Select an artist...</option>
              {artists.map((artist) => (
                <option key={artist.id} value={artist.id}>
                  {artist.name}
                </option>
              ))}
            </select>

            <button
              type="submit"
              disabled={
                isCreating ||
                isUpdating ||
                deletingAlbumId !== null ||
                !albumTitle.trim() ||
                !selectedArtistId
              }
            >
              <Plus size={16} strokeWidth={1.8} aria-hidden="true" />
              {isCreating ? 'Adding…' : 'Add Album'}
            </button>
          </div>

          {/* Display validation feedback for whitespace-only input */}
          {albumTitle.length > 0 && !albumTitle.trim() && (
            <p className="form-error">Album title cannot be empty.</p>
          )}
        </form>

        {/* Display an error if album creation fails */}
        {createError && <p className="form-error">{createError}</p>}

        {/* Display an error if album deletion fails */}
        {deleteError && <p className="form-error">{deleteError}</p>}

        {/* Loading, error, empty, and populated states */}
        {isLoading ? (
          <EmptyState message="Loading albums…" />
        ) : error ? (
          <EmptyState message={error} />
        ) : albums.length === 0 ? (
          <EmptyState
            icon={Disc3}
            title="No albums yet"
            description="Albums you add to your library will appear here."
          />
        ) : (
          // Display the album cards.
          <div className="library-list">
            {albums.map((album) => {
              // Find the artist associated with the current album.
              const artist = artists.find(
                (currentArtist) => currentArtist.id === album.artist_id,
              )

              return (
                <div
                  className={`stat-card ${editingAlbumId === album.id ? 'editing' : ''}`}
                  key={album.id}
                >
                  {/* Show the edit form for the selected album */}
                  {editingAlbumId === album.id ? (
                    <form
                      onSubmit={handleUpdateAlbum}
                      className="library-edit-form"
                    >
                      <input
                        type="text"
                        value={editedAlbumTitle}
                        onChange={(event) =>
                          setEditedAlbumTitle(event.target.value)
                        }
                        disabled={isUpdating}
                      />

                      <select
                        value={editedArtistId}
                        onChange={(event) =>
                          setEditedArtistId(event.target.value)
                        }
                        disabled={isUpdating}
                      >
                        {artists.map((currentArtist) => (
                          <option
                            key={currentArtist.id}
                            value={currentArtist.id}
                          >
                            {currentArtist.name}
                          </option>
                        ))}
                      </select>

                      <div className="library-edit-form-actions">
                        <button
                          type="submit"
                          className="save-button"
                          disabled={
                            isUpdating ||
                            !editedAlbumTitle.trim() ||
                            !editedArtistId
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

                      {/* Display an error if the update fails */}
                      {editError && <p className="form-error">{editError}</p>}
                    </form>
                  ) : (
                    <>
                      {/* Display the album title and artist */}
                      <h3>{album.title}</h3>
                      <span className="album-card-artist">
                        {artist?.name ?? 'Unknown artist'}
                      </span>

                      {/* Group the album management buttons */}
                      <div className="library-card-actions">
                        <button
                          type="button"
                          className="edit-button"
                          onClick={() => handleEditClick(album)}
                          disabled={editingAlbumId !== null}
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
                          onClick={() => handleDeleteAlbum(album)}
                          disabled={deletingAlbumId !== null || isUpdating}
                        >
                          <Trash2
                            size={16}
                            strokeWidth={1.8}
                            aria-hidden="true"
                          />
                          {deletingAlbumId === album.id
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

export default AlbumsPage
