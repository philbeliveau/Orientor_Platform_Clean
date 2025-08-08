import axios from 'axios';
import { getAuthHeader, endpoint } from '../utils/api';


export interface ProgramRecommendation {
  id: string;
  program_name: string;
  institution: string;
  institution_type: string;
  program_code?: string;
  duration?: string;
  admission_requirements: string[];
  match_score: number;
  cost_estimate?: number;
  location: {
    city?: string;
    province?: string;
    campus_type?: string;
  };
  intake_dates: string[];
  relevance_explanation: string;
  career_outcomes: string[];
  website_url?: string;
  contact_info: {
    email?: string;
    phone?: string;
  };
}

export interface ProgramRecommendationsResponse {
  recommendations: ProgramRecommendation[];
  total: number;
  goal_info: {
    goal_id: number;
    notes?: string;
    target_date?: string;
    set_at?: string;
    job_title: string;
    esco_id: string;
  };
}

export interface Institution {
  id: string;
  name: string;
  type: string;
  city: string;
  province: string;
  website: string;
  programs_count: number;
}

export const getProgramRecommendationsForGoal = async (getToken: () => Promise<string | null>, goalId: number, limit: number = 10): Promise<ProgramRecommendationsResponse> => {
  try {
    const headers = await getAuthHeader(getToken);
    const response = await axios.get(
      endpoint(`/program-recommendations/career-goal/${goalId}`),
      {
        headers,
        params: { limit }
      }
    );

    return response.data;
  } catch (error: any) {
    console.error('Error fetching program recommendations:', error);
    throw new Error(error.response?.data?.detail || 'Failed to fetch program recommendations');
  }
};

export const saveProgramRecommendation = async (getToken: () => Promise<string | null>, goalId: number, programId: string): Promise<void> => {
  try {
    const headers = await getAuthHeader(getToken);
    await axios.post(
      endpoint(`/program-recommendations/career-goal/${goalId}/save`),
      {},
      {
        headers,
        params: { program_id: programId }
      }
    );
  } catch (error: any) {
    console.error('Error saving program recommendation:', error);
    throw new Error(error.response?.data?.detail || 'Failed to save program recommendation');
  }
};

export const getSavedProgramRecommendations = async (getToken: () => Promise<string | null>, goalId: number): Promise<ProgramRecommendation[]> => {
  try {
    const headers = await getAuthHeader(getToken);
    const response = await axios.get(
      endpoint(`/program-recommendations/career-goal/${goalId}/saved`),
      {
        headers
      }
    );

    return response.data.saved_recommendations;
  } catch (error: any) {
    console.error('Error fetching saved program recommendations:', error);
    throw new Error(error.response?.data?.detail || 'Failed to fetch saved recommendations');
  }
};

export const getAvailableInstitutions = async (getToken: () => Promise<string | null>, institutionType?: string, region: string = 'Quebec'): Promise<Institution[]> => {
  try {
    const headers = await getAuthHeader(getToken);
    const response = await axios.get(
      endpoint('/program-recommendations/institutions'),
      {
        headers,
        params: { 
          institution_type: institutionType,
          region 
        }
      }
    );

    return response.data.institutions;
  } catch (error: any) {
    console.error('Error fetching institutions:', error);
    throw new Error(error.response?.data?.detail || 'Failed to fetch institutions');
  }
};