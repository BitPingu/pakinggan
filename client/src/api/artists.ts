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

// Creates a new artist through the backend.
export async function createArtist(name: string): Promise<Artist> {
  // send a post request to fastapi
  const response = await fetch(`${API_BASE_URL}/api/artists/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ name }),
  })

  // check if request succeeded
  if (!response.ok) {
    throw new Error('Failed to create artist')
  }

  // return the newly created artist
  return response.json()
}
