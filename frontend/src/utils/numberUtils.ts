/**
 * Number utility functions for safe handling of numerical values
 * Provides defensive programming against NaN, undefined, and invalid numbers
 */

/**
 * Safely formats a percentage value, ensuring it's always a valid number
 * @param value - The percentage value to format
 * @param defaultValue - Default value to use if input is invalid (default: 0)
 * @param decimals - Number of decimal places (default: 1)
 * @returns Formatted percentage string (e.g., "75.5%")
 */
export const safePercentage = (
  value: number | undefined | null, 
  defaultValue: number = 0,
  decimals: number = 1
): string => {
  // Handle undefined, null, NaN, and infinity
  if (
    value === null || 
    value === undefined || 
    !Number.isFinite(value) || 
    Number.isNaN(value)
  ) {
    return `${defaultValue.toFixed(decimals)}%`;
  }
  
  // Clamp value between 0 and 100 for percentages
  const clampedValue = Math.max(0, Math.min(100, value));
  return `${clampedValue.toFixed(decimals)}%`;
};

/**
 * Safely converts a value to a number, with fallback
 * @param value - The value to convert to number
 * @param defaultValue - Default value if conversion fails (default: 0)
 * @returns Valid number
 */
export const safeNumber = (
  value: any, 
  defaultValue: number = 0
): number => {
  if (value === null || value === undefined) {
    return defaultValue;
  }
  
  const num = Number(value);
  
  if (Number.isNaN(num) || !Number.isFinite(num)) {
    return defaultValue;
  }
  
  return num;
};

/**
 * Safely formats a number for display
 * @param value - The number to format
 * @param defaultValue - Default value if input is invalid (default: 0)
 * @param decimals - Number of decimal places (default: 0)
 * @returns Formatted number string
 */
export const safeNumberDisplay = (
  value: number | undefined | null,
  defaultValue: number = 0,
  decimals: number = 0
): string => {
  const safeValue = safeNumber(value, defaultValue);
  return safeValue.toFixed(decimals);
};

/**
 * Checks if a value is a valid number (not NaN, null, undefined, or infinity)
 * @param value - The value to check
 * @returns True if the value is a valid finite number
 */
export const isValidNumber = (value: any): boolean => {
  return (
    value !== null && 
    value !== undefined && 
    typeof value === 'number' && 
    Number.isFinite(value) && 
    !Number.isNaN(value)
  );
};

/**
 * Safely performs division with fallback for division by zero
 * @param numerator - The numerator
 * @param denominator - The denominator
 * @param defaultValue - Default value if division is invalid (default: 0)
 * @returns Result of division or default value
 */
export const safeDivision = (
  numerator: number, 
  denominator: number, 
  defaultValue: number = 0
): number => {
  if (
    !isValidNumber(numerator) || 
    !isValidNumber(denominator) || 
    denominator === 0
  ) {
    return defaultValue;
  }
  
  const result = numerator / denominator;
  return isValidNumber(result) ? result : defaultValue;
};

/**
 * Safely calculates percentage with protection against division by zero
 * @param part - The part value
 * @param total - The total value
 * @param defaultValue - Default value if calculation is invalid (default: 0)
 * @returns Percentage value (0-100)
 */
export const safePercentageCalculation = (
  part: number, 
  total: number, 
  defaultValue: number = 0
): number => {
  if (!isValidNumber(part) || !isValidNumber(total) || total === 0) {
    return defaultValue;
  }
  
  const percentage = (part / total) * 100;
  
  if (!isValidNumber(percentage)) {
    return defaultValue;
  }
  
  // Clamp between 0 and 100
  return Math.max(0, Math.min(100, percentage));
};

/**
 * Type guard to check if an API response contains valid numerical data
 * @param response - The API response object
 * @param field - The field name to check
 * @returns True if the field exists and contains a valid number
 */
export const hasValidNumberField = (response: any, field: string): boolean => {
  return response && typeof response === 'object' && isValidNumber(response[field]);
};

/**
 * Safely extracts a number from an API response with fallback
 * @param response - The API response object
 * @param field - The field name to extract
 * @param defaultValue - Default value if extraction fails (default: 0)
 * @returns Extracted number or default value
 */
export const extractSafeNumber = (
  response: any, 
  field: string, 
  defaultValue: number = 0
): number => {
  if (!response || typeof response !== 'object') {
    return defaultValue;
  }
  
  return safeNumber(response[field], defaultValue);
};

/**
 * Safely calculates test duration with fallback for invalid question counts
 * @param questionCount - Number of questions in the test
 * @param timePerQuestion - Time per question in minutes (default: 0.5)
 * @param defaultDuration - Default duration if calculation fails (default: 15)
 * @returns Formatted duration string (e.g., "15 minutes")
 */
export const safeTestDuration = (
  questionCount: number | undefined | null,
  timePerQuestion: number = 0.5,
  defaultDuration: number = 15
): string => {
  // Validate question count
  const safeQuestionCount = safeNumber(questionCount, 30); // Default to 30 questions if invalid
  
  // Validate time per question
  const safeTimePerQuestion = safeNumber(timePerQuestion, 0.5);
  
  // Calculate duration
  const calculatedDuration = Math.ceil(safeQuestionCount * safeTimePerQuestion);
  
  // Ensure we have a reasonable duration (minimum 5 minutes, maximum 60 minutes)
  const finalDuration = Math.max(5, Math.min(60, calculatedDuration || defaultDuration));
  
  return `${finalDuration} minute${finalDuration !== 1 ? 's' : ''}`;
};

/**
 * Validates test metadata and ensures all required fields are safe
 * @param metadata - Raw test metadata from API
 * @returns Validated metadata with safe defaults
 */
export const validateTestMetadata = (metadata: any): {
  id: number;
  title: string;
  description: string;
  seo_code: string;
  video_url?: string;
  image_url?: string;
  chapter_count: number;
  question_count: number;
  is_valid: boolean;
} => {
  if (!metadata || typeof metadata !== 'object') {
    return {
      id: 0,
      title: 'Test Holland Code',
      description: 'Découvrez votre profil professionnel grâce au test Holland Code (RIASEC)',
      seo_code: 'holland-test',
      chapter_count: 1,
      question_count: 30,
      is_valid: false
    };
  }

  return {
    id: safeNumber(metadata.id, 0),
    title: typeof metadata.title === 'string' ? metadata.title : 'Test Holland Code',
    description: typeof metadata.description === 'string' 
      ? metadata.description 
      : 'Découvrez votre profil professionnel grâce au test Holland Code (RIASEC)',
    seo_code: typeof metadata.seo_code === 'string' ? metadata.seo_code : 'holland-test',
    video_url: typeof metadata.video_url === 'string' ? metadata.video_url : undefined,
    image_url: typeof metadata.image_url === 'string' ? metadata.image_url : undefined,
    chapter_count: safeNumber(metadata.chapter_count, 1),
    question_count: safeNumber(metadata.question_count, 30),
    is_valid: true
  };
};