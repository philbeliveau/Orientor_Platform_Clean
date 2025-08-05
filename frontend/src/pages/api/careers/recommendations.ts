import type { NextApiRequest, NextApiResponse } from 'next';
import axios from 'axios';

// Get the backend URL from environment variables
const BACKEND_API_URL = process.env.BACKEND_API_URL;
if (!BACKEND_API_URL) {
  console.error('BACKEND_API_URL environment variable is not set');
}

// Create an axios instance with the same configuration as your other endpoints
const backendApi = axios.create({
  baseURL: BACKEND_API_URL,
  withCredentials: true,
});

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'GET') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  if (!BACKEND_API_URL) {
    console.error('BACKEND_API_URL is not configured');
    return res.status(500).json({ 
      message: 'Backend API URL is not configured',
      error: 'Missing BACKEND_API_URL environment variable'
    });
  }

  try {
    const { limit = 30 } = req.query;
    const url = `/careers/recommendations`;
    console.log('Proxying request to:', `${BACKEND_API_URL}${url}`);
    
    // Use the same axios instance configuration as your other endpoints
    const response = await backendApi.get(url, {
      params: { limit },
      headers: {
        Authorization: req.headers.authorization,
      },
    });
    
    console.log('Received response from backend:', response.status);
    res.status(200).json(response.data);
  } catch (error: any) {
    console.error('Error proxying career recommendations:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status,
      url: error.config?.url,
      headers: error.config?.headers
    });
    
    res.status(error.response?.status || 500).json({
      message: error.response?.data?.message || 'internal server error',
      error: error.message,
      details: error.response?.data
    });
  }
} 