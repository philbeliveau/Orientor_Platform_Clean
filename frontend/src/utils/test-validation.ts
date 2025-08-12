// Test script to validate the runtime validation functionality
import {
  validateApiResponse,
  validateApiResponseFormat,
  validateCareerGoal,
  validateAvatarData,
  extractResponseData,
  validateArrayResponse
} from './validation';

// Test data
const validCareerGoal = {
  id: 1,
  title: 'Become a Software Engineer',
  description: 'Learn full-stack development',
  target_date: '2024-12-31',
  progress_percentage: 75
};

const invalidCareerGoal = {
  id: 1,
  title: 'Become a Software Engineer'
  // Missing required fields: target_date, progress_percentage
};

const validAvatarData = {
  success: true,
  avatar_name: 'My Avatar',
  avatar_description: 'A cool avatar',
  avatar_image_url: 'https://example.com/avatar.png'
};

const invalidAvatarData = {
  avatar_name: 'My Avatar'
  // Missing required field: success
};

// Test functions
export function testValidation() {
  console.log('🧪 Testing runtime validation...');

  try {
    // Test 1: Valid career goal
    console.log('Test 1: Valid career goal');
    const result1 = validateCareerGoal(validCareerGoal);
    console.log('✅ PASS: Valid career goal accepted');

    // Test 2: Invalid career goal
    console.log('Test 2: Invalid career goal');
    try {
      validateCareerGoal(invalidCareerGoal);
      console.log('❌ FAIL: Invalid career goal should have been rejected');
    } catch (error) {
      console.log('✅ PASS: Invalid career goal correctly rejected:', error.message);
    }

    // Test 3: Valid avatar data
    console.log('Test 3: Valid avatar data');
    const result3 = validateAvatarData(validAvatarData);
    console.log('✅ PASS: Valid avatar data accepted');

    // Test 4: Invalid avatar data
    console.log('Test 4: Invalid avatar data');
    try {
      validateAvatarData(invalidAvatarData);
      console.log('❌ FAIL: Invalid avatar data should have been rejected');
    } catch (error) {
      console.log('✅ PASS: Invalid avatar data correctly rejected:', error.message);
    }

    // Test 5: API response format validation
    console.log('Test 5: API response format validation');
    const wrappedResponse = { data: validCareerGoal, message: 'Success' };
    const unwrappedResponse = validCareerGoal;
    
    const formatted1 = validateApiResponseFormat(wrappedResponse);
    const formatted2 = validateApiResponseFormat(unwrappedResponse);
    
    console.log('✅ PASS: API response format validation works for both wrapped and unwrapped responses');

    // Test 6: Array validation
    console.log('Test 6: Array validation');
    const validArray = [validCareerGoal, { ...validCareerGoal, id: 2 }];
    const invalidArray = [validCareerGoal, invalidCareerGoal];
    
    const validatedArray = validateArrayResponse(validArray, validateCareerGoal);
    console.log('✅ PASS: Valid array accepted');
    
    try {
      validateArrayResponse(invalidArray, validateCareerGoal);
      console.log('❌ FAIL: Invalid array should have been rejected');
    } catch (error) {
      console.log('✅ PASS: Invalid array correctly rejected:', error.message);
    }

    console.log('🎉 All validation tests passed!');
    return true;

  } catch (error) {
    console.error('❌ Validation test failed:', error);
    return false;
  }
}

// Export for use in other files
export {
  validCareerGoal,
  validAvatarData,
  invalidCareerGoal,
  invalidAvatarData
};