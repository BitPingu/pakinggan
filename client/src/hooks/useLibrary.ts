import { useContext } from 'react'
import { LibraryContext } from '../context/library-context'

// Provides access to the shared library context.
export function useLibrary() {
  const context = useContext(LibraryContext)

  // Prevents the hook from being used outside the library provider.
  if (!context) {
    throw new Error('useLibrary must be used within a LibraryProvider')
  }

  return context
}
