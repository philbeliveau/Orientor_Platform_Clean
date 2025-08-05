import api from './api';

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
  static async getUserAvatar(): Promise<AvatarData> {
    try {
      console.log('🔍 Récupération de l\'avatar pour l\'utilisateur authentifié');
      const response = await api.get('/api/v1/avatar/me');
      console.log('✅ Avatar récupéré:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('❌ Erreur lors de la récupération de l\'avatar:', error);
      console.error('Détails de l\'erreur API:', {
        status: error?.response?.status,
        statusText: error?.response?.statusText,
        data: error?.response?.data,
        config: {
          baseURL: error?.config?.baseURL,
          url: error?.config?.url,
          headers: error?.config?.headers
        }
      });
      throw error;
    }
  }

  /**
   * Génère un nouvel avatar pour l'utilisateur authentifié
   */
  static async generateAvatar(): Promise<GenerateAvatarResponse> {
    try {
      console.log('🎨 Génération d\'un avatar pour l\'utilisateur authentifié');
      const response = await api.post('/api/v1/avatar/generate-avatar/me');
      console.log('✅ Avatar généré avec succès:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('❌ Erreur lors de la génération de l\'avatar:', error);
      console.error('Détails de l\'erreur API:', {
        status: error?.response?.status,
        statusText: error?.response?.statusText,
        data: error?.response?.data,
        config: {
          baseURL: error?.config?.baseURL,
          url: error?.config?.url,
          headers: error?.config?.headers
        }
      });
      throw error;
    }
  }

  /**
   * Vérifie si l'utilisateur authentifié a un avatar existant
   */
  static async hasAvatar(): Promise<boolean> {
    try {
      const avatarData = await this.getUserAvatar();
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