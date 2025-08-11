import { clerkApiService } from './api';

// Type definitions
export interface InsightData {
  preview: string;
  full_text: string;
  if_you_accept: string;
}

/**
 * Génère un insight philosophique pour l'utilisateur connecté
 * @param token - Clerk JWT token for authentication
 * @returns Les données d'insight générées
 */
export const generateInsight = async (token: string): Promise<InsightData> => {
  try {
    return await clerkApiService.request<InsightData>('/api/v1/insight/generate', {
      method: 'POST',
      token,
      body: JSON.stringify({})
    });
  } catch (error) {
    console.error('Erreur lors de la génération de l\'insight philosophique:', error);
    throw error;
  }
};

/**
 * Sauvegarde un insight philosophique pour l'utilisateur connecté
 * @param token - Clerk JWT token for authentication
 * @param philosophicalText - Le texte philosophique à sauvegarder
 * @returns Le statut de succès
 */
export const saveInsight = async (token: string, philosophicalText: string): Promise<{ success: boolean }> => {
  try {
    return await clerkApiService.request<{ success: boolean }>('/api/v1/insight/save', {
      method: 'PATCH',
      token,
      body: JSON.stringify({
        philosophical_text: philosophicalText
      })
    });
  } catch (error) {
    console.error('Erreur lors de la sauvegarde de l\'insight philosophique:', error);
    throw error;
  }
};

/**
 * Réécrit un insight philosophique basé sur le feedback de l'utilisateur connecté
 * @param token - Clerk JWT token for authentication
 * @param feedback - Le feedback de l'utilisateur pour la réécriture
 * @returns Les nouvelles données d'insight générées
 */
export const rewriteInsight = async (token: string, feedback: string): Promise<InsightData> => {
  try {
    return await clerkApiService.request<InsightData>('/api/v1/insight/rewrite', {
      method: 'POST',
      token,
      body: JSON.stringify({
        feedback: feedback
      })
    });
  } catch (error) {
    console.error('Erreur lors de la réécriture de l\'insight philosophique:', error);
    throw error;
  }
};

/**
 * Récupère l'insight philosophique existant pour l'utilisateur connecté
 * @param token - Clerk JWT token for authentication
 * @returns Les données d'insight existantes ou null si aucun insight n'existe
 */
export const getInsight = async (token: string): Promise<InsightData | null> => {
  try {
    // Make a direct fetch call to avoid logging 404s as errors
    const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/v1/insight/get`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (response.status === 404) {
      // 404 is expected for users without insights - not an error
      console.log('Aucun insight existant pour cet utilisateur - c\'est normal pour un nouveau profil');
      return null;
    }

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }

    return await response.json();
  } catch (error: any) {
    // Only log and throw unexpected errors (not 404s)
    console.error('Erreur lors de la récupération de l\'insight philosophique:', error);
    throw error;
  }
};

/**
 * Régénère un insight philosophique pour l'utilisateur connecté
 * @param token - Clerk JWT token for authentication
 * @returns Les nouvelles données d'insight générées
 */
export const regenerateInsight = async (token: string): Promise<InsightData> => {
  try {
    return await clerkApiService.request<InsightData>('/api/v1/insight/regenerate', {
      method: 'POST',
      token,
      body: JSON.stringify({})
    });
  } catch (error) {
    console.error('Erreur lors de la régénération de l\'insight philosophique:', error);
    throw error;
  }
};

// Données simulées pour le développement et les tests
export const mockInsightData: InsightData = {
  preview: "Your life seems structured but contains hidden creative impulses...",
  full_text: "You present yourself as methodical and organized, but there's a part of you that craves creative expression and spontaneity. Your career choices reflect a tension between security and passion. The skills you've developed suggest someone preparing for stability, yet your interests hint at unfulfilled creative ambitions...",
  if_you_accept: "If you accept this truth, you might find that integrating your analytical skills with your creative instincts leads to innovations others cannot conceive."
};