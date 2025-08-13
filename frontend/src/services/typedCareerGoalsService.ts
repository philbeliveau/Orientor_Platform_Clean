/**
 * Example migration of CareerGoalsService to use new typed API methods
 * This demonstrates how to update existing services to use the enhanced ClerkApiService
 */

import { useClerkApi } from './api';
import {
  CareerGoal,
  CreateCareerGoalRequest,
  UpdateCareerGoalRequest,
  ApiResponse
} from '../types/api';

/**
 * Hook to fetch all career goals for the current user
 * Uses the new typed getCareerGoals method
 */
export function useGetCareerGoals() {
  const api = useClerkApi();
  
  const fetchCareerGoals = async (): Promise<CareerGoal[]> => {
    try {
      const response = await api.getCareerGoals();
      return response.data;
    } catch (error) {
      console.error('Failed to fetch career goals:', error);
      throw error;
    }
  };

  return { fetchCareerGoals };
}

/**
 * Hook to create a new career goal
 * Uses the new typed createCareerGoal method with validation
 */
export function useCreateCareerGoal() {
  const api = useClerkApi();
  
  const createGoal = async (goalData: CreateCareerGoalRequest): Promise<CareerGoal> => {
    try {
      // Input validation
      if (!goalData.title.trim()) {
        throw new Error('Goal title is required');
      }
      
      if (!goalData.target_date) {
        throw new Error('Target date is required');
      }

      const response = await api.createCareerGoal(goalData);
      
      console.log('✅ Career goal created successfully:', response.data);
      return response.data;
    } catch (error) {
      console.error('Failed to create career goal:', error);
      throw error;
    }
  };

  return { createGoal };
}

/**
 * Hook to update an existing career goal
 * Uses the new typed updateCareerGoal method
 */
export function useUpdateCareerGoal() {
  const api = useClerkApi();
  
  const updateGoal = async (
    goalId: number, 
    updates: UpdateCareerGoalRequest
  ): Promise<CareerGoal> => {
    try {
      if (goalId <= 0) {
        throw new Error('Invalid goal ID');
      }

      const response = await api.updateCareerGoal(goalId, updates);
      
      console.log('✅ Career goal updated successfully:', response.data);
      return response.data;
    } catch (error) {
      console.error('Failed to update career goal:', error);
      throw error;
    }
  };

  return { updateGoal };
}

/**
 * Hook to delete a career goal
 * Uses the new typed deleteCareerGoal method
 */
export function useDeleteCareerGoal() {
  const api = useClerkApi();
  
  const deleteGoal = async (goalId: number): Promise<boolean> => {
    try {
      if (goalId <= 0) {
        throw new Error('Invalid goal ID');
      }

      const response = await api.deleteCareerGoal(goalId);
      
      console.log('✅ Career goal deleted successfully');
      return response.data.success;
    } catch (error) {
      console.error('Failed to delete career goal:', error);
      throw error;
    }
  };

  return { deleteGoal };
}

/**
 * Hook to update goal progress
 * Demonstrates partial updates using typed methods
 */
export function useUpdateGoalProgress() {
  const api = useClerkApi();
  
  const updateProgress = async (
    goalId: number, 
    progressPercentage: number
  ): Promise<CareerGoal> => {
    try {
      if (goalId <= 0) {
        throw new Error('Invalid goal ID');
      }
      
      if (progressPercentage < 0 || progressPercentage > 100) {
        throw new Error('Progress percentage must be between 0 and 100');
      }

      const updateData: UpdateCareerGoalRequest = {
        progress_percentage: progressPercentage
      };

      const response = await api.updateCareerGoal(goalId, updateData);
      
      console.log(`✅ Goal progress updated to ${progressPercentage}%`);
      return response.data;
    } catch (error) {
      console.error('Failed to update goal progress:', error);
      throw error;
    }
  };

  return { updateProgress };
}

/**
 * Composite hook that combines all career goals functionality
 */
export function useCareerGoalsManager() {
  const { fetchCareerGoals } = useGetCareerGoals();
  const { createGoal } = useCreateCareerGoal();
  const { updateGoal } = useUpdateCareerGoal();
  const { deleteGoal } = useDeleteCareerGoal();
  const { updateProgress } = useUpdateGoalProgress();

  return {
    fetchCareerGoals,
    createGoal,
    updateGoal,
    deleteGoal,
    updateProgress
  };
}

/**
 * Migration guide for existing services:
 * 
 * BEFORE (old pattern):
 * ```typescript
 * const response = await fetch('/api/v1/career-goals', {
 *   headers: { Authorization: `Bearer ${token}` }
 * });
 * const data = await response.json();
 * ```
 * 
 * AFTER (new typed pattern):
 * ```typescript
 * const { fetchCareerGoals } = useGetCareerGoals();
 * const goals = await fetchCareerGoals(); // Fully typed and validated
 * ```
 * 
 * Benefits of migration:
 * 1. Type safety at compile time
 * 2. Runtime validation of API responses
 * 3. Consistent error handling
 * 4. Automatic Clerk authentication
 * 5. Better development experience with IntelliSense
 */