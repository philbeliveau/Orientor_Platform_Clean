import axios from 'axios';
import { getAuthHeader, endpoint } from '../utils/api';

// Type definitions
export interface Recommendation {
  id?: number;
  oasis_code: string;
  label: string;
  description?: string;
  main_duties?: string;
  role_creativity?: number;
  role_leadership?: number;
  role_digital_literacy?: number;
  role_critical_thinking?: number;
  role_problem_solving?: number;
  analytical_thinking?: number;
  attention_to_detail?: number;
  collaboration?: number;
  adaptability?: number;
  independence?: number;
  evaluation?: number;
  decision_making?: number;
  stress_tolerance?: number;
  saved_at?: string;
  skill_comparison?: SkillsComparison;
  notes?: Note[];
  all_fields?: Record<string, string>;
  personal_analysis?: string;
  entry_qualifications?: string;
  suggested_improvements?: string;
}

export interface SkillComparison {
  user_skill?: number;
  role_skill?: number;
}

export interface SkillsComparison {
  creativity: SkillComparison;
  leadership: SkillComparison;
  digital_literacy: SkillComparison;
  critical_thinking: SkillComparison;
  problem_solving: SkillComparison;
}

export interface UserSkills {
  creativity: number;
  leadership: number;
  digital_literacy: number;
  critical_thinking: number;
  problem_solving: number;
  analytical_thinking: number;
  attention_to_detail: number;
  collaboration: number;
  adaptability: number;
  independence: number;
  evaluation: number;
  decision_making: number;
  stress_tolerance: number;
}

export interface Note {
  id: number;
  content: string;
  saved_recommendation_id?: number;
  created_at: string;
  updated_at: string;
}

// Saved Job types (from tree exploration)
export interface SavedJob {
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
  graphsage_skills?: Array<{
    skill_id: string;
    skill_name: string;
    relevance_score: number;
    description: string;
  }>;
}

export interface NoteCreate {
  content: string;
  saved_recommendation_id?: number;
}

export interface NoteUpdate {
  content: string;
}


// Fetch saved recommendations
export const fetchSavedRecommendations = async (getToken: () => Promise<string | null>): Promise<Recommendation[]> => {
  try {
    const headers = await getAuthHeader(getToken);
    console.log('Fetching saved recommendations from:', endpoint('/careers/saved'));
    const response = await axios.get<Recommendation[]>(endpoint('/careers/saved'), { headers });
    console.log('API response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error fetching saved recommendations:', error);
    throw error;
  }
};

// Save a recommendation
export const saveRecommendation = async (getToken: () => Promise<string | null>, recommendation: Recommendation): Promise<Recommendation> => {
  try {
    const headers = await getAuthHeader(getToken);
    const response = await axios.post<Recommendation>(
      endpoint('/space/recommendations'),
      recommendation,
      { headers }
    );
    return response.data;
  } catch (error) {
    console.error('Error saving recommendation:', error);
    throw error;
  }
};

// Save a recommendation with LLM analysis
export const saveRecommendationWithLLMAnalysis = async (
  getToken: () => Promise<string | null>,
  recommendation: Recommendation,
  userProfile: {
    skills: UserSkills;
    experience?: string;
    education?: string;
    interests?: string;
  }
): Promise<Recommendation> => {
  try {
    // Préparer les données pour l'analyse LLM
    const analysisInput: LLMAnalysisInput = {
      oasis_code: recommendation.oasis_code,
      job_description: recommendation.description || '',
      user_profile: userProfile
    };

    // Générer l'analyse LLM
    const analysisResult = await generateLLMAnalysis(analysisInput);

    // Ajouter les résultats de l'analyse à la recommandation
    const enrichedRecommendation: Recommendation = {
      ...recommendation,
      personal_analysis: analysisResult.personal_analysis,
      entry_qualifications: analysisResult.entry_qualifications,
      suggested_improvements: analysisResult.suggested_improvements
    };

    // Sauvegarder la recommandation enrichie
    return await saveRecommendation(getToken, enrichedRecommendation);
  } catch (error) {
    console.error('Error saving recommendation with LLM analysis:', error);
    throw error;
  }
};

// Delete a saved recommendation
export const deleteRecommendation = async (getToken: () => Promise<string | null>, recommendationId: number | string): Promise<void> => {
  try {
    const headers = await getAuthHeader(getToken);
    await axios.delete(
      endpoint(`/space/recommendations/${recommendationId}`),
      { headers }
    );
  } catch (error) {
    console.error('Error deleting recommendation:', error);
    throw error;
  }
};

// Fetch notes for a recommendation
export const fetchNotes = async (getToken: () => Promise<string | null>, recommendationId: number): Promise<Note[]> => {
  try {
    const headers = await getAuthHeader(getToken);
    const response = await axios.get<Note[]>(
      endpoint(`/space/notes?saved_recommendation_id=${recommendationId}`),
      { headers }
    );
    return response.data;
  } catch (error) {
    console.error('Error fetching notes:', error);
    throw error;
  }
};

// Fetch all user notes (not tied to specific recommendations)
// Cache for deduplicating requests
let notesCache: {
  data: Note[] | null;
  timestamp: number;
  pendingRequest: Promise<Note[]> | null;
} = {
  data: null,
  timestamp: 0,
  pendingRequest: null
};

export const fetchAllUserNotes = async (getToken: () => Promise<string | null>): Promise<Note[]> => {
  // Return cached data if it's fresh (5 seconds)
  if (notesCache.data && Date.now() - notesCache.timestamp < 5000) {
    return notesCache.data;
  }

  // Return pending request if one exists
  if (notesCache.pendingRequest) {
    return notesCache.pendingRequest;
  }

  try {
    // Create new pending request
    const headers = await getAuthHeader(getToken);
    notesCache.pendingRequest = axios.get<Note[]>(
      endpoint('/space/notes'),
      { headers }
    ).then(response => {
      notesCache.data = response.data;
      notesCache.timestamp = Date.now();
      return response.data;
    }).finally(() => {
      notesCache.pendingRequest = null;
    });

    return await notesCache.pendingRequest;
  } catch (error) {
    console.error('Error fetching all user notes:', error);
    throw error;
  }
};

// Create a standalone note (not tied to a recommendation)
export const createStandaloneNote = async (getToken: () => Promise<string | null>, content: string): Promise<Note> => {
  try {
    const headers = await getAuthHeader(getToken);
    const response = await axios.post<Note>(
      endpoint('/space/notes'),
      { content },
      { headers }
    );
    return response.data;
  } catch (error) {
    console.error('Error creating standalone note:', error);
    throw error;
  }
};

// Create a new note
export const createNote = async (getToken: () => Promise<string | null>, note: NoteCreate): Promise<Note> => {
  try {
    const headers = await getAuthHeader(getToken);
    const response = await axios.post<Note>(
      endpoint('/space/notes'),
      note,
      { headers }
    );
    return response.data;
  } catch (error) {
    console.error('Error creating note:', error);
    throw error;
  }
};

// Update a note
export const updateNote = async (getToken: () => Promise<string | null>, noteId: number, updates: NoteUpdate): Promise<Note> => {
  try {
    const headers = await getAuthHeader(getToken);
    const response = await axios.put<Note>(
      endpoint(`/space/notes/${noteId}`),
      updates,
      { headers }
    );
    return response.data;
  } catch (error) {
    console.error('Error updating note:', error);
    throw error;
  }
};

// Delete a note
export const deleteNote = async (getToken: () => Promise<string | null>, noteId: number): Promise<void> => {
  try {
    const headers = await getAuthHeader(getToken);
    await axios.delete(
      endpoint(`/space/notes/${noteId}`),
      { headers }
    );
  } catch (error) {
    console.error('Error deleting note:', error);
    throw error;
  }
};

// Interface pour les données d'entrée de l'analyse LLM
export interface LLMAnalysisInput {
  oasis_code: string;
  job_description: string;
  user_profile: {
    skills: UserSkills;
    experience?: string;
    education?: string;
    interests?: string;
  };
}

// Interface pour les résultats de l'analyse LLM
export interface LLMAnalysisResult {
  personal_analysis: string;
  entry_qualifications: string;
  suggested_improvements: string;
}

// Generate LLM analysis for a recommendation by recommendation ID
export const generateLLMAnalysisForRecommendation = async (getToken: () => Promise<string | null>, recommendationId: number): Promise<Recommendation> => {
  try {
    const headers = await getAuthHeader(getToken);
    const response = await axios.post<Recommendation>(
      endpoint(`/space/recommendations/${recommendationId}/generate-analysis`),
      {},
      { headers }
    );
    return response.data;
  } catch (error) {
    console.error('Error generating LLM analysis:', error);
    throw error;
  }
};

// Legacy function kept for compatibility - now shows deprecation warning
export const generateLLMAnalysis = async (input: LLMAnalysisInput): Promise<LLMAnalysisResult> => {
  console.warn('generateLLMAnalysis is deprecated. Use generateLLMAnalysisForRecommendation instead.');
  
  try {
    // For backward compatibility, return empty analysis
    return {
      personal_analysis: "Please use the new analysis generation method.",
      entry_qualifications: "Please use the new analysis generation method.",
      suggested_improvements: "Please use the new analysis generation method."
    };
  } catch (error) {
    console.error('Error in legacy generateLLMAnalysis:', error);
    return {
      personal_analysis: "Error generating analysis.",
      entry_qualifications: "Error generating analysis.",
      suggested_improvements: "Error generating analysis."
    };
  }
};

// Get user skills
export const getUserSkills = async (getToken: () => Promise<string | null>): Promise<UserSkills> => {
  try {
    const headers = await getAuthHeader(getToken);
    const response = await axios.get<UserSkills>(
      endpoint('/space/skills'),
      { headers }
    );
    return response.data;
  } catch (error) {
    console.error('Error fetching skills:', error);
    throw error;
  }
};

// Update user skills
export const updateUserSkills = async (getToken: () => Promise<string | null>, skills: UserSkills): Promise<UserSkills> => {
  try {
    const headers = await getAuthHeader(getToken);
    const response = await axios.put<UserSkills>(
      endpoint('/space/skills'),
      skills,
      { headers }
    );
    return response.data;
  } catch (error) {
    console.error('Error updating skills:', error);
    throw error;
  }
};

// Get skill comparison data
export const getSkillComparison = async (getToken: () => Promise<string | null>, oasisCode: string): Promise<any> => {
  try {
    const headers = await getAuthHeader(getToken);
    const response = await axios.get(
      endpoint(`/space/recommendations/${oasisCode}/skill-comparison`),
      { headers }
    );
    return response.data;
  } catch (error) {
    console.error('Error fetching skill comparison:', error);
    throw error;
  }
};

// ===== SAVED JOBS FUNCTIONALITY =====

// Fetch saved jobs from tree exploration
export const fetchSavedJobs = async (getToken: () => Promise<string | null>): Promise<SavedJob[]> => {
  try {
    const headers = await getAuthHeader(getToken);
    const response = await axios.get<{jobs: SavedJob[], total: number}>(
      endpoint('/jobs/saved'),
      { headers }
    );
    return response.data.jobs;
  } catch (error) {
    console.error('Error fetching saved jobs:', error);
    throw error;
  }
};

// Delete a saved job
export const deleteSavedJob = async (getToken: () => Promise<string | null>, jobId: number): Promise<void> => {
  try {
    const headers = await getAuthHeader(getToken);
    await axios.delete(
      endpoint(`/jobs/${jobId}`),
      { headers }
    );
  } catch (error) {
    console.error('Error deleting saved job:', error);
    throw error;
  }
};

// Get job details from ESCO
export const getJobDetails = async (getToken: () => Promise<string | null>, escoId: string): Promise<any> => {
  try {
    const headers = await getAuthHeader(getToken);
    const response = await axios.get(
      endpoint(`/jobs/${escoId}/details`),
      { headers }
    );
    return response.data;
  } catch (error) {
    console.error('Error fetching job details:', error);
    throw error;
  }
};

// ===== CAREER FIT ANALYSIS =====

export interface SkillMatch {
  skill_name: string;
  user_level?: number;
  required_level?: number;
  match_percentage: number;
}

export interface GapAnalysis {
  skill_gaps: Array<{
    skill: string;
    current: number;
    required: number;
    gap: number;
  }>;
  strength_areas: string[];
  improvement_areas: string[];
}

export interface CareerFitResponse {
  fit_score: number;
  skill_match: Record<string, SkillMatch>;
  gap_analysis: GapAnalysis;
  recommendations: string[];
}

// Analyze career fit for a job
export const analyzeCareerFit = async (getToken: () => Promise<string | null>, jobId: string, jobSource: 'esco' | 'oasis'): Promise<CareerFitResponse> => {
  try {
    const headers = await getAuthHeader(getToken);
    const response = await axios.post<CareerFitResponse>(
      endpoint('/careers/fit-analysis'),
      {
        job_id: jobId,
        job_source: jobSource
      },
      { headers }
    );
    return response.data;
  } catch (error) {
    console.error('Error analyzing career fit:', error);
    throw error;
  }
};

// Cleanup fake test jobs
export const cleanupTestJobs = async (getToken: () => Promise<string | null>): Promise<{success: boolean, message: string, deleted_count: number}> => {
  try {
    const headers = await getAuthHeader(getToken);
    const response = await axios.delete<{success: boolean, message: string, deleted_count: number}>(
      endpoint('/careers/cleanup-test-jobs'),
      { headers }
    );
    return response.data;
  } catch (error) {
    console.error('Error cleaning up test jobs:', error);
    throw error;
  }
};
