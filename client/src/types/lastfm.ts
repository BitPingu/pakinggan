// Represents the user's Last.fm connection status.
export interface LastFMStatus {
  connected: boolean
  lastfm_username: string | null
}

// Represents a recently played Last.fm track.
export interface LastFMTrack {
  name: string
  artist: string
  album: string | null
  url: string | null
  image: string | null
  played_at: string | null
  nowplaying: boolean
}

// Represents the user's recent Last.fm tracks.
export interface LastFMRecentTracks {
  tracks: LastFMTrack[]
}

// Represents the user's currently playing Last.fm track.
export interface LastFMNowPlaying {
  track: LastFMTrack | null
}

// Represents supplementary information about a track.
export interface TrackMetadata {
  genres: string[]
  releaseDate: string | null
  duration: number | null
  description: string | null
  sourceUrl: string | null
}

// Represents supplementary information about an artist.
export interface ArtistMetadata {
  image: string | null
  biography: string | null
  genres: string[]
  sourceUrl: string | null
}
