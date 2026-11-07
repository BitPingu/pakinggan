import { useEffect, useState } from 'react'
import type { SubmitEvent } from 'react'
import {
  createArtist,
  getArtists,
  updateArtist,
} from '../api/artists'
import type { Artist } from '../types/music'

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

  // Fetches the artist list when the page first loads.
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
      const updatedArtist = await updateArtist(
        editingArtistId,
        trimmedName,
      )

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

  return (
    <>
      {/* Page heading */}
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

        {/* Form for creating a new artist */}
        <form onSubmit={handleCreateArtist} className="artist-form">
          <div className="artist-form-controls">
            <input
              type="text"
              placeholder="Enter artist name..."
              value={artistName}
              onChange={(event) => setArtistName(event.target.value)}
              disabled={isCreating}
            />

            <button
              type="submit"
              disabled={isCreating || !artistName.trim()}
            >
              {isCreating ? 'Adding...' : 'Add Artist'}
            </button>
          </div>

          {/* Display validation feedback for whitespace-only input */}
          {artistName.length > 0 && !artistName.trim() && (
            <p className="form-error">
              Artist name cannot be empty.
            </p>
          )}
        </form>

        {/* Display an error if artist creation fails */}
        {createError && <p className="form-error">{createError}</p>}

        {/* Loading, error, empty, and populated states */}
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
          // Display the artist cards
          <div className="artists-list">
            {artists.map((artist) => (
              <div
                className={`stat-card ${editingArtistId === artist.id ? 'editing' : ''}`}
                key={artist.id}
              >
                {/* Show the edit form for the selected artist */}
                {editingArtistId === artist.id ? (
                  <form onSubmit={handleUpdateArtist} className="artist-edit-form">
                    <input
                      type="text"
                      value={editedArtistName}
                      onChange={(event) => setEditedArtistName(event.target.value)}
                      disabled={isUpdating}
                    />

                    <div className="artist-edit-form-actions">
                      <button
                        type="submit"
                        className="save-button"
                        disabled={isUpdating || !editedArtistName.trim()}
                      >
                        {isUpdating ? 'Saving...' : 'Save'}
                      </button>

                      <button
                        type="button"
                        className="cancel-button"
                        onClick={handleCancelEdit}
                        disabled={isUpdating}
                      >
                        Cancel
                      </button>
                    </div>

                    {/* Display an error if the update fails */}
                    {editError && <p className="form-error">{editError}</p>}
                  </form>
                ) : (
                  // Show the artist name and edit button
                  <>
                    <h3>{artist.name}</h3>
                    <button
                      type="button"
                      className="edit-button"
                      onClick={() => handleEditClick(artist)}
                    >
                      Edit
                    </button>
                  </>
                )}
              </div>
            ))}
          </div>
        )}
      </section>
    </>
  )
}

export default ArtistsPage
