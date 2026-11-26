// Represents the artist information returned with a track.
export interface ListeningHistoryArtist {
  id: number
  name: string
}

// Represents the album information returned with a track.
export interface ListeningHistoryAlbum {
  id: number
  title: string
}

// Represents the track information returned with a listening-history entry.
export interface ListeningHistoryTrack {
  id: number
  title: string
  duration: number | null
  artist: ListeningHistoryArtist
  album: ListeningHistoryAlbum | null
}

// Represents a listening-history entry returned by the backend.
export interface ListeningHistoryEntry {
  id: number
  played_at: string
  track: ListeningHistoryTrack
}
