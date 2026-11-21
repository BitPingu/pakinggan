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

// Changes the authenticated user's password after verifying their current password.
export async function changePassword(
  token: string,
  currentPassword: string,
  newPassword: string,
): Promise<PasswordResetResponse> {
  return apiRequest<PasswordResetResponse>('/api/users/me/password', {
    method: 'PUT',
    body: JSON.stringify({
      current_password: currentPassword,
      new_password: newPassword,
    }),
    token,
  })
}

// Changes the authenticated user's email after verifying their current password.
export async function changeEmail(
  token: string,
  email: string,
  currentPassword: string,
): Promise<PasswordResetResponse> {
  return apiRequest<PasswordResetResponse>('/api/users/me/email', {
    method: 'PUT',
    body: JSON.stringify({
      email,
      current_password: currentPassword,
    }),
    token,
  })
}

// Changes the authenticated user's username after verifying their current password.
export async function changeUsername(
  token: string,
  username: string,
  currentPassword: string,
): Promise<PasswordResetResponse> {
  return apiRequest<PasswordResetResponse>('/api/users/me/username', {
    method: 'PUT',
    body: JSON.stringify({
      username,
      current_password: currentPassword,
    }),
    token,
  })
}

// Deletes the authenticated user's account after password confirmation.
export async function deleteAccount(
  token: string,
  password: string,
): Promise<void> {
  return apiRequest<void>('/api/users/me', {
    method: 'DELETE',
    body: JSON.stringify({ password }),
    token,
  })
}
