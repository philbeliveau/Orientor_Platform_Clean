import { safeTestDuration, validateTestMetadata, safeNumber } from '../numberUtils';

describe('Holland Test Duration Processing', () => {
  describe('safeTestDuration', () => {
    it('should calculate correct duration for valid question count', () => {
      expect(safeTestDuration(30)).toBe('15 minutes');
      expect(safeTestDuration(20)).toBe('10 minutes');
      expect(safeTestDuration(10)).toBe('5 minutes');
      expect(safeTestDuration(40)).toBe('20 minutes');
    });

    it('should handle edge cases and return fallback for invalid inputs', () => {
      expect(safeTestDuration(null)).toBe('15 minutes');
      expect(safeTestDuration(undefined)).toBe('15 minutes');
      expect(safeTestDuration(NaN)).toBe('15 minutes');
      expect(safeTestDuration(Infinity)).toBe('15 minutes');
      expect(safeTestDuration(-5)).toBe('15 minutes');
    });

    it('should handle zero and very small numbers', () => {
      expect(safeTestDuration(0)).toBe('15 minutes');
      expect(safeTestDuration(1)).toBe('5 minutes'); // Minimum is 5 minutes
      expect(safeTestDuration(2)).toBe('5 minutes'); // Minimum is 5 minutes
    });

    it('should cap very large durations', () => {
      expect(safeTestDuration(200)).toBe('60 minutes'); // Maximum is 60 minutes
      expect(safeTestDuration(1000)).toBe('60 minutes'); // Maximum is 60 minutes
    });

    it('should use custom time per question and default duration', () => {
      expect(safeTestDuration(30, 1)).toBe('30 minutes'); // 1 minute per question
      expect(safeTestDuration(null, 0.5, 20)).toBe('20 minutes'); // Custom default
    });

    it('should handle string inputs that can be converted to numbers', () => {
      // Note: The function expects numbers, but let's test the safeNumber utility it uses
      expect(safeNumber('30', 0)).toBe(30);
      expect(safeNumber('invalid', 30)).toBe(30);
    });

    it('should always return a string with "minute" or "minutes"', () => {
      expect(safeTestDuration(1)).toContain('minute');
      expect(safeTestDuration(30)).toContain('minutes');
      expect(safeTestDuration(null)).toContain('minutes');
    });

    it('should use singular "minute" for duration of 1', () => {
      // Since minimum is 5 minutes, we need to test with custom params
      expect(safeTestDuration(2, 0.5, 1)).toBe('1 minute');
    });
  });

  describe('validateTestMetadata', () => {
    it('should validate and return clean metadata for valid input', () => {
      const validMetadata = {
        id: 1,
        title: 'Test Holland',
        description: 'Un test de personnalité',
        seo_code: 'holland-test',
        video_url: 'https://example.com/video.mp4',
        image_url: 'https://example.com/image.jpg',
        chapter_count: 3,
        question_count: 30
      };

      const result = validateTestMetadata(validMetadata);

      expect(result.is_valid).toBe(true);
      expect(result.id).toBe(1);
      expect(result.title).toBe('Test Holland');
      expect(result.question_count).toBe(30);
      expect(result.chapter_count).toBe(3);
    });

    it('should provide safe defaults for null or undefined input', () => {
      const result = validateTestMetadata(null);

      expect(result.is_valid).toBe(false);
      expect(result.title).toBe('Test Holland Code');
      expect(result.question_count).toBe(30);
      expect(result.chapter_count).toBe(1);
      expect(result.description).toContain('Holland Code');
    });

    it('should sanitize invalid numeric fields', () => {
      const invalidMetadata = {
        id: 'invalid',
        title: 'Test',
        description: 'Description',
        seo_code: 'test',
        question_count: NaN,
        chapter_count: undefined
      };

      const result = validateTestMetadata(invalidMetadata);

      expect(result.id).toBe(0); // Fallback for invalid ID
      expect(result.question_count).toBe(30); // Fallback for NaN
      expect(result.chapter_count).toBe(1); // Fallback for undefined
      expect(result.is_valid).toBe(true); // Still valid because it was an object
    });

    it('should handle missing required fields', () => {
      const partialMetadata = {
        id: 1
        // Missing other required fields
      };

      const result = validateTestMetadata(partialMetadata);

      expect(result.id).toBe(1);
      expect(result.title).toBe('Test Holland Code'); // Default title
      expect(result.description).toContain('Holland Code'); // Default description
      expect(result.question_count).toBe(30); // Default count
    });

    it('should preserve valid optional fields', () => {
      const metadataWithOptionals = {
        id: 1,
        title: 'Test',
        description: 'Description',
        seo_code: 'test',
        video_url: 'https://example.com/video.mp4',
        image_url: 'https://example.com/image.jpg',
        question_count: 25,
        chapter_count: 2
      };

      const result = validateTestMetadata(metadataWithOptionals);

      expect(result.video_url).toBe('https://example.com/video.mp4');
      expect(result.image_url).toBe('https://example.com/image.jpg');
    });

    it('should filter out invalid optional fields', () => {
      const metadataWithInvalidOptionals = {
        id: 1,
        title: 'Test',
        description: 'Description',
        seo_code: 'test',
        video_url: 123, // Invalid type
        image_url: null, // Null
        question_count: 25,
        chapter_count: 2
      };

      const result = validateTestMetadata(metadataWithInvalidOptionals);

      expect(result.video_url).toBeUndefined();
      expect(result.image_url).toBeUndefined();
    });
  });

  describe('Integration: Duration calculation with validated metadata', () => {
    it('should never produce NaN when using validated metadata', () => {
      // Test with various invalid metadata inputs
      const invalidInputs = [
        null,
        undefined,
        { question_count: NaN },
        { question_count: 'invalid' },
        { question_count: null },
        {},
        { question_count: Infinity },
        { question_count: -10 }
      ];

      invalidInputs.forEach(input => {
        const validatedMetadata = validateTestMetadata(input);
        const duration = safeTestDuration(validatedMetadata.question_count);
        
        expect(duration).toMatch(/^\d+ minutes?$/); // Should always be a valid duration string
        expect(duration).not.toContain('NaN');
        expect(duration).not.toContain('Infinity');
        expect(duration).not.toContain('undefined');
      });
    });

    it('should produce consistent results for the same validated input', () => {
      const metadata = validateTestMetadata({ question_count: 30 });
      const duration1 = safeTestDuration(metadata.question_count);
      const duration2 = safeTestDuration(metadata.question_count);
      
      expect(duration1).toBe(duration2);
      expect(duration1).toBe('15 minutes');
    });

    it('should handle real-world API response scenarios', () => {
      // Simulate API responses that might cause issues
      const realWorldScenarios = [
        // Empty response
        {},
        // Partial response
        { title: 'Test', question_count: 30 },
        // Response with string numbers
        { question_count: '25', chapter_count: '3' },
        // Response with extra fields
        { 
          question_count: 30, 
          extra_field: 'should be ignored',
          another_field: 123 
        },
        // Response with null values
        { 
          question_count: null, 
          title: null, 
          description: undefined 
        }
      ];

      realWorldScenarios.forEach((scenario, index) => {
        const validatedMetadata = validateTestMetadata(scenario);
        const duration = safeTestDuration(validatedMetadata.question_count);
        
        // Should never crash or produce invalid output
        expect(typeof duration).toBe('string');
        expect(duration).toMatch(/^\d+ minutes?$/);
        
        console.log(`Scenario ${index + 1}: Input:`, scenario, 'Duration:', duration);
      });
    });
  });
});