// Represents the authenticated user's public profile.
export interface User {
  id: number
  username: string
  email: string
}

// Represents the access token returned after login.
export interface TokenResponse {
  access_token: string
  token_type: string
}
