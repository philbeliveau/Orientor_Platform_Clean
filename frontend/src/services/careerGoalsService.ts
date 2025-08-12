import { SkillNode, TimelineTier } from '@/components/career/TimelineVisualization';
import { useClerkApi, ClerkApiService } from './clerkApi';
import { useAuth } from '@clerk/nextjs';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Types for API responses
export interface CareerGoal {
  id: number;
  user_id: number;
  esco_occupation_id?: string;
  oasis_code?: string;
  title: string;
  description?: string;
  target_date: string;
  is_active: boolean;
  progress_percentage: number;
  created_at: string;
  updated_at: string;
  achieved_at?: string;
  source?: string;
  milestones_count?: number;
  completed_milestones?: number;
}

interface GraphSageScore {
  skill_id: string;
  confidence_score: number;
  tier_level: number;
  relationships: string[];
  metadata: {
    last_updated: string;
    model_version: string;
    training_accuracy: number;
  };
}

interface CareerProgressionResponse {
  user_id: string;
  tiers: TimelineTier[];
  goals: CareerGoal[];
  graphsage_scores: GraphSageScore[];
  last_updated: string;
}


// Career Goals Service
export class CareerGoalsService {
  /**
   * Set a career goal from any job card using ClerkApiService
   */
  static async setCareerGoalFromJob(apiService: ClerkApiService, job: {
    esco_id?: string;
    oasis_code?: string;
    title: string;
    description?: string;
    source?: string;
  }): Promise<{ goal: CareerGoal; timeline: any }> {
    console.log('[CareerGoals] 🎯 Setting career goal from job:', job.title);
    
    try {
      const requestBody = {
        esco_occupation_id: job.esco_id,
        oasis_code: job.oasis_code,
        title: job.title,
        description: job.description,
        source: job.source,
        target_date: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString()
      };
      
      console.log('[CareerGoals] 📦 Request body:', requestBody);

      const data = await apiService.post<{ goal: CareerGoal; timeline: any }>('/career-goals', requestBody);
      
      console.log('[CareerGoals] ✅ Successfully set career goal:', data);
      
      // Clear cache since we just updated the goal
      this.activeGoalCache = null;
      
      return data;
    } catch (error) {
      console.error('[CareerGoals] ❌ Error setting career goal:', {
        message: error.message,
        job: job.title
      });
      throw error;
    }
  }

  /**
   * Get active career goal with progression
   */
  private static activeGoalCache: {
    data: {
      goal: CareerGoal | null;
      progression: any;
      milestones: any[];
    };
    timestamp: number;
  } | null = null;

  private static pendingRequest: Promise<any> | null = null;

  static async getActiveCareerGoal(apiService: ClerkApiService): Promise<{
    goal: CareerGoal | null;
    progression: any;
    milestones: any[];
  }> {
    console.log('[CareerGoals] 🎯 Getting active career goal...');
    
    // Return cached data if it's fresh (less than 5 seconds old)
    if (this.activeGoalCache && Date.now() - this.activeGoalCache.timestamp < 5000) {
      console.log('[CareerGoals] 📦 Using cached data');
      return this.activeGoalCache.data;
    }

    // If there's already a pending request, return its promise
    if (this.pendingRequest) {
      console.log('[CareerGoals] ⏳ Waiting for pending request');
      return this.pendingRequest;
    }

    try {
      console.log('[CareerGoals] 🌐 Making API request...');

      // Create and store the pending request
      this.pendingRequest = apiService.get<{
        goal: CareerGoal | null;
        progression: any;
        milestones: any[];
      }>('/career-goals/active').then(data => {
        console.log('[CareerGoals] ✅ Successfully fetched career goal data');
        // Update cache
        this.activeGoalCache = {
          data,
          timestamp: Date.now()
        };
        return data;
      }).catch(error => {
        console.error('[CareerGoals] ❌ Error fetching active career goal:', {
          message: error.message,
          cacheAvailable: !!this.activeGoalCache
        });
        
        // Return cached data if available, otherwise empty state
        const fallbackData = this.activeGoalCache?.data || { goal: null, progression: null, milestones: [] };
        console.log('[CareerGoals] 🔄 Using fallback data:', fallbackData);
        return fallbackData;
      }).finally(() => {
        // Clear the pending request
        this.pendingRequest = null;
      });

      return await this.pendingRequest;
    } catch (error) {
      console.error('[CareerGoals] ❌ Critical error in getActiveCareerGoal:', {
        message: error.message
      });
      this.pendingRequest = null;
      const fallbackData = this.activeGoalCache?.data || { goal: null, progression: null, milestones: [] };
      console.log('[CareerGoals] 🔄 Using final fallback data:', fallbackData);
      return fallbackData;
    }
  }

  /**
   * Fetch user's career progression with GraphSage scores
   */
  static async getCareerProgression(apiService: ClerkApiService): Promise<CareerProgressionResponse> {
    try {
      // First try to get active goal's progression
      const { goal, progression } = await this.getActiveCareerGoal(apiService);
      
      if (goal && progression) {
        return progression;
      }
      
      // Fallback to generic progression endpoint if available
      const data = await apiService.get<CareerProgressionResponse>('/api/v1/career/progression');
      return data;
    } catch (error) {
      console.error('Error fetching career progression:', error);
      
      // Return mock data for development
      return this.getMockCareerProgression();
    }
  }

  /**
   * Update GraphSage confidence scores for skills
   * TODO: Phase 2 - Convert remaining methods to use ClerkApiService
   */
  static async updateGraphSageScores(token: string, skillIds: string[]): Promise<GraphSageScore[]> {
    try {
      const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      };
        
      const response = await fetch(endpoint('/api/v1/career/graphsage/update'), {
        method: 'POST',
        headers,
        body: JSON.stringify({ skill_ids: skillIds }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.scores;
    } catch (error) {
      console.error('Error updating GraphSage scores:', error);
      throw error;
    }
  }

  /**
   * Update career goal
   */
  static async updateCareerGoal(token: string, goalId: number, updates: {
    title?: string;
    description?: string;
    target_date?: string;
    is_active?: boolean;
  }): Promise<CareerGoal> {
    try {
      const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      };
        
      const response = await fetch(endpoint(`/api/v1/career-goals/${goalId}`), {
        method: 'PUT',
        headers,
        body: JSON.stringify(updates),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error updating career goal:', error);
      throw error;
    }
  }

  /**
   * Complete a milestone
   */
  static async completeMilestone(token: string, goalId: number, milestoneId: number): Promise<{
    message: string;
    xp_awarded: number;
    goal_progress: number;
    goal_achieved: boolean;
  }> {
    try {
      const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      };
        
      const response = await fetch(
        endpoint(`/api/v1/career-goals/${goalId}/milestones/${milestoneId}/complete`),
        {
          method: 'POST',
          headers,
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error completing milestone:', error);
      throw error;
    }
  }

  /**
   * Get all career goals
   */
  static async getAllCareerGoals(token: string, includeInactive = false): Promise<CareerGoal[]> {
    try {
      const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      };
        
      const response = await fetch(
        endpoint(`/api/v1/career-goals?include_inactive=${includeInactive}`),
        {
          method: 'GET',
          headers,
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching career goals:', error);
      return [];
    }
  }

  /**
   * Get skill recommendations based on GraphSage analysis
   */
  static async getSkillRecommendations(token: string, currentSkillIds: string[]): Promise<SkillNode[]> {
    try {
      const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      };
        
      const response = await fetch(endpoint('/api/v1/career/recommendations/skills'), {
        method: 'POST',
        headers,
        body: JSON.stringify({ current_skills: currentSkillIds }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.recommendations;
    } catch (error) {
      console.error('Error getting skill recommendations:', error);
      throw error;
    }
  }

  /**
   * Analyze skill relationships using GraphSage
   */
  static async analyzeSkillRelationships(token: string, skillIds: string[]): Promise<{
    relationships: Array<{
      source: string;
      target: string;
      strength: number;
      confidence: number;
    }>;
    clusters: Array<{
      id: string;
      skills: string[];
      theme: string;
    }>;
  }> {
    try {
      const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      };
        
      const response = await fetch(endpoint('/api/v1/career/graphsage/relationships'), {
        method: 'POST',
        headers,
        body: JSON.stringify({ skill_ids: skillIds }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error analyzing skill relationships:', error);
      throw error;
    }
  }

  /**
   * Get career path optimization suggestions
   */
  static async getCareerPathOptimization(token: string, currentTier: number): Promise<{
    recommendations: Array<{
      skill_id: string;
      priority_score: number;
      expected_impact: number;
      estimated_months: number;
      reasoning: string;
    }>;
    timeline_adjustments: Array<{
      tier_id: string;
      suggested_duration: number;
      current_duration: number;
      reasoning: string;
    }>;
  }> {
    try {
      const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      };
        
      const response = await fetch(endpoint(`/api/v1/career/optimization/${currentTier}`), {
        method: 'GET',
        headers,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error getting career path optimization:', error);
      throw error;
    }
  }

  /**
   * Mock data for development
   */
  private static getMockCareerProgression(): CareerProgressionResponse {
    return {
      user_id: 'mock-user-123',
      tiers: [
        {
          id: 'tier-1',
          title: 'Foundation & Exploration',
          level: 1,
          timeline_months: 6,
          confidence_threshold: 0.8,
          skills: [
            {
              id: 'skill-1-1',
              label: 'Programming Fundamentals',
              confidence_score: 0.92,
              type: 'skill',
              level: 1,
              relationships: ['skill-1-2', 'skill-2-1'],
              metadata: {
                description: 'Learn core programming concepts and syntax',
                estimated_months: 3,
                prerequisites: [],
                learning_resources: ['Online courses', 'Practice projects']
              }
            },
            {
              id: 'skill-1-2',
              label: 'Problem Solving',
              confidence_score: 0.85,
              type: 'skill',
              level: 1,
              relationships: ['skill-1-1', 'skill-2-3'],
              metadata: {
                description: 'Develop analytical thinking and debugging skills',
                estimated_months: 2,
                prerequisites: [],
                learning_resources: ['Algorithm challenges', 'Code reviews']
              }
            }
          ]
        }
      ],
      goals: [
        {
          id: 1,
          user_id: 1,
          title: 'Master Frontend Development',
          description: 'Become proficient in React and modern frontend technologies',
          target_date: '2024-12-31',
          is_active: true,
          progress_percentage: 65,
          created_at: '2024-01-15T00:00:00Z',
          updated_at: '2024-06-20T00:00:00Z'
        }
      ],
      graphsage_scores: [
        {
          skill_id: 'skill-1-1',
          confidence_score: 0.92,
          tier_level: 1,
          relationships: ['skill-1-2', 'skill-2-1'],
          metadata: {
            last_updated: '2024-06-20T10:30:00Z',
            model_version: 'graphsage-v2.1',
            training_accuracy: 0.94
          }
        }
      ],
      last_updated: '2024-06-20T10:30:00Z'
    };
  }
}

// Convenience hook for React components using ClerkApiService
export const useCareerGoalsService = () => {
  const apiService = useClerkApi();
  
  return {
    setCareerGoalFromJob: (job: {
      esco_id?: string;
      oasis_code?: string;
      title: string;
      description?: string;
      source?: string;
    }) => CareerGoalsService.setCareerGoalFromJob(apiService, job),
    getActiveCareerGoal: () => CareerGoalsService.getActiveCareerGoal(apiService),
    getCareerProgression: () => CareerGoalsService.getCareerProgression(apiService),
    // Note: Other methods would need similar refactoring to use apiService
    // For now, they maintain their original token-based interface
  };
};

// Legacy support - wrapper functions that maintain backward compatibility
export const LegacyCareerGoalsService = {
  async setCareerGoalFromJob(getToken: () => Promise<string>, job: {
    esco_id?: string;
    oasis_code?: string;
    title: string;
    description?: string;
    source?: string;
  }): Promise<{ goal: CareerGoal; timeline: any }> {
    const token = await getToken();
    const apiService = new ClerkApiService(() => Promise.resolve(token));
    return CareerGoalsService.setCareerGoalFromJob(apiService, job);
  },
  
  async getActiveCareerGoal(getToken: () => Promise<string>): Promise<{
    goal: CareerGoal | null;
    progression: any;
    milestones: any[];
  }> {
    const token = await getToken();
    const apiService = new ClerkApiService(() => Promise.resolve(token));
    return CareerGoalsService.getActiveCareerGoal(apiService);
  },
};

// Export types for use in components
export type { GraphSageScore, CareerProgressionResponse };
