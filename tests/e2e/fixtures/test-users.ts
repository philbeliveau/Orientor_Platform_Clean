export const testUsers = {
  validUser: {
    email: 'test@orientor.com',
    password: 'TestPassword123!',
    firstName: 'Test',
    lastName: 'User'
  },
  adminUser: {
    email: 'admin@orientor.com',
    password: 'AdminPassword123!',
    firstName: 'Admin',
    lastName: 'User'
  },
  newUser: {
    email: 'newuser@orientor.com',
    password: 'NewPassword123!',
    firstName: 'New',
    lastName: 'User'
  }
};

export const testData = {
  chatMessage: 'Hello, I need help with career guidance',
  skillNode: 'Software Development',
  careerGoal: 'Become a Full Stack Developer',
  assessment: {
    hexaco: {
      answers: Array(60).fill(3) // Neutral answers for all questions
    },
    holland: {
      answers: Array(48).fill(3) // Neutral answers for all questions
    }
  }
};