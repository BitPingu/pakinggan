import { apiRequest } from './request'
import type { TokenResponse, User } from '../types/user'

interface PasswordResetResponse {
  message: string
}

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

// Requests a password-reset email.
export async function forgotPassword(
  email: string,
): Promise<PasswordResetResponse> {
  return apiRequest<PasswordResetResponse>('/api/users/forgot-password', {
    method: 'POST',
    body: JSON.stringify({ email }),
  })
}

// Resets a user's password using a valid reset token.
export async function resetPassword(
  token: string,
  newPassword: string,
): Promise<PasswordResetResponse> {
  return apiRequest<PasswordResetResponse>('/api/users/reset-password', {
    method: 'POST',
    body: JSON.stringify({ token, new_password: newPassword }),
  })
}
