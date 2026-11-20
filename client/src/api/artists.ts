import { apiRequest, ApiError } from './request'
import type { Artist } from '../types/music'

// Fetches all artists from the backend.
export async function getArtists(): Promise<Artist[]> {
  return apiRequest<Artist[]>('/api/artists/')
}

// Creates a new artist through the backend.
export async function createArtist(name: string): Promise<Artist> {
  return apiRequest<Artist>('/api/artists/', {
    method: 'POST',
    body: JSON.stringify({ name }),
  })
}

// Updates an existing artist through the backend.
export async function updateArtist(id: number, name: string): Promise<Artist> {
  return apiRequest<Artist>(`/api/artists/${id}`, {
    method: 'PUT',
    body: JSON.stringify({ name }),
  })
}

// Deletes an artist through the backend.
export async function deleteArtist(id: number): Promise<void> {
  try {
    await apiRequest<void>(`/api/artists/${id}`, {
      method: 'DELETE',
    })
  } catch (error) {
    // Handle artists that still have associated albums.
    if (error instanceof ApiError && error.status === 409) {
      throw new Error(
        'Cannot delete this artist because they have associated albums. Delete or reassign their albums first.',
        { cause: error },
      )
    }

    throw error
  }
}
