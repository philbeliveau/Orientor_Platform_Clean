import axios from 'axios';
import { getAuthHeader, endpoint } from '../utils/api';

// Type definitions
export interface InsightData {
  preview: string;
  full_text: string;
  if_you_accept: string;
}

/**
 * Génère un insight philosophique pour l'utilisateur connecté
 * @param getToken - Clerk getToken function for authentication
 * @returns Les données d'insight générées
 */
export const generateInsight = async (getToken: () => Promise<string | null>): Promise<InsightData> => {
  try {
    const headers = await getAuthHeader(getToken);
    const response = await axios.post<InsightData>(
      endpoint('/api/v1/insight/generate'),
      {},
      { headers }
    );
    return response.data;
  } catch (error) {
    console.error('Erreur lors de la génération de l\'insight philosophique:', error);
    throw error;
  }
};

/**
 * Sauvegarde un insight philosophique pour l'utilisateur connecté
 * @param getToken - Clerk getToken function for authentication
 * @param philosophicalText - Le texte philosophique à sauvegarder
 * @returns Le statut de succès
 */
export const saveInsight = async (getToken: () => Promise<string | null>, philosophicalText: string): Promise<{ success: boolean }> => {
  try {
    const headers = await getAuthHeader(getToken);
    const response = await axios.patch<{ success: boolean }>(
      endpoint('/api/v1/insight/save'),
      {
        philosophical_text: philosophicalText
      },
      { headers }
    );
    return response.data;
  } catch (error) {
    console.error('Erreur lors de la sauvegarde de l\'insight philosophique:', error);
    throw error;
  }
};

/**
 * Réécrit un insight philosophique basé sur le feedback de l'utilisateur connecté
 * @param getToken - Clerk getToken function for authentication
 * @param feedback - Le feedback de l'utilisateur pour la réécriture
 * @returns Les nouvelles données d'insight générées
 */
export const rewriteInsight = async (getToken: () => Promise<string | null>, feedback: string): Promise<InsightData> => {
  try {
    const headers = await getAuthHeader(getToken);
    const response = await axios.post<InsightData>(
      endpoint('/api/v1/insight/rewrite'),
      {
        feedback: feedback
      },
      { headers }
    );
    return response.data;
  } catch (error) {
    console.error('Erreur lors de la réécriture de l\'insight philosophique:', error);
    throw error;
  }
};

/**
 * Récupère l'insight philosophique existant pour l'utilisateur connecté
 * @param getToken - Clerk getToken function for authentication
 * @returns Les données d'insight existantes
 */
export const getInsight = async (getToken: () => Promise<string | null>): Promise<InsightData> => {
  try {
    const headers = await getAuthHeader(getToken);
    const response = await axios.get<InsightData>(
      endpoint('/api/v1/insight/get'),
      { headers }
    );
    return response.data;
  } catch (error) {
    console.error('Erreur lors de la récupération de l\'insight philosophique:', error);
    throw error;
  }
};

/**
 * Régénère un insight philosophique pour l'utilisateur connecté
 * @param getToken - Clerk getToken function for authentication
 * @returns Les nouvelles données d'insight générées
 */
export const regenerateInsight = async (getToken: () => Promise<string | null>): Promise<InsightData> => {
  try {
    const headers = await getAuthHeader(getToken);
    const response = await axios.post<InsightData>(
      endpoint('/api/v1/insight/regenerate'),
      {},
      { headers }
    );
    return response.data;
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