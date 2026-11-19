import API_BASE_URL from './client'
import type { TokenResponse, User } from '../types/user'

// Registers a new user through the backend.
export async function registerUser(
  username: string,
  email: string,
  password: string,
): Promise<User> {
  const response = await fetch(`${API_BASE_URL}/api/users/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, email, password }),
  })

  if (!response.ok) {
    throw new Error('Failed to register user')
  }

  return response.json()
}

// Authenticates a user and returns an access token.
export async function loginUser(
  username: string,
  password: string,
): Promise<TokenResponse> {
  const response = await fetch(`${API_BASE_URL}/api/users/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
  })

  if (!response.ok) {
    throw new Error('Failed to log in')
  }

  return response.json()
}

// Retrieves the authenticated user's profile.
export async function getCurrentUser(token: string): Promise<User> {
  const response = await fetch(`${API_BASE_URL}/api/users/me`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })

  if (!response.ok) {
    throw new Error('Failed to fetch current user')
  }

  return response.json()
}
