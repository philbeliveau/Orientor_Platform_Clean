/**
 * React hook that provides authenticated service calls using Clerk JWT tokens
 */

import { useClerkToken } from '@/utils/clerkAuth';
import AvatarService, { AvatarData, GenerateAvatarResponse } from '@/services/avatarService';
import { CareerGoalsService, CareerGoal } from '@/services/careerGoalsService';
import { courseAnalysisService, Course, CourseCreate } from '@/services/courseAnalysisService';

export const useAuthenticatedServices = () => {
  const { getAuthToken, isSignedIn, isLoaded } = useClerkToken();

  // Avatar Services
  const avatarServices = {
    getUserAvatar: async (): Promise<AvatarData> => {
      const token = await getAuthToken();
      return AvatarService.getUserAvatar(token);
    },

    generateAvatar: async (): Promise<GenerateAvatarResponse> => {
      const token = await getAuthToken();
      return AvatarService.generateAvatar(token);
    },

    hasAvatar: async (): Promise<boolean> => {
      const token = await getAuthToken();
      return AvatarService.hasAvatar(token);
    }
  };

  // Career Goals Services
  const careerGoalsServices = {
    getActiveCareerGoal: async () => {
      const token = await getAuthToken();
      return CareerGoalsService.getActiveCareerGoal(token);
    },

    setCareerGoalFromJob: async (job: {
      esco_id?: string;
      oasis_code?: string;
      title: string;
      description?: string;
      source?: string;
    }) => {
      const token = await getAuthToken();
      return CareerGoalsService.setCareerGoalFromJob(token, job);
    },

    getCareerProgression: async () => {
      const token = await getAuthToken();
      return CareerGoalsService.getCareerProgression(token);
    },

    updateCareerGoal: async (goalId: number, updates: {
      title?: string;
      description?: string;
      target_date?: string;
      is_active?: boolean;
    }) => {
      const token = await getAuthToken();
      return CareerGoalsService.updateCareerGoal(token, goalId, updates);
    },

    getAllCareerGoals: async (includeInactive = false) => {
      const token = await getAuthToken();
      return CareerGoalsService.getAllCareerGoals(token, includeInactive);
    },

    completeMilestone: async (goalId: number, milestoneId: number) => {
      const token = await getAuthToken();
      return CareerGoalsService.completeMilestone(token, goalId, milestoneId);
    }
  };

  // Course Services
  const courseServices = {
    getCourses: async (filters?: {
      semester?: string;
      year?: number;
      subject_category?: string;
    }) => {
      const token = await getAuthToken();
      return courseAnalysisService.getCourses(token, filters);
    },

    getCourse: async (courseId: number) => {
      const token = await getAuthToken();
      return courseAnalysisService.getCourse(courseId, token);
    },

    createCourse: async (courseData: CourseCreate) => {
      const token = await getAuthToken();
      return courseAnalysisService.createCourse(courseData, token);
    },

    updateCourse: async (courseId: number, updateData: Partial<CourseCreate>) => {
      const token = await getAuthToken();
      return courseAnalysisService.updateCourse(courseId, updateData, token);
    },

    deleteCourse: async (courseId: number) => {
      const token = await getAuthToken();
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
    getAuthToken
  };
};

export default useAuthenticatedServices;