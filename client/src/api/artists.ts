import API_BASE_URL from './client'
import type { Artist } from '../types/music'

// Fetches all artists from the backend.
export async function getArtists(): Promise<Artist[]> {
  // send a get request to fastapi
  const response = await fetch(`${API_BASE_URL}/api/artists/`)

  // check if request succeeded
  if (!response.ok) {
    throw new Error('Failed to fetch artists')
  }

  // convert response into javascript data
  return response.json()
}
