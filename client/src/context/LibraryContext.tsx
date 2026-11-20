import { useEffect, useState, type ReactNode } from 'react'
import {
  createArtist,
  deleteArtist,
  getArtists,
  updateArtist,
} from '../api/artists'
import { createAlbum, deleteAlbum, getAlbums, updateAlbum } from '../api/albums'
import { createTrack, deleteTrack, getTracks, updateTrack } from '../api/tracks'
import type { Artist, Album, Track } from '../types/music'
import { LibraryContext } from './library-context'

interface LibraryProviderProps {
  children: ReactNode
}

// Provides library data and operations to authenticated application pages.
function LibraryProvider({ children }: LibraryProviderProps) {
  // Stores the artists, albums, and tracks returned by the backend.
  const [artists, setArtists] = useState<Artist[]>([])
  const [albums, setAlbums] = useState<Album[]>([])
  const [tracks, setTracks] = useState<Track[]>([])

  // Tracks whether the initial library data is loading.
  const [isLoading, setIsLoading] = useState(true)

  // Stores any error that occurs while fetching library data.
  const [error, setError] = useState<string | null>(null)

  // Fetches all library data when the provider first loads.
  useEffect(() => {
    async function fetchLibrary() {
      try {
        // Retrieve all three collections from the backend.
        const [artistData, albumData, trackData] = await Promise.all([
          getArtists(),
          getAlbums(),
          getTracks(),
        ])

        // Save the returned collections in shared state.
        setArtists(artistData)
        setAlbums(albumData)
        setTracks(trackData)
      } catch {
        setError('Unable to load your library. Please try again later.')
      } finally {
        // Stop displaying the loading state.
        setIsLoading(false)
      }
    }

    fetchLibrary()
  }, [])

  // Creates an artist and adds it to the shared collection.
  async function addArtist(name: string) {
    const newArtist = await createArtist(name)

    setArtists((currentArtists) => [...currentArtists, newArtist])

    return newArtist
  }

  // Updates an artist in the shared collection.
  async function editArtist(id: number, name: string) {
    const updatedArtist = await updateArtist(id, name)

    setArtists((currentArtists) =>
      currentArtists.map((artist) =>
        artist.id === updatedArtist.id ? updatedArtist : artist,
      ),
    )

    return updatedArtist
  }

  // Deletes an artist from the shared collection.
  async function removeArtist(id: number) {
    await deleteArtist(id)

    setArtists((currentArtists) =>
      currentArtists.filter((artist) => artist.id !== id),
    )
  }

  // Creates an album and adds it to the shared collection.
  async function addAlbum(title: string, artistId: number) {
    const newAlbum = await createAlbum(title, artistId)

    setAlbums((currentAlbums) => [...currentAlbums, newAlbum])

    return newAlbum
  }

  // Updates an album in the shared collection.
  async function editAlbum(id: number, title: string, artistId: number) {
    const updatedAlbum = await updateAlbum(id, title, artistId)

    setAlbums((currentAlbums) =>
      currentAlbums.map((album) =>
        album.id === updatedAlbum.id ? updatedAlbum : album,
      ),
    )

    return updatedAlbum
  }

  // Deletes an album from the shared collection.
  async function removeAlbum(id: number) {
    await deleteAlbum(id)

    setAlbums((currentAlbums) =>
      currentAlbums.filter((album) => album.id !== id),
    )
  }

  // Creates a track and adds it to the shared collection.
  async function addTrack(
    title: string,
    duration: number | null,
    albumId: number,
  ) {
    const newTrack = await createTrack(title, duration, albumId)

    setTracks((currentTracks) => [...currentTracks, newTrack])

    return newTrack
  }

  // Updates a track in the shared collection.
  async function editTrack(
    id: number,
    title: string,
    duration: number | null,
    albumId: number,
  ) {
    const updatedTrack = await updateTrack(id, title, duration, albumId)

    setTracks((currentTracks) =>
      currentTracks.map((track) =>
        track.id === updatedTrack.id ? updatedTrack : track,
      ),
    )

    return updatedTrack
  }

  // Deletes a track from the shared collection.
  async function removeTrack(id: number) {
    await deleteTrack(id)

    setTracks((currentTracks) =>
      currentTracks.filter((track) => track.id !== id),
    )
  }

  return (
    <LibraryContext.Provider
      value={{
        artists,
        albums,
        tracks,
        isLoading,
        error,
        addArtist,
        editArtist,
        removeArtist,
        addAlbum,
        editAlbum,
        removeAlbum,
        addTrack,
        editTrack,
        removeTrack,
      }}
    >
      {children}
    </LibraryContext.Provider>
  )
}

export default LibraryProvider
