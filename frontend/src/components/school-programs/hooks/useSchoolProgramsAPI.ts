/**
 * Custom hook for School Programs API interactions
 */

import { useCallback } from 'react';
import { useAuth } from '@clerk/nextjs';
import { toast } from 'react-hot-toast';
import { Program, SearchFilters, SearchResults, UserProgramInteraction, SaveProgramRequest } from '../types';
import { getAuthHeader, endpoint } from '@/services/api';

export const useSchoolProgramsAPI = () => {
  const { getToken } = useAuth();

  const searchPrograms = useCallback(async (filters: SearchFilters, page: number = 1): Promise<SearchResults> => {
    try {
      const headers = await getAuthHeader(getToken);
      const response = await fetch(endpoint('/school-programs/search'), {
        method: 'POST',
        headers,
        body: JSON.stringify({
          ...filters,
          pagination: { page, limit: 20 }
        }),
      });

      if (!response.ok) {
        throw new Error('Search failed');
      }

      return await response.json();
    } catch (error) {
      toast.error("Unable to search programs. Please try again.");
      throw error;
    }
  }, []);

  const getProgramDetails = useCallback(async (programId: string): Promise<Program> => {
    try {
      const headers = await getAuthHeader(getToken);
      const response = await fetch(endpoint(`/school-programs/programs/${programId}`), {
        headers,
      });

      if (!response.ok) {
        throw new Error('Failed to fetch program details');
      }

      return await response.json();
    } catch (error) {
      toast.error("Unable to load program details.");
      throw error;
    }
  }, []);

  const saveProgram = useCallback(async (programId: string, notes?: string): Promise<void> => {
    try {
      const headers = await getAuthHeader(getToken);
      const response = await fetch(endpoint('/school-programs/users/saved-programs'), {
        method: 'POST',
        headers,
        body: JSON.stringify({
          program_id: programId,
          notes: notes,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to save program');
      }

      toast.success("Program saved to your list!");
    } catch (error) {
      toast.error("Unable to save program. Please try again.");
    }
  }, []);

  const recordInteraction = useCallback(async (programId: string, type: string, metadata?: any): Promise<void> => {
    try {
      const headers = await getAuthHeader(getToken);
      await fetch(endpoint('/school-programs/users/interactions'), {
        method: 'POST',
        headers,
        body: JSON.stringify({
          program_id: programId,
          interaction_type: type,
          metadata: metadata || {},
        }),
      });
    } catch (error) {
      // Silent fail for analytics
      console.warn('Failed to record interaction:', error);
    }
  }, []);

  const getSavedPrograms = useCallback(async (): Promise<Program[]> => {
    try {
      const headers = await getAuthHeader(getToken);
      const response = await fetch(endpoint('/school-programs/users/saved-programs'), {
        headers,
      });

      if (!response.ok) {
        throw new Error('Failed to fetch saved programs');
      }

      return await response.json();
    } catch (error) {
      toast.error("Unable to load saved programs.");
      throw error;
    }
  }, []);

  const removeSavedProgram = useCallback(async (programId: string): Promise<void> => {
    try {
      const headers = await getAuthHeader(getToken);
      const response = await fetch(endpoint(`/school-programs/users/saved-programs/${programId}`), {
        method: 'DELETE',
        headers,
      });

      if (!response.ok) {
        throw new Error('Failed to remove saved program');
      }

      toast.success("Program removed from your saved list.");
    } catch (error) {
      toast.error("Unable to remove program. Please try again.");
    }
  }, []);

  const getAvailableFilters = useCallback(async () => {
    try {
      const headers = await getAuthHeader(getToken);
      const response = await fetch(endpoint('/school-programs/filters'), {
        headers,
      });

      if (!response.ok) {
        throw new Error('Failed to fetch filters');
      }

      return await response.json();
    } catch (error) {
      console.warn('Failed to fetch filters:', error);
      return {
        program_types: [],
        levels: [],
        provinces: [],
        languages: [
          { value: 'en', label: 'English', count: 0 },
          { value: 'fr', label: 'French', count: 0 }
        ]
      };
    }
  }, []);

  return {
    searchPrograms,
    getProgramDetails,
    saveProgram,
    recordInteraction,
    getSavedPrograms,
    removeSavedProgram,
    getAvailableFilters,
  };
};