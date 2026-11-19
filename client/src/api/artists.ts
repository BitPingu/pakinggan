import API_BASE_URL from './client'
import type { Artist } from '../types/music'

// Fetches all artists from the backend.
export async function getArtists(): Promise<Artist[]> {
  const response = await fetch(`${API_BASE_URL}/api/artists/`)

  if (!response.ok) {
    throw new Error('Failed to fetch artists')
  }

  return response.json()
}

// Creates a new artist through the backend.
export async function createArtist(name: string): Promise<Artist> {
  const response = await fetch(`${API_BASE_URL}/api/artists/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ name }),
  })

  if (!response.ok) {
    throw new Error('Failed to create artist')
  }

  return response.json()
}

// Updates an existing artist through the backend.
export async function updateArtist(id: number, name: string): Promise<Artist> {
  const response = await fetch(`${API_BASE_URL}/api/artists/${id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ name }),
  })

  if (!response.ok) {
    throw new Error('Failed to update artist')
  }

  return response.json()
}

// Deletes an artist through the backend.
export async function deleteArtist(id: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/artists/${id}`, {
    method: 'DELETE',
  })

  // Handle artists that still have associated albums.
  if (response.status === 409) {
    throw new Error(
      'Cannot delete this artist because they have associated albums. Delete or reassign their albums first.',
    )
  }

  if (!response.ok) {
    throw new Error('Unable to delete artist. Please try again.')
  }
}
