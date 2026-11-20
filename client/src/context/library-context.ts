import { createContext } from 'react'
import type { Artist, Album, Track } from '../types/music'

// Defines the shared library data and operations available to application pages.
export interface LibraryContextType {
  artists: Artist[]
  albums: Album[]
  tracks: Track[]
  isLoading: boolean
  error: string | null
  addArtist: (name: string) => Promise<Artist>
  editArtist: (id: number, name: string) => Promise<Artist>
  removeArtist: (id: number) => Promise<void>
  addAlbum: (title: string, artistId: number) => Promise<Album>
  editAlbum: (id: number, title: string, artistId: number) => Promise<Album>
  removeAlbum: (id: number) => Promise<void>
  addTrack: (
    title: string,
    duration: number | null,
    albumId: number,
  ) => Promise<Track>
  editTrack: (
    id: number,
    title: string,
    duration: number | null,
    albumId: number,
  ) => Promise<Track>
  removeTrack: (id: number) => Promise<void>
}

// Provides shared library data through React Context.
export const LibraryContext = createContext<LibraryContextType | undefined>(
  undefined,
)
