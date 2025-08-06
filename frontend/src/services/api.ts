import axios from 'axios'

// Create basic axios client for legacy compatibility
const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Response interceptor for error handling
apiClient.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      console.error('Unauthorized request - authentication required')
      // In a Clerk-based app, redirect to sign-in
      if (typeof window !== 'undefined') {
        window.location.href = '/sign-in';
      }
    }
    return Promise.reject(error)
  }
)

// Client-side API helper that requires token to be passed (for Clerk integration)
export const getJobRecommendations = async (token: string, topK: number = 3) => {
  try {
    const response = await apiClient.get(`/api/v1/jobs/recommendations/me?top_k=${topK}`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    return response.data
  } catch (error) {
    console.error('Error fetching job recommendations:', error)
    throw error
  }
}

// Server-side API helper (for use in API routes)
export const serverApiClient = (token?: string) => {
  const client = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    }
  })

  return client
}

// Legacy compatibility export - NOTE: Use useClerkApi() for authenticated requests
export default apiClient
