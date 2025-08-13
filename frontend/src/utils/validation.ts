// Runtime validation utilities for API responses

/**
 * Validates that an API response contains all required fields
 * @param response The response object to validate
 * @param requiredFields Array of field names that must be present
 * @throws Error if any required field is missing
 * @returns The validated response object cast to type T
 */
export function validateApiResponse<T>(
  response: any,
  requiredFields: (keyof T)[]
): T {
  if (!response || typeof response !== 'object') {
    throw new Error('Invalid response: Expected an object');
  }

  const missingFields: string[] = [];
  
  for (const field of requiredFields) {
    if (!(field in response)) {
      missingFields.push(String(field));
    }
  }

  if (missingFields.length > 0) {
    throw new Error(`Missing required fields: ${missingFields.join(', ')}`);
  }

  return response as T;
}

/**
 * Validates that a response is a properly formatted API response
 * @param response The response to validate
 * @throws Error if response doesn't match ApiResponse format
 */
export function validateApiResponseFormat<T>(response: any): { data: T; message?: string; error?: string } {
  if (!response || typeof response !== 'object') {
    throw new Error('Invalid API response format: Expected an object');
  }

  // For responses that already have the wrapper format
  if ('data' in response) {
    return response;
  }

  // For responses that are directly the data (common in current implementation)
  return { data: response };
}

/**
 * Validates required fields for Career Goal objects
 * More flexible validation to handle API variations
 */
export function validateCareerGoal(obj: any) {
  if (!obj || typeof obj !== 'object') {
    throw new Error('Invalid career goal: Expected an object');
  }
  
  // Require only essential fields, make others optional
  const requiredFields = ['id', 'title'];
  const missingFields = requiredFields.filter(field => !(field in obj));
  
  if (missingFields.length > 0) {
    throw new Error(`Missing required career goal fields: ${missingFields.join(', ')}`);
  }
  
  return obj;
}

/**
 * Validates required fields for Avatar Data objects
 * More flexible validation for avatar responses
 */
export function validateAvatarData(obj: any) {
  if (!obj || typeof obj !== 'object') {
    throw new Error('Invalid avatar data: Expected an object');
  }
  
  // Avatar data can have various formats, be flexible
  return obj;
}

/**
 * Validates required fields for User Profile objects
 * Flexible validation for user profile data
 */
export function validateUserProfile(obj: any) {
  if (!obj || typeof obj !== 'object') {
    throw new Error('Invalid user profile: Expected an object');
  }
  
  // User profiles might have different formats - be very flexible
  // Accept any object that resembles a user profile
  if (!('id' in obj) && !('email' in obj) && !('user_id' in obj) && !('clerk_id' in obj) && !('name' in obj)) {
    console.warn('User profile missing typical fields, but allowing:', obj);
  }
  
  return obj;
}

/**
 * Validates required fields for Job Recommendation objects
 * Flexible validation for job recommendation data
 */
export function validateJobRecommendation(obj: any) {
  if (!obj || typeof obj !== 'object') {
    throw new Error('Invalid job recommendation: Expected an object');
  }
  
  // Job recommendations might not have id field - be flexible
  // Accept objects that have either id, or score, or metadata
  if (!('id' in obj) && !('score' in obj) && !('metadata' in obj)) {
    console.warn('Job recommendation missing typical fields, but allowing:', obj);
  }
  
  return obj;
}

/**
 * Validates required fields for Holland Results objects
 * Flexible validation for Holland test results
 */
export function validateHollandResults(obj: any) {
  if (!obj || typeof obj !== 'object') {
    throw new Error('Invalid Holland results: Expected an object');
  }
  
  // Holland results might not have id field - accept any object with score data
  // Accept objects that have scores or any recognizable Holland test fields
  if (!('id' in obj) && !('scores' in obj) && !('realistic' in obj) && !('investigative' in obj) && !('artistic' in obj)) {
    console.warn('Holland results missing typical fields, but allowing:', obj);
  }
  
  return obj;
}

/**
 * Validates required fields for Skills Tree Data objects
 */
export function validateSkillsTreeData(obj: any) {
  return validateApiResponse(obj, ['tree_data']);
}

/**
 * Validates required fields for User Note objects
 * Flexible validation for user note data
 */
export function validateUserNote(obj: any) {
  if (!obj || typeof obj !== 'object') {
    throw new Error('Invalid user note: Expected an object');
  }
  
  // Only require id and title as essential fields
  if (!('id' in obj) || !('title' in obj)) {
    throw new Error('Invalid user note: Missing required fields id or title');
  }
  
  return obj;
}

/**
 * Validates required fields for Compatible Peer objects
 * More flexible validation for peer data
 */
export function validateCompatiblePeer(obj: any) {
  if (!obj || typeof obj !== 'object') {
    throw new Error('Invalid peer object: Expected an object');
  }
  
  // Only require id - other fields are optional
  if (!('id' in obj)) {
    throw new Error('Invalid peer object: Missing required field "id"');
  }
  
  return obj;
}

/**
 * Validates required fields for Onboarding Status objects
 * Expects the standardized onboarding router format
 */
export function validateOnboardingStatus(obj: any) {
  if (!obj || typeof obj !== 'object') {
    throw new Error('Invalid onboarding status: Expected an object');
  }
  
  // Validate standardized onboarding router response format
  if (
    typeof obj.onboarding_completed === 'boolean' &&
    typeof obj.has_started === 'boolean' &&
    typeof obj.is_complete === 'boolean' &&
    typeof obj.message === 'string'
  ) {
    return obj; // Valid format, return as-is
  }
  
  throw new Error('Invalid onboarding status format: Expected onboarding router schema with onboarding_completed, has_started, is_complete, and message fields');
}

/**
 * Type guard to check if an object is an API error
 */
export function isApiError(obj: any): obj is { status: number; message: string; details?: string } {
  return obj && 
         typeof obj === 'object' && 
         typeof obj.status === 'number' && 
         typeof obj.message === 'string';
}

/**
 * Safely extracts data from an API response, handling both wrapped and unwrapped formats
 */
export function extractResponseData<T>(response: any): T {
  // If response has a 'data' field, use it
  if (response && typeof response === 'object' && 'data' in response) {
    return response.data;
  }
  
  // Otherwise, assume the response itself is the data
  return response;
}

/**
 * Validates an array response and each item in the array
 * Handles cases where response might not be an array
 */
export function validateArrayResponse<T>(
  response: any,
  itemValidator: (item: any) => T
): T[] {
  const data = extractResponseData(response);
  
  // Handle null, undefined, or non-array responses gracefully
  if (!data) {
    console.warn('API returned null/undefined data, returning empty array');
    return [];
  }
  
  if (!Array.isArray(data)) {
    console.warn('API response is not an array, wrapping single item:', data);
    // If it's a single object, wrap it in an array
    if (typeof data === 'object') {
      try {
        return [itemValidator(data)];
      } catch (error) {
        console.error('Failed to validate single item response:', error);
        return [];
      }
    }
    return [];
  }

  return data.map((item, index) => {
    try {
      return itemValidator(item);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown validation error';
      console.warn(`Invalid item at index ${index}: ${errorMessage}`, item);
      // Skip invalid items instead of throwing
      return null;
    }
  }).filter(item => item !== null) as T[];
}