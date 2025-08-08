import axios from 'axios';
import { getAuthHeader, endpoint } from '../utils/api';

export interface CompetenceNode {
  id: string;
  skill_id: string;
  skill_label: string;
  challenge: string;
  xp_reward: number;
  visible: boolean;
  revealed: boolean;
  state: 'locked' | 'completed';
  notes: string;
}

export interface CompetenceTreeData {
  nodes: CompetenceNode[];
  edges: { source: string; target: string }[];
  graph_id: string;
}

export const generateCompetenceTree = async (getToken: () => Promise<string | null>, userId: number): Promise<{ graph_id: string }> => {
  try {
    console.log(`Génération d'un arbre de compétences pour l'utilisateur ${userId}`);
    
    // Get authentication headers using Clerk
    const headers = await getAuthHeader(getToken);
    if (!Object.keys(headers).length) {
      throw new Error('Authentication required');
    }
    
    const response = await axios.post(
      endpoint('/api/v1/competence-tree/generate'),
      {},
      {
        headers,
        timeout: 180000, // 3 minute timeout
        params: {
          max_depth: 3,
          max_nodes: 20
        }
      }
    );
    
    console.log('Réponse de génération:', response.data);
    
    // Validate response structure
    if (!response.data?.graph_id) {
      throw new Error('Invalid response: missing graph_id');
    }
    
    return response.data as { graph_id: string };
  } catch (error: any) {
    console.error('Erreur lors de la génération de l\'arbre de compétences:', error);
    
    // Handle specific error types
    if (error.code === 'ECONNABORTED') {
      throw new Error('Tree generation timed out. The process is complex - please try again.');
    } else if (error.response?.status === 408) {
      throw new Error('Tree generation is taking longer than expected. Please try again.');
    } else if (error.response?.status === 500) {
      const errorMsg = error.response?.data?.detail || 'Internal server error occurred during tree generation';
      throw new Error(errorMsg);
    } else if (error.response?.status === 401) {
      throw new Error('Authentication failed. Please log in again.');
    } else {
      throw new Error(error.message || 'An unexpected error occurred during tree generation');
    }
  }
};

export const getCompetenceTree = async (getToken: () => Promise<string | null>, graphId: string): Promise<CompetenceTreeData> => {
  try {
    // Get authentication headers using Clerk
    const headers = await getAuthHeader(getToken);
    if (!Object.keys(headers).length) {
      throw new Error('Authentication required');
    }
    
    const response = await axios.get(endpoint(`/api/v1/competence-tree/${graphId}`), {
      headers
    });
    return response.data as CompetenceTreeData;
  } catch (error) {
    console.error('Erreur lors de la récupération de l\'arbre de compétences:', error);
    throw error;
  }
};

export const completeChallenge = async (getToken: () => Promise<string | null>, nodeId: string, userId: number): Promise<{ success: boolean }> => {
  try {
    console.log(`Complétion du défi ${nodeId} pour l'utilisateur ${userId}`);
    
    // Get authentication headers using Clerk
    const headers = await getAuthHeader(getToken);
    if (!Object.keys(headers).length) {
      throw new Error('Authentication required');
    }
    
    const response = await axios.patch(
      endpoint(`/api/v1/competence-tree/node/${nodeId}/complete?user_id=${userId}`),
      {},
      { headers }
    );
    console.log('Réponse de complétion:', response.data);
    return response.data as { success: boolean };
  } catch (error) {
    console.error('Erreur lors de la complétion du défi:', error);
    throw error;
  }
};

// Job saving functionality
export interface SaveJobRequest {
  esco_id: string;
  job_title: string;
  skills_required?: string[];
  discovery_source?: string;
  tree_graph_id?: string;
  relevance_score?: number;
  metadata?: Record<string, any>;
}

export interface SavedJobResponse {
  id: number;
  user_id: number;
  esco_id: string;
  job_title: string;
  skills_required: string[];
  discovery_source: string;
  tree_graph_id?: string;
  relevance_score?: number;
  saved_at: string;
  metadata: Record<string, any>;
  already_saved: boolean;
}

export const saveJobFromTree = async (getToken: () => Promise<string | null>, jobData: SaveJobRequest): Promise<SavedJobResponse> => {
  try {
    // Get authentication headers using Clerk
    const headers = await getAuthHeader(getToken);
    if (!Object.keys(headers).length) {
      throw new Error('Authentication required');
    }
    
    const response = await axios.post(
      endpoint('/api/v1/jobs/save'),
      jobData,
      { headers }
    );
    
    console.log('Job saved successfully:', response.data);
    return response.data as SavedJobResponse;
  } catch (error: any) {
    console.error('Error saving job:', error);
    if (error.response?.status === 401) {
      throw new Error('Authentication failed. Please log in again.');
    }
    throw new Error(error.response?.data?.detail || 'Failed to save job');
  }
};

export const getSavedJobs = async (getToken: () => Promise<string | null>): Promise<SavedJobResponse[]> => {
  try {
    // Get authentication headers using Clerk
    const headers = await getAuthHeader(getToken);
    if (!Object.keys(headers).length) {
      throw new Error('Authentication required');
    }
    
    const response = await axios.get(
      endpoint('/api/v1/jobs/saved'),
      { headers }
    );
    
    return response.data.jobs as SavedJobResponse[];
  } catch (error: any) {
    console.error('Error fetching saved jobs:', error);
    throw new Error(error.response?.data?.detail || 'Failed to fetch saved jobs');
  }
};

export const generateTreeFromAnchors = async (
  getToken: () => Promise<string | null>,
  anchorSkills: string[]
): Promise<{ graph_id: string }> => {
  try {
    // Get authentication headers using Clerk
    const headers = await getAuthHeader(getToken);
    if (!Object.keys(headers).length) {
      throw new Error('Authentication required');
    }
    
    const response = await axios.post(
      endpoint('/api/v1/competence-tree/generate-from-anchors'),
      {
        anchor_skills: anchorSkills,
        max_depth: 3,
        max_nodes: 50,
        include_occupations: true
      },
      {
        headers,
        timeout: 60000 // 1 minute timeout
      }
    );
    
    return response.data;
  } catch (error: any) {
    console.error('Error generating tree from anchors:', error);
    throw error;
  }
};