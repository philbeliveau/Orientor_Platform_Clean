import axios from 'axios';
import { getAuthHeader, endpoint } from '../utils/api';

// Define TreeNode interface for the career tree
export interface CareerTreeNode {
  id: string;
  label: string;
  type: string;
  level: number;
  actions?: string[];
  children?: CareerTreeNode[];
}

interface CareerTreeResponse {
  tree: CareerTreeNode;
}

// Service to interact with the career tree API endpoint
export const careerTreeService = {
  /**
   * Generate a career exploration tree based on the provided profile
   * @param getToken - Clerk getToken function for authentication
   * @param profile - The student profile (interests, traits, etc.)
   * @returns The generated career tree
   */
  async generateCareerTree(getToken: () => Promise<string | null>, profile: string): Promise<CareerTreeNode> {
    console.log(`careerTreeService: Generating tree`);
    console.log(`careerTreeService: Profile length: ${profile.length} characters`);
    
    try {
      // Get authentication headers using Clerk
      const headers = await getAuthHeader(getToken);
      console.log(`careerTreeService: Auth headers ${Object.keys(headers).length ? 'configured' : 'missing'}`);
      
      console.log(`careerTreeService: Making POST request to tree endpoint`);
      console.time('careerTreeService:apiCall');
      
      // Use the existing /tree endpoint with proper auth headers
      const response = await axios.post<CareerTreeResponse>(
        endpoint('/tree'), 
        { profile },
        { headers }
      );
      
      console.timeEnd('careerTreeService:apiCall');
      console.log(`careerTreeService: Request successful - Status: ${response.status}`);
      
      if (!response.data || !response.data.tree) {
        console.error('careerTreeService: Response missing tree data:', response.data);
        throw new Error('API response missing tree data structure');
      }
      
      // Basic validation of tree structure
      const tree = response.data.tree;
      if (!tree.id || !tree.type || !tree.children || !Array.isArray(tree.children)) {
        console.error('careerTreeService: Invalid tree structure received:', tree);
        throw new Error('API returned invalid tree structure');
      }
      
      console.log(`careerTreeService: Tree generated successfully with root ID: ${tree.id}`);
      console.log(`careerTreeService: Tree has ${tree.children?.length || 0} level 1 children`);
      
      return tree;
    } catch (error: any) {
      // Enhance error logging
      console.error('careerTreeService: Error generating career tree:', error);
      
      if (error.response) {
        // The request was made and the server responded with a status code outside of 2xx
        console.error(`careerTreeService: Server error - Status: ${error.response.status}`);
        console.error('careerTreeService: Response headers:', error.response.headers);
        console.error('careerTreeService: Response data:', error.response.data);
        
        // Add specific error handling for common status codes
        if (error.response.status === 401) {
          console.error('careerTreeService: Authentication error - not authorized');
        } else if (error.response.status === 400) {
          console.error('careerTreeService: Bad request - check payload format');
        } else if (error.response.status === 500) {
          console.error('careerTreeService: Server error - check backend logs');
        }
      } else if (error.request) {
        // The request was made but no response was received
        console.error('careerTreeService: No response received from server');
        console.error('careerTreeService: Request details:', error.request);
      } else {
        // Something happened in setting up the request
        console.error('careerTreeService: Request setup error:', error.message);
      }
      
      // Forward the error for handling in the component
      throw error;
    }
  },
}; 