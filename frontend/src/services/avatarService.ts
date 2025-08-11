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
   * Récupère l'avatar existant de l'utilisateur authentifié
   */
  private static avatarCache: {
    data: AvatarData | null;
    timestamp: number;
  } = { data: null, timestamp: 0 };

  static async getUserAvatar(getToken: () => Promise<string | null>): Promise<AvatarData> {
    try {
      // Return cached data if it's fresh (5 seconds)
      const now = Date.now();
      if (this.avatarCache.data && now - this.avatarCache.timestamp < 5000) {
        return this.avatarCache.data;
      }

      console.log('🔍 Récupération de l\'avatar pour l\'utilisateur authentifié');
      const token = await getToken();
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

      console.log('✅ Avatar récupéré:', data);
      return data;
    } catch (error: any) {
      // Return cached data if available, even if stale
      if (this.avatarCache.data) {
        console.warn('Using cached avatar data after error');
        return this.avatarCache.data;
      }
      console.error('❌ Erreur lors de la récupération de l\'avatar:', error);
      throw error;
    }
  }

  /**
   * Génère un nouvel avatar pour l'utilisateur authentifié
   */
  static async generateAvatar(getToken: () => Promise<string | null>): Promise<GenerateAvatarResponse> {
    try {
      console.log('🎨 Génération d\'un avatar pour l\'utilisateur authentifié');
      const token = await getToken();
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
      console.log('✅ Avatar généré avec succès:', data);
      return data;
    } catch (error: any) {
      console.error('❌ Erreur lors de la génération de l\'avatar:', error);
      console.error('Détails de l\'erreur API:', error);
      throw error;
    }
  }

  /**
   * Vérifie si l'utilisateur authentifié a un avatar existant
   */
  static async hasAvatar(getToken: () => Promise<string | null>): Promise<boolean> {
    try {
      const avatarData = await this.getUserAvatar(getToken);
      return avatarData.success && !!avatarData.avatar_name;
    } catch (error) {
      console.log('Aucun avatar trouvé pour cet utilisateur');
      return false;
    }
  }

  /**
   * Obtient l'URL complète de l'image d'avatar
   */
  static getAvatarImageUrl(relativeUrl: string): string {
    if (!relativeUrl) return '';
    
    // Si l'URL est déjà complète, la retourner telle quelle
    if (relativeUrl.startsWith('http')) {
      return relativeUrl;
    }
    
    // Construire l'URL complète avec l'API base URL
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    return `${apiUrl}${relativeUrl}`;
  }

  /**
   * Gère les erreurs d'avatar de manière standardisée
   */
  static handleAvatarError(error: any): string {
    if (error?.response?.status === 404) {
      return 'Aucun avatar trouvé pour cet utilisateur';
    } else if (error?.response?.status === 403) {
      return 'Vous n\'avez pas l\'autorisation de générer cet avatar';
    } else if (error?.response?.status === 500) {
      return 'Erreur interne du serveur lors de la génération de l\'avatar';
    } else if (error?.response?.data?.detail) {
      return error.response.data.detail;
    } else {
      return 'Une erreur inattendue s\'est produite';
    }
  }
}

export default AvatarService;
