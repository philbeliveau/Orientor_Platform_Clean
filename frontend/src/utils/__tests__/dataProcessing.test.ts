import { 
  ensureArray, 
  safeForEach, 
  safeMap, 
  safeFilter, 
  safeArrayLength, 
  hasArrayItems,
  extractNestedArray,
  responsePatterns 
} from '../safeArrayProcessing';

describe('Safe Array Processing', () => {
  describe('ensureArray', () => {
    it('should return empty array for null/undefined', () => {
      expect(ensureArray(null)).toEqual([]);
      expect(ensureArray(undefined)).toEqual([]);
    });

    it('should return the same array for valid arrays', () => {
      const testArray = [1, 2, 3];
      expect(ensureArray(testArray)).toBe(testArray);
    });

    it('should wrap single objects in array', () => {
      const testObj = { id: 1, name: 'test' };
      expect(ensureArray(testObj)).toEqual([testObj]);
    });

    it('should return empty array for invalid types', () => {
      expect(ensureArray('string')).toEqual([]);
      expect(ensureArray(123)).toEqual([]);
      expect(ensureArray(true)).toEqual([]);
    });

    it('should validate items when validator provided', () => {
      const validator = (item: any) => {
        if (!item || !item.id) throw new Error('Invalid item');
        return item;
      };

      const validArray = [{ id: 1 }, { id: 2 }];
      expect(ensureArray(validArray, validator)).toEqual(validArray);

      const invalidArray = [{ id: 1 }, null, { id: 2 }];
      expect(ensureArray(invalidArray, validator)).toEqual([{ id: 1 }, { id: 2 }]);
    });
  });

  describe('safeForEach', () => {
    it('should handle valid arrays normally', () => {
      const callback = jest.fn();
      const testArray = [1, 2, 3];
      
      safeForEach(testArray, callback);
      
      expect(callback).toHaveBeenCalledTimes(3);
      expect(callback).toHaveBeenCalledWith(1, 0);
      expect(callback).toHaveBeenCalledWith(2, 1);
      expect(callback).toHaveBeenCalledWith(3, 2);
    });

    it('should handle non-arrays gracefully', () => {
      const callback = jest.fn();
      
      safeForEach(null, callback);
      expect(callback).not.toHaveBeenCalled();

      safeForEach({ id: 1 }, callback);
      expect(callback).toHaveBeenCalledWith({ id: 1 }, 0);
    });

    it('should prevent TypeError: forEach is not a function', () => {
      const callback = jest.fn();
      
      // These should not throw errors
      expect(() => safeForEach('not an array', callback)).not.toThrow();
      expect(() => safeForEach(123, callback)).not.toThrow();
      expect(() => safeForEach(null, callback)).not.toThrow();
    });
  });

  describe('safeMap', () => {
    it('should map arrays normally', () => {
      const mapper = (x: number) => x * 2;
      expect(safeMap([1, 2, 3], mapper)).toEqual([2, 4, 6]);
    });

    it('should handle non-arrays', () => {
      const mapper = (x: any) => x.id;
      expect(safeMap({ id: 5 }, mapper)).toEqual([5]);
      expect(safeMap(null, mapper)).toEqual([]);
    });
  });

  describe('safeFilter', () => {
    it('should filter arrays normally', () => {
      const predicate = (x: number) => x > 2;
      expect(safeFilter([1, 2, 3, 4], predicate)).toEqual([3, 4]);
    });

    it('should handle non-arrays', () => {
      const predicate = (x: any) => x.valid;
      expect(safeFilter({ valid: true }, predicate)).toEqual([{ valid: true }]);
      expect(safeFilter({ valid: false }, predicate)).toEqual([]);
    });
  });

  describe('safeArrayLength', () => {
    it('should return correct length for arrays', () => {
      expect(safeArrayLength([1, 2, 3])).toBe(3);
      expect(safeArrayLength([])).toBe(0);
    });

    it('should return 1 for objects, 0 for null', () => {
      expect(safeArrayLength({ id: 1 })).toBe(1);
      expect(safeArrayLength(null)).toBe(0);
      expect(safeArrayLength(undefined)).toBe(0);
    });
  });

  describe('hasArrayItems', () => {
    it('should correctly identify empty/non-empty', () => {
      expect(hasArrayItems([1, 2, 3])).toBe(true);
      expect(hasArrayItems([])).toBe(false);
      expect(hasArrayItems({ id: 1 })).toBe(true);
      expect(hasArrayItems(null)).toBe(false);
    });
  });

  describe('extractNestedArray', () => {
    it('should extract nested arrays', () => {
      const response = {
        data: {
          items: [1, 2, 3]
        }
      };
      
      expect(extractNestedArray(response, 'data.items')).toEqual([1, 2, 3]);
    });

    it('should handle missing paths', () => {
      const response = { data: {} };
      expect(extractNestedArray(response, 'data.missing')).toEqual([]);
    });
  });

  describe('responsePatterns', () => {
    describe('dataWrapper', () => {
      it('should handle wrapped responses', () => {
        const wrappedResponse = { data: [1, 2, 3] };
        expect(responsePatterns.dataWrapper(wrappedResponse)).toEqual([1, 2, 3]);
        
        const directResponse = [1, 2, 3];
        expect(responsePatterns.dataWrapper(directResponse)).toEqual([1, 2, 3]);
      });
    });

    describe('paginated', () => {
      it('should handle different pagination field names', () => {
        expect(responsePatterns.paginated({ items: [1, 2] })).toEqual([1, 2]);
        expect(responsePatterns.paginated({ data: [1, 2] })).toEqual([1, 2]);
        expect(responsePatterns.paginated({ results: [1, 2] })).toEqual([1, 2]);
        expect(responsePatterns.paginated({ records: [1, 2] })).toEqual([1, 2]);
      });
    });

    describe('nested', () => {
      it('should handle nested field extraction', () => {
        const response = { jobs: [{ id: 1 }], total: 1 };
        expect(responsePatterns.nested(response, 'jobs')).toEqual([{ id: 1 }]);
      });
    });
  });
});

// Test specific bug scenarios
describe('Bug Prevention', () => {
  it('should prevent "forEach is not a function" errors', () => {
    const problematicData = [
      null,
      undefined,
      'string response',
      123,
      { single: 'object' },
      { data: null },
      { data: 'not an array' }
    ];

    problematicData.forEach(data => {
      expect(() => {
        safeForEach(data, (item) => {
          console.log('Processing item:', item);
        });
      }).not.toThrow();
    });
  });

  it('should handle API response inconsistencies', () => {
    // Simulate different API response formats
    const responses = [
      [{ id: 1 }], // Direct array
      { data: [{ id: 1 }] }, // Wrapped array
      { id: 1 }, // Single object
      null, // Null response
      { jobs: [{ id: 1 }], total: 1 } // Paginated response
    ];

    responses.forEach(response => {
      expect(() => {
        const items = responsePatterns.dataWrapper(response);
        safeForEach(items, (item) => {
          console.log('Safe processing:', item);
        });
      }).not.toThrow();
    });
  });
});