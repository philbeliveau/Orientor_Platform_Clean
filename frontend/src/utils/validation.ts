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
 */
export function validateCareerGoal(obj: any) {
  return validateApiResponse(obj, ['id', 'title', 'target_date', 'progress_percentage']);
}

/**
 * Validates required fields for Avatar Data objects
 */
export function validateAvatarData(obj: any) {
  return validateApiResponse(obj, ['success']);
}

/**
 * Validates required fields for User Profile objects
 */
export function validateUserProfile(obj: any) {
  return validateApiResponse(obj, ['id', 'email', 'created_at', 'updated_at']);
}

/**
 * Validates required fields for Job Recommendation objects
 */
export function validateJobRecommendation(obj: any) {
  return validateApiResponse(obj, ['id', 'title']);
}

/**
 * Validates required fields for Holland Results objects
 */
export function validateHollandResults(obj: any) {
  return validateApiResponse(obj, [
    'id', 'user_id', 'realistic_score', 'investigative_score', 
    'artistic_score', 'social_score', 'enterprising_score', 
    'conventional_score', 'holland_code', 'created_at'
  ]);
}

/**
 * Validates required fields for Skills Tree Data objects
 */
export function validateSkillsTreeData(obj: any) {
  return validateApiResponse(obj, ['tree_data']);
}

/**
 * Validates required fields for User Note objects
 */
export function validateUserNote(obj: any) {
  return validateApiResponse(obj, ['id', 'title', 'content', 'created_at', 'updated_at', 'user_id']);
}

/**
 * Validates required fields for Compatible Peer objects
 */
export function validateCompatiblePeer(obj: any) {
  return validateApiResponse(obj, ['id', 'user_id', 'compatibility_score']);
}

/**
 * Validates required fields for Onboarding Status objects
 */
export function validateOnboardingStatus(obj: any) {
  return validateApiResponse(obj, ['completed', 'user_id']);
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
 */
export function validateArrayResponse<T>(
  response: any,
  itemValidator: (item: any) => T
): T[] {
  const data = extractResponseData(response);
  
  if (!Array.isArray(data)) {
    throw new Error('Expected an array response');
  }

  return data.map((item, index) => {
    try {
      return itemValidator(item);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown validation error';
      throw new Error(`Invalid item at index ${index}: ${errorMessage}`);
    }
  });
}