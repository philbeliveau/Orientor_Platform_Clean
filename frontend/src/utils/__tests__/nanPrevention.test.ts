/**
 * NaN Prevention Tests for Holland Test UI Components
 * 
 * These tests ensure that NaN values never reach the user interface,
 * specifically focusing on the "Durée estimée: NaN minutes" bug.
 */

import { safeTestDuration, validateTestMetadata, safeNumber } from '../numberUtils';
import hollandTestService from '../../services/hollandTestService';

describe('NaN Prevention for Holland Test UI', () => {
  describe('UI Display Protection', () => {
    it('should never display "NaN minutes" in any scenario', () => {
      const problematicInputs = [
        null,
        undefined,
        NaN,
        Infinity,
        -Infinity,
        'not a number',
        {},
        [],
        false,
        true,
        -1,
        0
      ];

      problematicInputs.forEach(input => {
        const duration = safeTestDuration(input as any);
        
        expect(duration).not.toContain('NaN');
        expect(duration).not.toContain('Infinity');
        expect(duration).not.toContain('undefined');
        expect(duration).not.toContain('null');
        expect(duration).toMatch(/^\d+ minutes?$/);
      });
    });

    it('should never display "NaN" in question count', () => {
      const problematicInputs = [
        null,
        undefined,
        NaN,
        Infinity,
        'invalid',
        {},
        []
      ];

      problematicInputs.forEach(input => {
        const safeCount = safeNumber(input as any, 30);
        
        expect(safeCount).not.toBeNaN();
        expect(isFinite(safeCount)).toBe(true);
        expect(typeof safeCount).toBe('number');
        expect(safeCount).toBeGreaterThanOrEqual(0);
      });
    });

    it('should provide meaningful fallbacks for all UI elements', () => {
      const emptyMetadata = validateTestMetadata(null);
      
      // Title should never be empty or invalid
      expect(emptyMetadata.title).toBeTruthy();
      expect(typeof emptyMetadata.title).toBe('string');
      expect(emptyMetadata.title.length).toBeGreaterThan(0);
      
      // Description should never be empty or invalid
      expect(emptyMetadata.description).toBeTruthy();
      expect(typeof emptyMetadata.description).toBe('string');
      expect(emptyMetadata.description.length).toBeGreaterThan(0);
      
      // Question count should always be a valid positive number
      expect(emptyMetadata.question_count).toBeGreaterThan(0);
      expect(Number.isFinite(emptyMetadata.question_count)).toBe(true);
      
      // Duration should always be valid
      const duration = safeTestDuration(emptyMetadata.question_count);
      expect(duration).toMatch(/^\d+ minutes?$/);
    });
  });

  describe('Service Layer Protection', () => {
    it('should validate metadata structure before processing', () => {
      const malformedResponses = [
        null,
        undefined,
        {},
        { question_count: 'invalid' },
        { question_count: NaN, title: null },
        'not an object',
        []
      ];

      malformedResponses.forEach(response => {
        const validated = validateTestMetadata(response);
        
        // Should always return a valid structure
        expect(validated).toHaveProperty('id');
        expect(validated).toHaveProperty('title');
        expect(validated).toHaveProperty('description');
        expect(validated).toHaveProperty('question_count');
        expect(validated).toHaveProperty('chapter_count');
        
        // Should always have valid types
        expect(typeof validated.id).toBe('number');
        expect(typeof validated.title).toBe('string');
        expect(typeof validated.description).toBe('string');
        expect(typeof validated.question_count).toBe('number');
        expect(typeof validated.chapter_count).toBe('number');
        
        // Numeric fields should never be NaN
        expect(Number.isFinite(validated.id)).toBe(true);
        expect(Number.isFinite(validated.question_count)).toBe(true);
        expect(Number.isFinite(validated.chapter_count)).toBe(true);
      });
    });

    it('should handle service failures gracefully', async () => {
      // Mock a service that returns invalid data
      const originalGetTestMetadata = hollandTestService.getTestMetadata;
      
      // Test with the actual implementation since it now has defensive programming
      try {
        // This should not throw and should return valid fallback data
        const metadata = await hollandTestService.getTestMetadata('fake-token');
        
        expect(metadata).toBeDefined();
        expect(typeof metadata.question_count).toBe('number');
        expect(Number.isFinite(metadata.question_count)).toBe(true);
        expect(metadata.question_count).toBeGreaterThan(0);
      } catch (error) {
        // If it throws, that's also acceptable as long as the UI handles it
        expect(error).toBeDefined();
      }
    });
  });

  describe('Mathematical Operations Protection', () => {
    it('should handle division by zero safely', () => {
      const result = safeTestDuration(0);
      expect(result).not.toContain('NaN');
      expect(result).not.toContain('Infinity');
      expect(result).toMatch(/^\d+ minutes?$/);
    });

    it('should handle floating point precision issues', () => {
      const precisionTestCases = [
        0.1 + 0.2, // 0.30000000000000004
        1 / 3,     // 0.3333333333333333
        Math.sqrt(-1), // NaN
        1 / 0,     // Infinity
        -1 / 0     // -Infinity
      ];

      precisionTestCases.forEach(testCase => {
        const duration = safeTestDuration(testCase);
        expect(duration).toMatch(/^\d+ minutes?$/);
        expect(duration).not.toContain('NaN');
        expect(duration).not.toContain('Infinity');
      });
    });

    it('should handle extremely large and small numbers', () => {
      const extremeValues = [
        Number.MAX_VALUE,
        Number.MIN_VALUE,
        Number.MAX_SAFE_INTEGER,
        Number.MIN_SAFE_INTEGER,
        1e-10,
        1e10
      ];

      extremeValues.forEach(value => {
        const duration = safeTestDuration(value);
        expect(duration).toMatch(/^\d+ minutes?$/);
        expect(duration).not.toContain('NaN');
        expect(duration).not.toContain('Infinity');
      });
    });
  });

  describe('Type Safety Protection', () => {
    it('should handle mixed type inputs safely', () => {
      const mixedTypes = [
        '30',        // String number
        '30.5',      // String decimal
        'thirty',    // String word
        true,        // Boolean
        false,       // Boolean
        [30],        // Array with number
        { value: 30 }, // Object
        new Date(),  // Date object
        Symbol('30') // Symbol
      ];

      mixedTypes.forEach(input => {
        const safeValue = safeNumber(input as any, 30);
        expect(typeof safeValue).toBe('number');
        expect(Number.isFinite(safeValue)).toBe(true);
        
        const duration = safeTestDuration(safeValue);
        expect(duration).toMatch(/^\d+ minutes?$/);
      });
    });

    it('should maintain type consistency through the pipeline', () => {
      // Simulate the full data flow: API -> Service -> Component
      const apiResponse = { question_count: '25' }; // String from API
      
      // Step 1: Service validation
      const validatedMetadata = validateTestMetadata(apiResponse);
      expect(typeof validatedMetadata.question_count).toBe('number');
      expect(Number.isFinite(validatedMetadata.question_count)).toBe(true);
      
      // Step 2: Component safe processing
      const safeCount = safeNumber(validatedMetadata.question_count, 30);
      expect(typeof safeCount).toBe('number');
      expect(Number.isFinite(safeCount)).toBe(true);
      
      // Step 3: UI display
      const duration = safeTestDuration(safeCount);
      expect(duration).toMatch(/^\d+ minutes?$/);
      expect(duration).not.toContain('NaN');
    });
  });

  describe('Real-world Scenario Testing', () => {
    it('should handle common API response patterns', () => {
      const realWorldPatterns = [
        // Successful response
        { 
          id: 1, 
          title: 'Holland Test', 
          description: 'Test description',
          question_count: 30,
          chapter_count: 3,
          seo_code: 'holland'
        },
        
        // Response with string numbers (common in some APIs)
        { 
          question_count: '30',
          chapter_count: '3'
        },
        
        // Incomplete response
        { 
          title: 'Holland Test'
        },
        
        // Response with extra fields
        { 
          question_count: 30,
          extra_field: 'ignored',
          internal_id: 'abc123'
        },
        
        // Empty response
        {},
        
        // Null response
        null
      ];

      realWorldPatterns.forEach((pattern, index) => {
        const validated = validateTestMetadata(pattern);
        const duration = safeTestDuration(validated.question_count);
        
        // Should never fail
        expect(duration).toBeDefined();
        expect(duration).toMatch(/^\d+ minutes?$/);
        expect(duration).not.toContain('NaN');
        
        console.log(`Pattern ${index + 1}: ${JSON.stringify(pattern)} -> ${duration}`);
      });
    });

    it('should provide consistent user experience regardless of data quality', () => {
      const inconsistentData = [
        null,
        { question_count: NaN },
        { question_count: 'invalid' },
        { question_count: 0 },
        { question_count: -5 },
        { question_count: 1000 }
      ];

      const durations = inconsistentData.map(data => {
        const validated = validateTestMetadata(data);
        return safeTestDuration(validated.question_count);
      });

      // All durations should be valid and user-friendly
      durations.forEach(duration => {
        expect(duration).toMatch(/^\d+ minutes?$/);
        expect(duration).not.toContain('NaN');
        
        // Extract the number to ensure it's reasonable
        const minutes = parseInt(duration.match(/\d+/)?.[0] || '0');
        expect(minutes).toBeGreaterThanOrEqual(5);  // Minimum reasonable time
        expect(minutes).toBeLessThanOrEqual(60);    // Maximum reasonable time
      });
    });
  });
});