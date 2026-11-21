import { apiRequest } from './request'
import type { Track } from '../types/music'

// Fetches all tracks from the backend.
export async function getTracks(): Promise<Track[]> {
  return apiRequest<Track[]>('/api/tracks/')
}

// Creates a new track through the backend.
export async function createTrack(
  title: string,
  duration: number | null,
  albumId: number,
): Promise<Track> {
  return apiRequest<Track>('/api/tracks/', {
    method: 'POST',
    body: JSON.stringify({ title, duration, album_id: albumId }),
  })
}

// Updates an existing track through the backend.
export async function updateTrack(
  id: number,
  title: string,
  duration: number | null,
  albumId: number,
): Promise<Track> {
  return apiRequest<Track>(`/api/tracks/${id}`, {
    method: 'PUT',
    body: JSON.stringify({ title, duration, album_id: albumId }),
  })
}

// Deletes a track through the backend.
export async function deleteTrack(id: number): Promise<void> {
  await apiRequest<void>(`/api/tracks/${id}`, {
    method: 'DELETE',
  })
}
