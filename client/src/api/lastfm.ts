import { apiRequest } from './request'
import type {
  LastFMStatus,
  LastFMRecentTracks,
  LastFMNowPlaying,
} from '../types/lastfm'

// Fetches the user's Last.fm connection status.
export async function getLastFMStatus(): Promise<LastFMStatus> {
  return apiRequest<LastFMStatus>('/api/lastfm/status', {
    auth: true,
  })
}

// Fetches the user's recently played Last.fm tracks.
export async function getRecentTracks(): Promise<LastFMRecentTracks> {
  return apiRequest<LastFMRecentTracks>('/api/lastfm/recent-tracks', {
    auth: true,
  })
}

// Fetches the user's currently playing Last.fm track.
export async function getNowPlaying(): Promise<LastFMNowPlaying> {
  return apiRequest<LastFMNowPlaying>('/api/lastfm/now-playing', {
    auth: true,
  })
}

// Disconnects the user's Last.fm account.
export async function disconnectLastFM(): Promise<void> {
  await apiRequest<void>('/api/lastfm/disconnect', {
    method: 'DELETE',
    auth: true,
  })
}

// Redirects the user to Last.fm to connect their account.
export async function connectLastFM(): Promise<void> {
  const response = await apiRequest<{ auth_url: string }>(
    '/api/lastfm/connect',
    {
      auth: true,
      credentials: 'include',
    },
  )

  window.location.href = response.auth_url
}
