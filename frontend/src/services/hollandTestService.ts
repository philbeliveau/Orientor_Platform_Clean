import axios from 'axios';
import { clerkApiService } from './api';  // Import Clerk-authenticated API service

// Types basés sur les modèles backend
export interface TestMetadata {
  id: number;
  title: string;
  description: string;
  seo_code: string;
  video_url?: string;
  image_url?: string;
  chapter_count: number;
  question_count: number;
}

export interface Choice {
  id: number;
  title: string;
  question_id: number;
  sort_idx: number;
  r: number;
  i: number;
  a: number;
  s: number;
  e: number;
  c: number;
}

export interface Question {
  id: number;
  title: string;
  chapter_number: number;
  sort_idx: number;
  choices: Choice[];
}

export interface AnswerRequest {
  attempt_id: string;
  question_id: number;
  choice_id: number;
}

export interface ScoreResponse {
  r_score: number;
  i_score: number;
  a_score: number;
  s_score: number;
  e_score: number;
  c_score: number;
  top_3_code: string;
  personality_description?: string;
}

// URL de base de l'API
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const HOLLAND_TEST_API = `${API_BASE_URL}/api/v1/tests/holland`;

// Service pour le test Holland with Clerk authentication
const hollandTestService = {
  // Récupérer les métadonnées du test
  getTestMetadata: async (token: string): Promise<TestMetadata> => {
    try {
      return await clerkApiService.request<TestMetadata>(`/api/v1/tests/holland`, {
        method: 'GET',
        token
      });
    } catch (error) {
      console.error('Erreur lors de la récupération des métadonnées du test:', error);
      throw error;
    }
  },

  // Récupérer toutes les questions du test
  getQuestions: async (token: string): Promise<Question[]> => {
    try {
      return await clerkApiService.request<Question[]>(`/api/v1/tests/holland/questions`, {
        method: 'GET',
        token
      });
    } catch (error) {
      console.error('Erreur lors de la récupération des questions:', error);
      throw error;
    }
  },

  // Enregistrer une réponse
  saveAnswer: async (token: string, answerData: AnswerRequest): Promise<{ message: string; id: string }> => {
    try {
      return await clerkApiService.request<{ message: string; id: string }>(`/api/v1/tests/holland/answer`, {
        method: 'POST',
        token,
        body: JSON.stringify(answerData)
      });
    } catch (error) {
      console.error('Erreur lors de l\'enregistrement de la réponse:', error);
      throw error;
    }
  },

  // Récupérer le score du test
  getScore: async (token: string, attemptId: string, includeDescription: boolean = true): Promise<ScoreResponse> => {
    try {
      return await clerkApiService.request<ScoreResponse>(
        `/api/v1/tests/holland/score/${attemptId}?include_description=${includeDescription}`,
        {
          method: 'GET',
          token
        }
      );
    } catch (error) {
      console.error('Erreur lors de la récupération du score:', error);
      throw error;
    }
  },

  // Récupérer les derniers résultats du test Holland pour l'utilisateur connecté
  getUserLatestResults: async (token: string): Promise<ScoreResponse> => {
    try {
      return await clerkApiService.request<ScoreResponse>(`/api/v1/tests/holland/user-results`, {
        method: 'GET',
        token
      });
    } catch (error) {
      console.error('Erreur lors de la récupération des résultats du test:', error);
      throw error;
    }
  },

  // Récupérer la description personnalisée du profil basée sur les résultats RIASEC
  getProfileDescription: async (token: string, regenerate: boolean = false): Promise<string> => {
    try {
      const response = await clerkApiService.request<{ description: string }>(
        `/api/v1/tests/holland/profile-description?regenerate=${regenerate}`,
        {
          method: 'GET',
          token
        }
      );
      return response.description;
    } catch (error) {
      console.error('Erreur lors de la récupération de la description du profil:', error);
      throw error;
    }
  },
  
  // Récupérer la description personnalisée pour un utilisateur spécifique
  getUserProfileDescription: async (token: string, userId: string, regenerate: boolean = false): Promise<string> => {
    try {
      const response = await clerkApiService.request<{ description: string }>(
        `/api/v1/tests/holland/profile-description/${userId}?regenerate=${regenerate}`,
        {
          method: 'GET',
          token
        }
      );
      return response.description;
    } catch (error) {
      console.error('Erreur lors de la récupération de la description du profil:', error);
      throw error;
    }
  },

  // Générer un nouvel ID de tentative
  generateAttemptId: (): string => {
    return crypto.randomUUID ? crypto.randomUUID() :
      'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
      });
  }
};

export default hollandTestService;