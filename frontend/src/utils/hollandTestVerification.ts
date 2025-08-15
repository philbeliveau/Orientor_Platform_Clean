/**
 * Holland Test Duration Fix Verification
 * 
 * This script verifies that the NaN duration bug has been fixed
 * and provides validation for the Holland test components.
 */

import { safeTestDuration, validateTestMetadata, safeNumber } from './numberUtils';

export interface VerificationResult {
  success: boolean;
  message: string;
  details?: any;
}

/**
 * Verify that duration calculation never produces NaN
 */
export function verifyDurationCalculation(): VerificationResult {
  const problematicInputs = [
    null,
    undefined,
    NaN,
    Infinity,
    -Infinity,
    'not a number',
    {},
    [],
    0,
    -5
  ];

  for (const input of problematicInputs) {
    const duration = safeTestDuration(input as any);
    
    if (duration.includes('NaN') || duration.includes('Infinity') || duration.includes('undefined')) {
      return {
        success: false,
        message: `Duration calculation failed for input: ${input}`,
        details: { input, output: duration }
      };
    }
    
    if (!duration.match(/^\d+ minutes?$/)) {
      return {
        success: false,
        message: `Invalid duration format for input: ${input}`,
        details: { input, output: duration }
      };
    }
  }

  return {
    success: true,
    message: 'Duration calculation is robust against all problematic inputs'
  };
}

/**
 * Verify that metadata validation provides safe defaults
 */
export function verifyMetadataValidation(): VerificationResult {
  const problematicInputs = [
    null,
    undefined,
    {},
    { question_count: NaN },
    { question_count: 'invalid' },
    { question_count: Infinity },
    'not an object',
    []
  ];

  for (const input of problematicInputs) {
    const validated = validateTestMetadata(input as any);
    
    // Check required fields exist and are valid
    if (!validated.title || typeof validated.title !== 'string') {
      return {
        success: false,
        message: `Invalid title in validated metadata for input: ${input}`,
        details: { input, validated }
      };
    }
    
    if (!Number.isFinite(validated.question_count) || validated.question_count <= 0) {
      return {
        success: false,
        message: `Invalid question_count in validated metadata for input: ${input}`,
        details: { input, validated }
      };
    }
    
    if (!Number.isFinite(validated.chapter_count) || validated.chapter_count <= 0) {
      return {
        success: false,
        message: `Invalid chapter_count in validated metadata for input: ${input}`,
        details: { input, validated }
      };
    }
  }

  return {
    success: true,
    message: 'Metadata validation provides safe defaults for all inputs'
  };
}

/**
 * Test the complete pipeline from API response to UI display
 */
export function verifyCompleteDataPipeline(): VerificationResult {
  // Simulate problematic API responses
  const apiResponses = [
    null,
    undefined,
    {},
    { question_count: null },
    { question_count: 'invalid_string' },
    { question_count: NaN, title: undefined },
    { question_count: 0 },
    { some_other_field: 'value' }
  ];

  for (const apiResponse of apiResponses) {
    try {
      // Step 1: Validate metadata (service layer)
      const validatedMetadata = validateTestMetadata(apiResponse);
      
      // Step 2: Safe number processing (component layer)
      const safeQuestionCount = safeNumber(validatedMetadata.question_count, 30);
      
      // Step 3: Duration calculation (UI layer)
      const duration = safeTestDuration(safeQuestionCount);
      
      // Verify no NaN values at any step
      if (
        !Number.isFinite(safeQuestionCount) ||
        duration.includes('NaN') ||
        duration.includes('Infinity') ||
        duration.includes('undefined')
      ) {
        return {
          success: false,
          message: `Pipeline failed for API response: ${JSON.stringify(apiResponse)}`,
          details: {
            apiResponse,
            validatedMetadata,
            safeQuestionCount,
            duration
          }
        };
      }
    } catch (error) {
      return {
        success: false,
        message: `Pipeline threw error for API response: ${JSON.stringify(apiResponse)}`,
        details: { apiResponse, error: error.message }
      };
    }
  }

  return {
    success: true,
    message: 'Complete data pipeline is robust against all problematic inputs'
  };
}

/**
 * Run all verification tests
 */
export function runAllVerifications(): {
  overall: boolean;
  results: Record<string, VerificationResult>;
} {
  const results = {
    durationCalculation: verifyDurationCalculation(),
    metadataValidation: verifyMetadataValidation(),
    completeDataPipeline: verifyCompleteDataPipeline()
  };

  const overall = Object.values(results).every(result => result.success);

  return { overall, results };
}

/**
 * Format verification results for console output
 */
export function formatVerificationResults(verification: ReturnType<typeof runAllVerifications>): string {
  const { overall, results } = verification;
  
  let output = `\n🔍 Holland Test Duration Fix Verification\n`;
  output += `${'='.repeat(50)}\n\n`;
  
  for (const [testName, result] of Object.entries(results)) {
    const status = result.success ? '✅ PASS' : '❌ FAIL';
    output += `${status} ${testName}: ${result.message}\n`;
    
    if (!result.success && result.details) {
      output += `   Details: ${JSON.stringify(result.details, null, 2)}\n`;
    }
  }
  
  output += `\n${'='.repeat(50)}\n`;
  output += overall 
    ? `🎉 ALL TESTS PASSED - Holland test duration NaN bug is FIXED!\n`
    : `💥 SOME TESTS FAILED - Additional fixes needed\n`;
  
  return output;
}

// Export for testing in browser console or Node.js
if (typeof window !== 'undefined') {
  // Browser environment - add to window for testing
  (window as any).hollandTestVerification = {
    runAllVerifications,
    formatVerificationResults
  };
} else if (typeof module !== 'undefined' && module.exports) {
  // Node.js environment
  module.exports = {
    runAllVerifications,
    formatVerificationResults,
    verifyDurationCalculation,
    verifyMetadataValidation,
    verifyCompleteDataPipeline
  };
}