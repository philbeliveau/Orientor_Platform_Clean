/**
 * Safe Data Processing Utilities
 * 
 * Provides robust data validation and sanitization to prevent NaN, undefined,
 * and other invalid values from breaking UI components.
 */

/**
 * Safely converts a value to a number, with fallback
 */
export function safeNumber(value: any, fallback: number = 0): number {
  if (typeof value === 'number' && !isNaN(value) && isFinite(value)) {
    return value;
  }
  
  if (typeof value === 'string') {
    const parsed = parseFloat(value);
    if (!isNaN(parsed) && isFinite(parsed)) {
      return parsed;
    }
  }
  
  return fallback;
}

/**
 * Safely converts a value to a percentage (0-1 range)
 */
export function safePercentage(value: any, fallback: number = 0): number {
  const num = safeNumber(value, fallback);
  return Math.max(0, Math.min(1, num));
}

/**
 * Safely processes an object with numeric values
 */
export function safeNumericObject<T extends Record<string, any>>(
  obj: T,
  fallback: number = 0
): Record<string, number> {
  const result: Record<string, number> = {};
  
  if (!obj || typeof obj !== 'object') {
    return result;
  }
  
  for (const [key, value] of Object.entries(obj)) {
    result[key] = safeNumber(value, fallback);
  }
  
  return result;
}

/**
 * Validates that a number is suitable for display (not NaN, Infinity, etc.)
 */
export function isDisplayableNumber(value: any): boolean {
  return typeof value === 'number' && !isNaN(value) && isFinite(value);
}

/**
 * Formats a percentage for display with fallback
 */
export function formatPercentage(value: any, fallback: string = '0%'): string {
  const num = safePercentage(value);
  if (!isDisplayableNumber(num)) {
    return fallback;
  }
  return `${Math.round(num * 100)}%`;
}

/**
 * Comprehensive data sanitization for profile completion data
 */
export interface ProfileCompletionData {
  overall_percentage: number;
  category_scores: Record<string, number>;
  next_actions: any[];
  recommendation_eligible: boolean;
  missing_critical_data: string[];
}

export function sanitizeProfileCompletionData(rawData: any): ProfileCompletionData {
  return {
    overall_percentage: safePercentage(rawData?.overall_percentage),
    category_scores: safeNumericObject(rawData?.category_scores),
    next_actions: Array.isArray(rawData?.next_actions) ? rawData.next_actions : [],
    recommendation_eligible: Boolean(rawData?.recommendation_eligible),
    missing_critical_data: Array.isArray(rawData?.missing_critical_data) ? rawData.missing_critical_data : []
  };
}