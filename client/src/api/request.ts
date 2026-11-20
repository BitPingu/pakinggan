import API_BASE_URL from './client'

// Represents an unsuccessful API response.
export class ApiError extends Error {
  public status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

// Defines the additional options supported by API requests.
interface ApiRequestOptions extends RequestInit {
  auth?: boolean
  token?: string
}

// Sends a request to the backend and handles its response.
export async function apiRequest<T>(
  path: string,
  options: ApiRequestOptions = {},
): Promise<T> {
  const { auth = false, token, ...requestOptions } = options

  // Prepare the request headers.
  const headers = new Headers(requestOptions.headers)

  // Set the content type when sending a request body.
  if (requestOptions.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  // Attach the access token to authenticated requests.
  if (auth || token) {
    const accessToken = token ?? sessionStorage.getItem('access_token')

    if (accessToken) {
      headers.set('Authorization', `Bearer ${accessToken}`)
    }
  }

  // Send the request to the backend.
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...requestOptions,
    headers,
  })

  // Handle unsuccessful responses.
  if (!response.ok) {
    let message = `Request failed with status ${response.status}`

    try {
      // Extract the error message returned by the backend.
      const data = await response.json()

      if (typeof data.detail === 'string') {
        message = data.detail
      }
    } catch {
      // Use the default error message if the response isn't JSON.
    }

    throw new ApiError(message, response.status)
  }

  // Return undefined for successful requests without a response body.
  if (response.status === 204) {
    return undefined as T
  }

  // Return the parsed JSON response.
  return response.json()
}
