/**
 * Safe array processing utilities to prevent forEach and array operation errors
 * Implements defensive programming patterns for API response handling
 */

/**
 * Safely processes an unknown value as an array
 * @param data - Unknown data that should be an array
 * @param itemValidator - Optional validator function for each item
 * @returns Array of validated items
 */
export function ensureArray<T>(
  data: unknown,
  itemValidator?: (item: unknown) => T
): T[] {
  // Handle null/undefined
  if (!data) {
    console.warn('[safeArrayProcessing] Received null/undefined data, returning empty array');
    return [];
  }

  // Handle already valid arrays
  if (Array.isArray(data)) {
    if (itemValidator) {
      return data.map((item, index) => {
        try {
          return itemValidator(item);
        } catch (error) {
          console.warn(`[safeArrayProcessing] Invalid item at index ${index}:`, error);
          return null;
        }
      }).filter((item): item is T => item !== null);
    }
    return data as T[];
  }

  // Handle single objects - wrap in array
  if (typeof data === 'object') {
    console.warn('[safeArrayProcessing] Received single object, wrapping in array:', data);
    try {
      const validatedItem = itemValidator ? itemValidator(data) : (data as T);
      return [validatedItem];
    } catch (error) {
      console.error('[safeArrayProcessing] Failed to validate single object:', error);
      return [];
    }
  }

  // Handle other types
  console.error('[safeArrayProcessing] Received unexpected data type:', typeof data, data);
  return [];
}

/**
 * Safely performs forEach on unknown data
 * @param data - Unknown data that should be an array
 * @param callback - Function to call for each item
 * @param itemValidator - Optional validator for each item
 */
export function safeForEach<T>(
  data: unknown,
  callback: (item: T, index: number) => void,
  itemValidator?: (item: unknown) => T
): void {
  const safeArray = ensureArray(data, itemValidator);
  safeArray.forEach(callback);
}

/**
 * Safely performs map on unknown data
 * @param data - Unknown data that should be an array
 * @param callback - Function to call for each item
 * @param itemValidator - Optional validator for each item
 * @returns Array of mapped results
 */
export function safeMap<T, R>(
  data: unknown,
  callback: (item: T, index: number) => R,
  itemValidator?: (item: unknown) => T
): R[] {
  const safeArray = ensureArray(data, itemValidator);
  return safeArray.map(callback);
}

/**
 * Safely performs filter on unknown data
 * @param data - Unknown data that should be an array
 * @param callback - Function to test each item
 * @param itemValidator - Optional validator for each item
 * @returns Filtered array
 */
export function safeFilter<T>(
  data: unknown,
  callback: (item: T, index: number) => boolean,
  itemValidator?: (item: unknown) => T
): T[] {
  const safeArray = ensureArray(data, itemValidator);
  return safeArray.filter(callback);
}

/**
 * Safely gets array length
 * @param data - Unknown data that should be an array
 * @returns Length of array (0 if not an array)
 */
export function safeArrayLength(data: unknown): number {
  if (Array.isArray(data)) {
    return data.length;
  }
  if (data && typeof data === 'object') {
    return 1; // Single object counts as 1
  }
  return 0;
}

/**
 * Safely checks if data has items
 * @param data - Unknown data that should be an array
 * @returns Boolean indicating if there are items
 */
export function hasArrayItems(data: unknown): boolean {
  return safeArrayLength(data) > 0;
}

/**
 * Safely extracts nested array from API response
 * @param response - API response object
 * @param path - Dot-notation path to the array (e.g., 'data.items')
 * @param itemValidator - Optional validator for each item
 * @returns Safe array
 */
export function extractNestedArray<T>(
  response: any,
  path: string,
  itemValidator?: (item: unknown) => T
): T[] {
  if (!response || typeof response !== 'object') {
    console.warn('[safeArrayProcessing] Invalid response object');
    return [];
  }

  // Navigate the path
  let current = response;
  const pathParts = path.split('.');
  
  for (const part of pathParts) {
    if (!current || typeof current !== 'object' || !(part in current)) {
      console.warn(`[safeArrayProcessing] Path '${path}' not found in response`);
      return [];
    }
    current = current[part];
  }

  return ensureArray(current, itemValidator);
}

/**
 * Creates a safe forEach wrapper for components
 * @param componentName - Name of component for debugging
 * @returns Safe forEach function
 */
export function createSafeForEach(componentName: string) {
  return function<T>(
    data: unknown,
    callback: (item: T, index: number) => void,
    itemValidator?: (item: unknown) => T
  ): void {
    try {
      safeForEach(data, callback, itemValidator);
    } catch (error) {
      console.error(`[${componentName}] Error in safe forEach:`, error);
    }
  };
}

/**
 * Validates common API response patterns
 */
export const responsePatterns = {
  /**
   * Handles responses that might be { data: [...] } or just [...]
   */
  dataWrapper<T>(response: any, itemValidator?: (item: unknown) => T): T[] {
    if (response && typeof response === 'object' && 'data' in response) {
      return ensureArray(response.data, itemValidator);
    }
    return ensureArray(response, itemValidator);
  },

  /**
   * Handles paginated responses like { items: [...], total: number }
   */
  paginated<T>(response: any, itemValidator?: (item: unknown) => T): T[] {
    if (response && typeof response === 'object') {
      // Try common pagination field names
      for (const field of ['items', 'data', 'results', 'records']) {
        if (field in response) {
          return ensureArray(response[field], itemValidator);
        }
      }
    }
    return ensureArray(response, itemValidator);
  },

  /**
   * Handles nested responses like { jobs: [...], total: number }
   */
  nested<T>(response: any, arrayField: string, itemValidator?: (item: unknown) => T): T[] {
    return extractNestedArray(response, arrayField, itemValidator);
  }
};

export default {
  ensureArray,
  safeForEach,
  safeMap,
  safeFilter,
  safeArrayLength,
  hasArrayItems,
  extractNestedArray,
  createSafeForEach,
  responsePatterns
};