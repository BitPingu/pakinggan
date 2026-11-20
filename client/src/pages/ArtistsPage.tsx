import { useEffect, useState } from 'react'
import type { SubmitEvent } from 'react'
import {
  createArtist,
  deleteArtist,
  getArtists,
  updateArtist,
} from '../api/artists'
import type { Artist } from '../types/music'
import PageHeader from '../components/PageHeader/PageHeader'
import EmptyState from '../components/EmptyState/EmptyState'
import LibrarySectionHeader from '../components/LibrarySectionHeader/LibrarySectionHeader'
import { Pencil, Plus, Save, Trash2, Users, X } from 'lucide-react'

// Displays and manages the artists in the user's music library.
function ArtistsPage() {
  // Stores the artists returned by the backend.
  const [artists, setArtists] = useState<Artist[]>([])

  // Tracks whether the initial artist list is loading.
  const [isLoading, setIsLoading] = useState(true)

  // Stores any error that occurs while fetching artists.
  const [error, setError] = useState<string | null>(null)

  // Stores the name entered when creating a new artist.
  const [artistName, setArtistName] = useState('')

  // Tracks whether an artist is currently being created.
  const [isCreating, setIsCreating] = useState(false)

  // Stores any error that occurs while creating an artist.
  const [createError, setCreateError] = useState<string | null>(null)

  // Tracks which artist is currently being edited.
  const [editingArtistId, setEditingArtistId] = useState<number | null>(null)

  // Stores the artist name entered in the edit form.
  const [editedArtistName, setEditedArtistName] = useState('')

  // Tracks whether an artist update is in progress.
  const [isUpdating, setIsUpdating] = useState(false)

  // Stores any error that occurs while updating an artist.
  const [editError, setEditError] = useState<string | null>(null)

  // Tracks which artist is currently being deleted.
  const [deletingArtistId, setDeletingArtistId] = useState<number | null>(null)

  // Stores any error that occurs while deleting an artist.
  const [deleteError, setDeleteError] = useState<string | null>(null)

  // Fetches the artist list when the page first loads.
  useEffect(() => {
    async function fetchArtists() {
      try {
        // Retrieve artists from the backend.
        const data = await getArtists()

        // Update the artist list.
        setArtists(data)
      } catch {
        setError('Unable to load artists. Please try again later.')
      } finally {
        // Stop displaying the loading state.
        setIsLoading(false)
      }
    }

    fetchArtists()
  }, [])

  // Creates a new artist through the backend.
  async function handleCreateArtist(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault()

    // Remove leading and trailing whitespace.
    const trimmedName = artistName.trim()

    // Prevent submission if the name is empty.
    if (!trimmedName) return

    setIsCreating(true)
    setCreateError(null)

    try {
      // Send the new artist name to the backend.
      const newArtist = await createArtist(trimmedName)

      // Add the newly created artist to the existing list.
      setArtists((currentArtists) => [...currentArtists, newArtist])

      // Clear the input after successful creation.
      setArtistName('')
    } catch {
      setCreateError('Unable to create artist. Please try again.')
    } finally {
      setIsCreating(false)
    }
  }

  // Starts editing an artist.
  function handleEditClick(artist: Artist) {
    setEditingArtistId(artist.id)
    setEditedArtistName(artist.name)
    setEditError(null)
  }

  // Cancels editing and clears the edit form.
  function handleCancelEdit() {
    setEditingArtistId(null)
    setEditedArtistName('')
    setEditError(null)
  }

  // Saves the updated artist through the backend.
  async function handleUpdateArtist(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault()

    // Remove leading and trailing whitespace.
    const trimmedName = editedArtistName.trim()

    // Prevent submission if the name or artist ID is invalid.
    if (!trimmedName || editingArtistId === null) return

    setIsUpdating(true)
    setEditError(null)

    try {
      // Send the updated name to the backend.
      const updatedArtist = await updateArtist(editingArtistId, trimmedName)

      // Replace the old artist with the updated artist in the list.
      setArtists((currentArtists) =>
        currentArtists.map((artist) =>
          artist.id === updatedArtist.id ? updatedArtist : artist,
        ),
      )

      // Exit edit mode after a successful update.
      handleCancelEdit()
    } catch {
      setEditError('Unable to update artist. Please try again.')
    } finally {
      setIsUpdating(false)
    }
  }

  // Deletes an artist through the backend.
  async function handleDeleteArtist(artist: Artist) {
    // Ask the user to confirm before deleting.
    const confirmed = window.confirm(
      `Are you sure you want to delete ${artist.name}?`,
    )

    if (!confirmed) return

    setDeletingArtistId(artist.id)
    setDeleteError(null)

    try {
      // Send the delete request to the backend.
      await deleteArtist(artist.id)

      // Remove the deleted artist from the frontend list.
      setArtists((currentArtists) =>
        currentArtists.filter(
          (currentArtist) => currentArtist.id !== artist.id,
        ),
      )
    } catch (error) {
      setDeleteError(
        error instanceof Error
          ? error.message
          : 'Unable to delete artist. Please try again.',
      )
    } finally {
      setDeletingArtistId(null)
    }
  }

  return (
    <>
      {/* Page heading */}
      <PageHeader
        eyebrow="YOUR LIBRARY"
        title="Artists"
        description="Explore and manage the artists in your music library."
      />

      <section className="library-section">
        <LibrarySectionHeader
          title="Your Artists"
          count={
            isLoading
              ? '…'
              : error
                ? '—'
                : `${artists.length} ${artists.length === 1 ? 'artist' : 'artists'}`
          }
        />

        {/* Form for creating a new artist */}
        <form onSubmit={handleCreateArtist} className="library-form">
          <div className="library-form-controls">
            <input
              type="text"
              placeholder="Enter artist name..."
              value={artistName}
              onChange={(event) => setArtistName(event.target.value)}
              disabled={isCreating}
            />

            <button type="submit" disabled={isCreating || !artistName.trim()}>
              <Plus size={16} strokeWidth={1.8} aria-hidden="true" />
              {isCreating ? 'Adding…' : 'Add Artist'}
            </button>
          </div>

          {/* Display validation feedback for whitespace-only input */}
          {artistName.length > 0 && !artistName.trim() && (
            <p className="form-error">Artist name cannot be empty.</p>
          )}
        </form>

        {/* Display an error if artist creation fails */}
        {createError && <p className="form-error">{createError}</p>}

        {/* Loading, error, empty, and populated states */}
        {isLoading ? (
          <EmptyState message="Loading artists…" />
        ) : error ? (
          <EmptyState message={error} />
        ) : (
          <>
            {/* Display an error if artist deletion fails */}
            {deleteError && <p className="form-error">{deleteError}</p>}

            {artists.length === 0 ? (
              <EmptyState
                icon={Users}
                title="No artists yet"
                description="Artists you add to your library will appear here."
              />
            ) : (
              // Display the artist cards
              <div className="library-list">
                {artists.map((artist) => (
                  <div
                    className={`stat-card ${editingArtistId === artist.id ? 'editing' : ''}`}
                    key={artist.id}
                  >
                    {/* Show the edit form for the selected artist */}
                    {editingArtistId === artist.id ? (
                      <form
                        onSubmit={handleUpdateArtist}
                        className="library-edit-form"
                      >
                        <input
                          type="text"
                          value={editedArtistName}
                          onChange={(event) =>
                            setEditedArtistName(event.target.value)
                          }
                          disabled={isUpdating}
                        />

                        <div className="library-edit-form-actions">
                          <button
                            type="submit"
                            className="save-button"
                            disabled={isUpdating || !editedArtistName.trim()}
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
                      // Show the artist name and edit button
                      <>
                        {/* Display the artist's name */}
                        <h3 className="artist-card-name">{artist.name}</h3>

                        {/* Group the artist management buttons */}
                        <div className="library-card-actions">
                          {/* Button to enter edit mode */}
                          <button
                            type="button"
                            className="edit-button"
                            onClick={() => handleEditClick(artist)}
                            disabled={editingArtistId !== null}
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
                            onClick={() => handleDeleteArtist(artist)}
                            disabled={deletingArtistId !== null || isUpdating}
                          >
                            <Trash2
                              size={16}
                              strokeWidth={1.8}
                              aria-hidden="true"
                            />
                            {deletingArtistId === artist.id
                              ? 'Deleting…'
                              : 'Delete'}
                          </button>
                        </div>
                      </>
                    )}
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </section>
    </>
  )
}

export default ArtistsPage
