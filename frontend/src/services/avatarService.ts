import { useClerkApi, ClerkApiService } from './clerkApi';
import { useAuth } from '@clerk/nextjs';

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
   * Get existing avatar for authenticated user using ClerkApiService
   */
  private static avatarCache: {
    data: AvatarData | null;
    timestamp: number;
  } = { data: null, timestamp: 0 };

  static async getUserAvatar(apiService: ClerkApiService): Promise<AvatarData> {
    try {
      // Return cached data if it's fresh (5 seconds)
      const now = Date.now();
      if (this.avatarCache.data && now - this.avatarCache.timestamp < 5000) {
        return this.avatarCache.data;
      }

      console.log('🔍 Fetching avatar for authenticated user');
      
      const data = await apiService.get<AvatarData>('/api/v1/avatar/me');

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
   * Generate new avatar for authenticated user using ClerkApiService
   */
  static async generateAvatar(apiService: ClerkApiService): Promise<GenerateAvatarResponse> {
    try {
      console.log('🎨 Generating avatar for authenticated user');
      
      const data = await apiService.post<GenerateAvatarResponse>('/api/v1/avatar/generate-avatar/me');
      
      // Clear cache since we just generated a new avatar
      this.avatarCache = { data: null, timestamp: 0 };
      
      console.log('✅ Avatar generated successfully:', data);
      return data;
    } catch (error: any) {
      console.error('❌ Error generating avatar:', error);
      throw error;
    }
  }

  /**
   * Check if authenticated user has an existing avatar using ClerkApiService
   */
  static async hasAvatar(apiService: ClerkApiService): Promise<boolean> {
    try {
      const avatarData = await this.getUserAvatar(apiService);
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

// Convenience hooks for React components using ClerkApiService
export const useAvatarService = () => {
  const apiService = useClerkApi();
  
  return {
    getUserAvatar: () => AvatarService.getUserAvatar(apiService),
    generateAvatar: () => AvatarService.generateAvatar(apiService),
    hasAvatar: () => AvatarService.hasAvatar(apiService),
    getAvatarImageUrl: AvatarService.getAvatarImageUrl,
    handleAvatarError: AvatarService.handleAvatarError,
  };
};

// Legacy support - wrapper functions that maintain backward compatibility
export const LegacyAvatarService = {
  async getUserAvatar(getToken: () => Promise<string | null>): Promise<AvatarData> {
    const apiService = new ClerkApiService(getToken);
    return AvatarService.getUserAvatar(apiService);
  },
  
  async generateAvatar(getToken: () => Promise<string | null>): Promise<GenerateAvatarResponse> {
    const apiService = new ClerkApiService(getToken);
    return AvatarService.generateAvatar(apiService);
  },
  
  async hasAvatar(getToken: () => Promise<string | null>): Promise<boolean> {
    const apiService = new ClerkApiService(getToken);
    return AvatarService.hasAvatar(apiService);
  },
  
  getAvatarImageUrl: AvatarService.getAvatarImageUrl,
  handleAvatarError: AvatarService.handleAvatarError,
};

export default AvatarService;
