import { endpoint } from '../utils/api';
import { useClerkAuth } from '@/contexts/ClerkAuthContext';

export interface AvatarData {
  success: boolean;
  message?: string;
  avatar_name?: string;
  avatar_description?: string;
  avatar_image_url?: string;
  generated_at?: string;
}

export interface GenerateAvatarResponse {
  success: boolean;
  message: string;
  avatar_name: string;
  avatar_description: string;
  avatar_image_url: string;
  generated_at: string;
}

class AvatarService {
  /**
   * Get existing avatar for authenticated user
   */
  private static avatarCache: {
    data: AvatarData | null;
    timestamp: number;
  } = { data: null, timestamp: 0 };

  static async getUserAvatar(token: string): Promise<AvatarData> {
    try {
      // Return cached data if it's fresh (5 seconds)
      const now = Date.now();
      if (this.avatarCache.data && now - this.avatarCache.timestamp < 5000) {
        return this.avatarCache.data;
      }

      console.log('🔍 Fetching avatar for authenticated user');
      if (!token) {
        throw new Error('User not authenticated');
      }
      
      const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      };
      const response = await fetch(endpoint('/avatar/me'), {
        method: 'GET',
        headers
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();

      // Update cache
      this.avatarCache = {
        data,
        timestamp: now
      };

      console.log('✅ Avatar retrieved:', data);
      return data;
    } catch (error: any) {
      // Return cached data if available, even if stale
      if (this.avatarCache.data) {
        console.warn('Using cached avatar data after error');
        return this.avatarCache.data;
      }
      console.error('❌ Error retrieving avatar:', error);
      throw error;
    }
  }

  /**
   * Generate new avatar for authenticated user
   */
  static async generateAvatar(token: string): Promise<GenerateAvatarResponse> {
    try {
      console.log('🎨 Generating avatar for authenticated user');
      if (!token) {
        throw new Error('User not authenticated');
      }
      
      const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      };
      const response = await fetch(endpoint('/avatar/generate-avatar/me'), {
        method: 'POST',
        headers
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('✅ Avatar generated successfully:', data);
      return data;
    } catch (error: any) {
      console.error('❌ Error generating avatar:', error);
      console.error('API error details:', error);
      throw error;
    }
  }

  /**
   * Check if authenticated user has an existing avatar
   */
  static async hasAvatar(token: string): Promise<boolean> {
    try {
      const avatarData = await this.getUserAvatar(token);
      return avatarData.success && !!avatarData.avatar_name;
    } catch (error) {
      console.log('No avatar found for this user');
      return false;
    }
  }

  /**
   * Get complete avatar image URL
   */
  static getAvatarImageUrl(relativeUrl: string): string {
    if (!relativeUrl) return '';
    
    // If URL is already complete, return as is
    if (relativeUrl.startsWith('http')) {
      return relativeUrl;
    }
    
    // Build complete URL with API base URL
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    return `${apiUrl}${relativeUrl}`;
  }

  /**
   * Handle avatar errors in standardized way
   */
  static handleAvatarError(error: any): string {
    if (error?.response?.status === 404) {
      return 'No avatar found for this user';
    } else if (error?.response?.status === 403) {
      return 'You are not authorized to generate this avatar';
    } else if (error?.response?.status === 500) {
      return 'Internal server error while generating avatar';
    } else if (error?.response?.data?.detail) {
      return error.response.data.detail;
    } else {
      return 'An unexpected error occurred';
    }
  }
}

export default AvatarService;
