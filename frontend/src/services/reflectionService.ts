import { clerkApiService } from './api';

// Helper function to make authenticated requests using consistent Clerk API service
async function makeAuthenticatedRequest<T>(
  endpoint: string, 
  options?: RequestInit,
  getToken?: () => Promise<string | null>
): Promise<T> {
  try {
    if (!getToken) {
      throw new Error('No token function provided');
    }

    const token = await getToken();
    
    if (!token) {
      // Redirect to sign-in if no token
      if (typeof window !== 'undefined') {
        window.location.href = '/sign-in';
      }
      throw new Error('No authentication token available');
    }

    // Validate token format - ensure it's a proper JWT
    if (token.startsWith('sess_')) {
      console.error('[ReflectionService] ❌ Got session token instead of JWT:', token.substring(0, 20));
      throw new Error('Invalid token type - please refresh and try again');
    }
    
    if (!token.startsWith('eyJ')) {
      console.error('[ReflectionService] ❌ Invalid JWT format:', token.substring(0, 20));
      throw new Error('Invalid JWT token format - please refresh and try again');
    }

    console.log('[ReflectionService] ✅ Using JWT token:', token.substring(0, 30) + '...');

    // Use the consistent clerkApiService for requests
    return await clerkApiService.request<T>(endpoint, {
      ...options,
      token,
    });

  } catch (error: any) {
    console.error('[ReflectionService] API request failed:', error);
    
    // Provide user-friendly error messages for common issues
    if (error?.message?.includes('500') && error?.message?.includes('Database')) {
      throw new Error('Unable to save your response due to a technical issue. Please try again in a moment.');
    } else if (error?.message?.includes('401')) {
      if (typeof window !== 'undefined') {
        window.location.href = '/sign-in';
      }
      throw new Error('Authentication required - redirecting to sign-in');
    }
    
    throw error;
  }
}

class ReflectionService {
  private baseUrl = '/api/v1/reflection';

  /**
   * Récupère toutes les questions de réflexion
   */
  async getQuestions(getToken?: () => Promise<string | null>): Promise<ReflectionQuestion[]> {
    try {
      return makeAuthenticatedRequest<ReflectionQuestion[]>(`${this.baseUrl}/questions`, undefined, getToken);
    } catch (error) {
      console.error('Erreur lors de la récupération des questions:', error);
      throw error;
    }
  }

  /**
   * Récupère les réponses de l'utilisateur actuel
   */
  async getCurrentUserResponses(getToken?: () => Promise<string | null>): Promise<ReflectionResponse[]> {
    try {
      return makeAuthenticatedRequest<ReflectionResponse[]>(`${this.baseUrl}/responses`, undefined, getToken);
    } catch (error) {
      console.error('Erreur lors de la récupération des réponses:', error);
      throw error;
    }
  }

  /**
   * Récupère les réponses d'un utilisateur spécifique
   */
  async getUserResponses(userId: number, getToken?: () => Promise<string | null>): Promise<ReflectionResponse[]> {
    try {
      return makeAuthenticatedRequest<ReflectionResponse[]>(`${this.baseUrl}/responses/${userId}`, undefined, getToken);
    } catch (error) {
      console.error('Erreur lors de la récupération des réponses utilisateur:', error);
      throw error;
    }
  }

  /**
   * Sauvegarde ou met à jour une réponse
   */
  async saveResponse(responseData: ReflectionResponseCreate, getToken?: () => Promise<string | null>): Promise<ReflectionResponse> {
    try {
      return makeAuthenticatedRequest<ReflectionResponse>(`${this.baseUrl}/responses`, {
        method: 'POST',
        body: JSON.stringify(responseData),
      }, getToken);
    } catch (error) {
      console.error('Erreur lors de la sauvegarde de la réponse:', error);
      throw error;
    }
  }

  /**
   * Met à jour une réponse existante
   */
  async updateResponse(responseId: number, responseData: ReflectionResponseUpdate, getToken?: () => Promise<string | null>): Promise<ReflectionResponse> {
    try {
      return makeAuthenticatedRequest<ReflectionResponse>(`${this.baseUrl}/responses/${responseId}`, {
        method: 'PUT',
        body: JSON.stringify(responseData),
      }, getToken);
    } catch (error) {
      console.error('Erreur lors de la mise à jour de la réponse:', error);
      throw error;
    }
  }

  /**
   * Sauvegarde plusieurs réponses en lot
   */
  async saveResponsesBatch(batchData: ReflectionResponseBatch, getToken?: () => Promise<string | null>): Promise<ReflectionResponse[]> {
    try {
      return makeAuthenticatedRequest<ReflectionResponse[]>(`${this.baseUrl}/responses/batch`, {
        method: 'POST',
        body: JSON.stringify(batchData),
      }, getToken);
    } catch (error) {
      console.error('Erreur lors de la sauvegarde en lot:', error);
      throw error;
    }
  }

  /**
   * Supprime une réponse
   */
  async deleteResponse(responseId: number, getToken?: () => Promise<string | null>): Promise<void> {
    try {
      await makeAuthenticatedRequest<void>(`${this.baseUrl}/responses/${responseId}`, {
        method: 'DELETE',
      }, getToken);
    } catch (error) {
      console.error('Erreur lors de la suppression de la réponse:', error);
      throw error;
    }
  }

  /**
   * Combine les questions avec les réponses existantes
   */
  async getQuestionsWithResponses(getToken?: () => Promise<string | null>): Promise<(ReflectionQuestion & { response?: ReflectionResponse })[]> {
    try {
      const [questions, responses] = await Promise.all([
        this.getQuestions(getToken),
        this.getCurrentUserResponses(getToken)
      ]);

      // Vérifier que responses est bien un tableau
      const responseArray = Array.isArray(responses) ? responses : [];

      // Créer un map des réponses par question_id
      const responsesMap = new Map<number, ReflectionResponse>();
      responseArray.forEach(response => {
        responsesMap.set(response.question_id, response);
      });

      // Combiner les questions avec leurs réponses
      return questions.map(question => ({
        ...question,
        response: responsesMap.get(question.id)
      }));
    } catch (error) {
      console.error('Erreur lors de la récupération des questions avec réponses:', error);
      throw error;
    }
  }
}

const reflectionService = new ReflectionService();
export default reflectionService;