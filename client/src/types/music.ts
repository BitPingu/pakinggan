// Represents an artist returned by the backend.
export interface Artist {
  id: number
  name: string
}

// Represents an album returned by the backend.
export interface Album {
  id: number
  title: string
  artist_id: number
}

// Represents a track returned by the backend.
export interface Track {
  id: number
  title: string
  duration: number | null
  album_id: number
}
