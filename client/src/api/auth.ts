import { apiRequest } from './request'
import type { TokenResponse, User } from '../types/user'

// Registers a new user through the backend.
export async function registerUser(
  username: string,
  email: string,
  password: string,
): Promise<User> {
  return apiRequest<User>('/api/users/', {
    method: 'POST',
    body: JSON.stringify({ username, email, password }),
  })
}

// Authenticates a user and returns an access token.
export async function loginUser(
  username: string,
  password: string,
): Promise<TokenResponse> {
  return apiRequest<TokenResponse>('/api/users/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  })
}

// Retrieves the authenticated user's profile.
export async function getCurrentUser(token: string): Promise<User> {
  return apiRequest<User>('/api/users/me', { token })
}
