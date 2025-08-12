/**
 * Example typed Avatar Service demonstrating Phase 2 implementation
 * Shows how to use typed API methods for avatar management
 */

import { useClerkApi } from './api';
import {
  AvatarData,
  UpdateAvatarRequest,
  ApiResponse
} from '../types/api';

// Enhanced Avatar Service using typed API methods
export class TypedAvatarService {
  
  /**
   * Fetch current user's avatar data
   * Uses the new typed getAvatarData method
   */
  static useGetAvatarData() {
    const api = useClerkApi();
    
    const fetchAvatarData = async (): Promise<AvatarData> => {
      try {
        const response = await api.getAvatarData();
        
        // The response is already validated by the API service
        console.log('✅ Avatar data fetched successfully:', response.data);
        return response.data;
      } catch (error) {
        console.error('Failed to fetch avatar data:', error);
        throw error;
      }
    };

    return { fetchAvatarData };
  }

  /**
   * Update user's avatar data
   * Uses the new typed updateAvatarData method with validation
   */
  static useUpdateAvatarData() {
    const api = useClerkApi();
    
    const updateAvatar = async (avatarData: UpdateAvatarRequest): Promise<AvatarData> => {
      try {
        // Input validation
        if (avatarData.avatar_name && avatarData.avatar_name.trim().length < 2) {
          throw new Error('Avatar name must be at least 2 characters long');
        }
        
        if (avatarData.avatar_description && avatarData.avatar_description.length > 500) {
          throw new Error('Avatar description cannot exceed 500 characters');
        }

        if (avatarData.avatar_image_url && !isValidUrl(avatarData.avatar_image_url)) {
          throw new Error('Invalid avatar image URL');
        }

        const response = await api.updateAvatarData(avatarData);
        
        console.log('✅ Avatar updated successfully:', response.data);
        return response.data;
      } catch (error) {
        console.error('Failed to update avatar:', error);
        throw error;
      }
    };

    return { updateAvatar };
  }

  /**
   * Update only avatar name
   * Demonstrates partial updates using typed methods
   */
  static useUpdateAvatarName() {
    const api = useClerkApi();
    
    const updateName = async (avatarName: string): Promise<AvatarData> => {
      try {
        if (!avatarName.trim()) {
          throw new Error('Avatar name cannot be empty');
        }
        
        if (avatarName.length > 100) {
          throw new Error('Avatar name cannot exceed 100 characters');
        }

        const updateData: UpdateAvatarRequest = {
          avatar_name: avatarName.trim()
        };

        const response = await api.updateAvatarData(updateData);
        
        console.log(`✅ Avatar name updated to: ${avatarName}`);
        return response.data;
      } catch (error) {
        console.error('Failed to update avatar name:', error);
        throw error;
      }
    };

    return { updateName };
  }

  /**
   * Update only avatar description
   */
  static useUpdateAvatarDescription() {
    const api = useClerkApi();
    
    const updateDescription = async (description: string): Promise<AvatarData> => {
      try {
        if (description.length > 500) {
          throw new Error('Description cannot exceed 500 characters');
        }

        const updateData: UpdateAvatarRequest = {
          avatar_description: description
        };

        const response = await api.updateAvatarData(updateData);
        
        console.log('✅ Avatar description updated successfully');
        return response.data;
      } catch (error) {
        console.error('Failed to update avatar description:', error);
        throw error;
      }
    };

    return { updateDescription };
  }

  /**
   * Update avatar image URL
   */
  static useUpdateAvatarImage() {
    const api = useClerkApi();
    
    const updateImage = async (imageUrl: string): Promise<AvatarData> => {
      try {
        if (!isValidUrl(imageUrl)) {
          throw new Error('Invalid image URL format');
        }

        const updateData: UpdateAvatarRequest = {
          avatar_image_url: imageUrl
        };

        const response = await api.updateAvatarData(updateData);
        
        console.log('✅ Avatar image updated successfully');
        return response.data;
      } catch (error) {
        console.error('Failed to update avatar image:', error);
        throw error;
      }
    };

    return { updateImage };
  }
}

/**
 * Complete Avatar Manager hook for React components
 */
export function useAvatarManager() {
  const { fetchAvatarData } = TypedAvatarService.useGetAvatarData();
  const { updateAvatar } = TypedAvatarService.useUpdateAvatarData();
  const { updateName } = TypedAvatarService.useUpdateAvatarName();
  const { updateDescription } = TypedAvatarService.useUpdateAvatarDescription();
  const { updateImage } = TypedAvatarService.useUpdateAvatarImage();

  return {
    fetchAvatarData,
    updateAvatar,
    updateName,
    updateDescription,
    updateImage
  };
}

/**
 * Utility function to validate URLs
 */
function isValidUrl(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

/**
 * Example React component usage:
 * 
 * ```typescript
 * import { useAvatarManager } from '@/services/typedAvatarService';
 * 
 * export function AvatarEditor() {
 *   const { fetchAvatarData, updateName, updateDescription } = useAvatarManager();
 *   const [avatar, setAvatar] = useState<AvatarData | null>(null);
 *   
 *   useEffect(() => {
 *     fetchAvatarData().then(setAvatar);
 *   }, []);
 *   
 *   const handleNameUpdate = async (newName: string) => {
 *     try {
 *       const updatedAvatar = await updateName(newName);
 *       setAvatar(updatedAvatar);
 *     } catch (error) {
 *       // Handle error with proper typing
 *       console.error('Update failed:', error);
 *     }
 *   };
 *   
 *   return (
 *     <div>
 *       <h2>{avatar?.avatar_name}</h2>
 *       <p>{avatar?.avatar_description}</p>
 *       // ... rest of component
 *     </div>
 *   );
 * }
 * ```
 */