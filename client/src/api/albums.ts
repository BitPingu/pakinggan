import { apiRequest, ApiError } from './request'
import type { Album } from '../types/music'

// Fetches all albums from the backend.
export async function getAlbums(): Promise<Album[]> {
  return apiRequest<Album[]>('/api/albums/')
}

// Creates a new album through the backend.
export async function createAlbum(
  title: string,
  artistId: number,
): Promise<Album> {
  return apiRequest<Album>('/api/albums/', {
    method: 'POST',
    body: JSON.stringify({ title, artist_id: artistId }),
  })
}

// Updates an existing album through the backend.
export async function updateAlbum(
  id: number,
  title: string,
  artistId: number,
): Promise<Album> {
  return apiRequest<Album>(`/api/albums/${id}`, {
    method: 'PUT',
    body: JSON.stringify({ title, artist_id: artistId }),
  })
}

// Deletes an album through the backend.
export async function deleteAlbum(id: number): Promise<void> {
  try {
    await apiRequest<void>(`/api/albums/${id}`, {
      method: 'DELETE',
    })
  } catch (error) {
    // Handle albums that still have associated tracks.
    if (error instanceof ApiError && error.status === 409) {
      throw new Error(
        'Cannot delete this album because it has associated tracks. Delete or reassign its tracks first.',
        { cause: error },
      )
    }

    throw error
  }
}
