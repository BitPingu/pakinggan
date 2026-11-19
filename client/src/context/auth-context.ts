import { createContext } from 'react'
import type { User } from '../types/user'

// Defines the authentication data and functions shared across the application.
export interface AuthContextType {
  user: User | null // Currently authenticated user's profile.
  token: string | null // Access token used for authenticated API requests.
  isLoading: boolean // Indicates whether the initial session restoration is in progress.
  login: (username: string, password: string) => Promise<void> // Authenticates the user.
  logout: () => void // Clears the current authentication session.
}

// Creates the authentication context.
export const AuthContext = createContext<AuthContextType | undefined>(undefined)
