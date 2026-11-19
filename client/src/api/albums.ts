import API_BASE_URL from './client'
import type { Album } from '../types/music'

// Fetches all albums from the backend.
export async function getAlbums(): Promise<Album[]> {
  const response = await fetch(`${API_BASE_URL}/api/albums/`)

  if (!response.ok) {
    throw new Error('Failed to fetch albums')
  }

  return response.json()
}

// Creates a new album through the backend.
export async function createAlbum(
  title: string,
  artistId: number,
): Promise<Album> {
  const response = await fetch(`${API_BASE_URL}/api/albums/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ title, artist_id: artistId }),
  })

  if (!response.ok) {
    throw new Error('Failed to create album')
  }

  return response.json()
}

// Updates an existing album through the backend.
export async function updateAlbum(
  id: number,
  title: string,
  artistId: number,
): Promise<Album> {
  const response = await fetch(`${API_BASE_URL}/api/albums/${id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ title, artist_id: artistId }),
  })

  if (!response.ok) {
    throw new Error('Failed to update album')
  }

  return response.json()
}

// Deletes an album through the backend.
export async function deleteAlbum(id: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/albums/${id}`, {
    method: 'DELETE',
  })

  if (!response.ok) {
    throw new Error('Failed to delete album')
  }
}
