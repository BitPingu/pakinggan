import { useEffect, useState, type ReactNode } from 'react'
import {
  deleteAccount as deleteAccountRequest,
  getCurrentUser,
  loginUser,
  registerUser,
  changePassword as changePasswordRequest,
  changeEmail as changeEmailRequest,
} from '../api/auth'
import type { User } from '../types/user'
import { ApiError } from '../api/request'
import { AuthContext } from './auth-context'

// Provides authentication state and functions to the application.
export function AuthProvider({ children }: { children: ReactNode }) {
  // Stores the authenticated user's profile and access token.
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)

  // Tracks whether the initial session restoration is complete.
  const [isLoading, setIsLoading] = useState(true)

  // Restores the user's session when the application loads.
  useEffect(() => {
    // Prevents state updates if the component unmounts before the request finishes.
    let cancelled = false

    async function restoreSession() {
      const storedToken = sessionStorage.getItem('access_token')

      // No stored token means there is no session to restore.
      if (!storedToken) {
        setIsLoading(false)
        return
      }

      try {
        // Validates the stored token and retrieves the user's profile.
        const currentUser = await getCurrentUser(storedToken)

        if (!cancelled) {
          setToken(storedToken)
          setUser(currentUser)
        }
      } catch (error) {
        // Removes the stored token only if the backend rejects the session.
        if (
          error instanceof ApiError &&
          (error.status === 401 || error.status === 403)
        ) {
          sessionStorage.removeItem('access_token')
        }
      } finally {
        // Finishes loading after the session restoration attempt.
        if (!cancelled) {
          setIsLoading(false)
        }
      }
    }

    restoreSession()

    return () => {
      cancelled = true
    }
  }, [])

  // Authenticates the user, retrieves their profile, and stores their session.
  async function login(username: string, password: string) {
    const tokenResponse = await loginUser(username, password)
    const accessToken = tokenResponse.access_token
    const currentUser = await getCurrentUser(accessToken)

    sessionStorage.setItem('access_token', accessToken)
    setToken(accessToken)
    setUser(currentUser)
  }

  // Registers a new user through the backend.
  async function register(username: string, email: string, password: string) {
    await registerUser(username, email, password)
  }

  // Deletes the account and clears the session after successful deletion.
  async function deleteAccount(password: string) {
    if (!token) {
      throw new Error('No authenticated session found.')
    }

    await deleteAccountRequest(token, password)
    logout()
  }

  // Changes the password and clears the session after successful password change.
  async function changePassword(currentPassword: string, newPassword: string) {
    if (!token) {
      throw new Error('No authenticated session found.')
    }

    await changePasswordRequest(token, currentPassword, newPassword)
    logout()
  }

  // Changes the email and refreshes the authenticated user's profile.
  async function changeEmail(email: string, currentPassword: string) {
    if (!token) {
      throw new Error('No authenticated session found.')
    }

    await changeEmailRequest(token, email, currentPassword)

    const currentUser = await getCurrentUser(token)
    setUser(currentUser)
  }

  // Logs out the user and clears their stored session and authentication state.
  function logout() {
    sessionStorage.removeItem('access_token')
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isLoading,
        login,
        register,
        changePassword,
        changeEmail,
        deleteAccount,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}
