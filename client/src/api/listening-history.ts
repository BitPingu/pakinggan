import { apiRequest } from './request'
import type { ListeningHistoryEntry } from '../types/listening-history'

// Fetches a paginated list of the user's listening history.
export async function getListeningHistory(
  limit: number = 20,
  offset: number = 0,
): Promise<ListeningHistoryEntry[]> {
  return apiRequest<ListeningHistoryEntry[]>(
    `/api/listening-history/?limit=${limit}&offset=${offset}`,
    { auth: true },
  )
}

// Syncs the user's listening history with Last.fm.
export async function syncListeningHistory(): Promise<{ imported: number }> {
  return apiRequest<{ imported: number }>('/api/listening-history/sync', {
    method: 'POST',
    auth: true,
  })
}
