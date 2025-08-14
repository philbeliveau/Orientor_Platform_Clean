/**
 * React hook that provides authenticated service calls using Clerk JWT tokens
 */

import { useClerkApi } from '@/services/clerkApi';
import AvatarService, { AvatarData, GenerateAvatarResponse } from '@/services/avatarService';
import { CareerGoalsService, CareerGoal } from '@/services/careerGoalsService';
import { courseAnalysisService, Course, CourseCreate } from '@/services/courseAnalysisService';
import { useAuth } from '@clerk/nextjs';

export const useAuthenticatedServices = () => {
  const { isSignedIn, isLoaded, getToken } = useAuth();
  const apiService = useClerkApi();

  // Avatar Services
  const avatarServices = {
    getUserAvatar: async (): Promise<AvatarData> => {
      return AvatarService.getUserAvatar(apiService);
    },

    generateAvatar: async (): Promise<GenerateAvatarResponse> => {
      return AvatarService.generateAvatar(apiService);
    },

    hasAvatar: async (): Promise<boolean> => {
      return AvatarService.hasAvatar(apiService);
    }
  };

  // Career Goals Services - TODO: Update these to use ClerkApiService pattern when refactoring career goals
  const careerGoalsServices = {
    getActiveCareerGoal: async () => {
      const { LegacyCareerGoalsService } = await import('@/services/careerGoalsService');
      return LegacyCareerGoalsService.getActiveCareerGoal(getToken);
    },

    setCareerGoalFromJob: async (job: {
      esco_id?: string;
      oasis_code?: string;
      title: string;
      description?: string;
      source?: string;
    }) => {
      const { LegacyCareerGoalsService } = await import('@/services/careerGoalsService');
      return LegacyCareerGoalsService.setCareerGoalFromJob(getToken, job);
    },

    getCareerProgression: async () => {
      const token = await getToken();
      return CareerGoalsService.getCareerProgression(token);
    },

    updateCareerGoal: async (goalId: number, updates: {
      title?: string;
      description?: string;
      target_date?: string;
      is_active?: boolean;
    }) => {
      const token = await getToken();
      return CareerGoalsService.updateCareerGoal(token, goalId, updates);
    },

    getAllCareerGoals: async (includeInactive = false) => {
      const token = await getToken();
      return CareerGoalsService.getAllCareerGoals(token, includeInactive);
    },

    completeMilestone: async (goalId: number, milestoneId: number) => {
      const token = await getToken();
      return CareerGoalsService.completeMilestone(token, goalId, milestoneId);
    }
  };

  // Course Services - TODO: Update these to use ClerkApiService pattern when refactoring course analysis
  const courseServices = {
    getCourses: async (filters?: {
      semester?: string;
      year?: number;
      subject_category?: string;
    }) => {
      const token = await getToken();
      return courseAnalysisService.getCourses(token, filters);
    },

    getCourse: async (courseId: number) => {
      const token = await getToken();
      return courseAnalysisService.getCourse(courseId, token);
    },

    createCourse: async (courseData: CourseCreate) => {
      const token = await getToken();
      return courseAnalysisService.createCourse(courseData, token);
    },

    updateCourse: async (courseId: number, updateData: Partial<CourseCreate>) => {
      const token = await getToken();
      return courseAnalysisService.updateCourse(courseId, updateData, token);
    },

    deleteCourse: async (courseId: number) => {
      const token = await getToken();
      return courseAnalysisService.deleteCourse(courseId, token);
    }
  };

  return {
    // Authentication state
    isSignedIn,
    isLoaded,

    // Service collections
    avatar: avatarServices,
    careerGoals: careerGoalsServices,
    courses: courseServices,

    // Direct token access if needed
    getToken
  };
};

export default useAuthenticatedServices;