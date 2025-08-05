# Orientor Platform - Comprehensive Testing Suite

## 🚀 Overview

This testing suite provides comprehensive end-to-end (E2E) testing for the Orientor Platform using Playwright. The tests cover authentication, API endpoints, frontend navigation, UI components, and integration flows.

## 📁 Test Structure

```
tests/
├── e2e/
│   ├── auth/
│   │   └── clerk-auth.spec.ts          # Clerk authentication tests
│   ├── api/
│   │   └── backend-endpoints.spec.ts   # Backend API endpoint tests
│   ├── frontend/
│   │   ├── navigation.spec.ts          # Frontend navigation tests
│   │   └── ui-components.spec.ts       # UI component interaction tests
│   ├── integration/
│   │   ├── chat-flow.spec.ts           # AI Chat integration tests
│   │   ├── skill-tree-flow.spec.ts     # Skill tree interaction tests
│   │   └── assessment-flow.spec.ts     # HEXACO/Holland assessment tests
│   ├── fixtures/
│   │   └── test-users.ts               # Test user data and fixtures
│   ├── global-setup.ts                 # Global test setup
│   ├── global-teardown.ts              # Global test cleanup
│   └── simple-test.spec.ts             # Basic connectivity test
└── README.md                           # This file
```

## 🛠️ Setup & Configuration

### Prerequisites

- Node.js 18+ installed
- Python 3.8+ installed (for backend)
- Frontend and backend applications configured

### Installation

1. **Install Playwright** (already done):
   ```bash
   npm install -D @playwright/test playwright
   npx playwright install
   ```

2. **Install additional dependencies**:
   ```bash
   npm install concurrently
   ```

## 🎯 Test Categories

### 1. Authentication Tests (`auth/clerk-auth.spec.ts`)
- Sign-in page rendering and interaction
- Sign-up page rendering and interaction  
- Form validation and error handling
- Authentication state management
- Protected route access

### 2. API Endpoint Tests (`api/backend-endpoints.spec.ts`)
- Health check endpoint
- API documentation access
- CORS configuration
- Protected endpoint authentication
- Error handling for invalid requests
- JSON response validation

### 3. Frontend Navigation Tests (`frontend/navigation.spec.ts`)
- Homepage loading and rendering
- Main navigation functionality
- Responsive navigation (mobile/desktop)
- Protected route redirects
- Breadcrumb navigation
- Back/forward navigation
- External link handling

### 4. UI Component Tests (`frontend/ui-components.spec.ts`)
- JavaScript error detection
- Loading state handling
- Button interactions
- Form input validation
- Modal/dialog interactions
- Dropdown/select functionality
- Tab navigation
- Card/tile interactions
- Toast/notification display
- Accessibility features
- Error state handling

### 5. Integration Tests

#### Chat Flow (`integration/chat-flow.spec.ts`)
- Chat interface rendering
- Message sending and receiving
- Conversation management
- AI response streaming
- Chat features and tools

#### Skill Tree Flow (`integration/skill-tree-flow.spec.ts`)
- Tree visualization rendering
- Node interactions and details
- Navigation and zoom controls
- Search and filtering
- Path exploration
- Assessment integration
- Performance with large datasets

#### Assessment Flow (`integration/assessment-flow.spec.ts`)
- HEXACO personality test interface
- Holland Code career test interface
- Test progression and completion
- Results display and interaction
- Integration with recommendations
- Profile summary display

## 🚀 Running Tests

### Basic Commands

```bash
# Run all tests
npm run test:e2e

# Run tests with UI mode
npm run test:e2e:ui

# Run tests in headed mode (visible browser)
npm run test:e2e:headed

# Debug tests
npm run test:e2e:debug

# Show test report
npm run test:e2e:report

# Run specific test file
npx playwright test tests/e2e/api/backend-endpoints.spec.ts

# Run specific test suite
npx playwright test tests/e2e/auth/

# Run tests on specific browser
npx playwright test --project=chromium
```

### Development Commands

```bash
# Start both frontend and backend for testing
npm run dev:full

# Run tests in CI mode
npm run test:ci

# Install browser binaries
npm run test:install
```

## 📊 Test Configuration

### Playwright Config Features

- **Multi-browser testing**: Chrome, Firefox, Safari, Mobile
- **Parallel execution**: Tests run concurrently for speed
- **Automatic retries**: Failed tests retry automatically
- **Screenshots**: Captured on test failures
- **Video recording**: Available for failed tests
- **Test reporting**: HTML, JSON, and JUnit formats
- **Global setup/teardown**: Shared test initialization

### Environment Variables

```bash
# Base URL for tests (default: http://localhost:3000)
BASE_URL=http://localhost:3000

# Backend URL for API tests (default: http://localhost:8000)
BACKEND_URL=http://localhost:8000
```

## 🐛 Troubleshooting

### Common Issues

1. **"No tests found" error**:
   - Ensure test files are in `tests/e2e/` directory
   - Check file naming convention (`*.spec.ts`)
   - Verify playwright configuration

2. **Browser not installed**:
   ```bash
   npx playwright install
   ```

3. **Port conflicts**:
   - Ensure frontend runs on port 3000
   - Ensure backend runs on port 8000
   - Update `playwright.config.ts` if using different ports

4. **Authentication tests failing**:
   - Verify Clerk configuration
   - Check if test user accounts exist
   - Ensure authentication endpoints are accessible

5. **API tests failing**:
   - Verify backend is running and healthy
   - Check CORS configuration
   - Ensure database is properly initialized

### Debugging Tips

1. **Use headed mode** to see browser interactions:
   ```bash
   npx playwright test --headed
   ```

2. **Use debug mode** to pause execution:
   ```bash
   npx playwright test --debug
   ```

3. **Check screenshots** in `test-results/` after failures

4. **View detailed reports**:
   ```bash
   npx playwright show-report
   ```

## 📈 Test Data & Fixtures

### Test Users (`fixtures/test-users.ts`)

```typescript
const testUsers = {
  validUser: { email: 'test@orientor.com', password: 'TestPassword123!' },
  adminUser: { email: 'admin@orientor.com', password: 'AdminPassword123!' },
  newUser: { email: 'newuser@orientor.com', password: 'NewPassword123!' }
};
```

### Test Data

- Sample chat messages
- Skill node names  
- Career goals
- Assessment answers (neutral responses)

## 🎭 Test Scenarios Covered

### User Journeys

1. **New User Registration**:
   - Sign up → Profile setup → Assessment completion → Recommendations

2. **Returning User**:
   - Sign in → Dashboard → Chat interaction → Skill exploration

3. **Career Exploration**:
   - Assessment completion → Results analysis → Skill tree navigation → Career recommendations

4. **Learning Path**:
   - Skill gap analysis → Course recommendations → Progress tracking

### Edge Cases

- Network connectivity issues
- Large dataset handling
- Mobile responsive behavior
- Error state recovery
- Performance under load

## 📊 Reporting & Metrics

### Test Reports

- **HTML Report**: Interactive test results with screenshots
- **JSON Report**: Machine-readable test data
- **JUnit Report**: CI/CD integration compatible

### Metrics Tracked

- Test execution time
- Browser compatibility
- API response times
- UI interaction performance
- Error rates and types

## 🔄 Continuous Integration

### GitHub Actions Integration

```yaml
- name: Run Playwright Tests
  run: npm run test:ci
```

### Docker Support

```bash
npm run test:docker
```

## 🚀 Next Steps

1. **Run initial test suite** to verify setup
2. **Configure test data** for your specific environment
3. **Set up CI/CD integration** for automated testing
4. **Extend test coverage** for new features
5. **Monitor test performance** and optimize as needed

## 📝 Contributing

When adding new tests:

1. Follow existing naming conventions
2. Use appropriate test categories
3. Include proper error handling
4. Add test documentation
5. Verify cross-browser compatibility

---

## 🚨 Current Status

✅ **Completed**:
- Playwright installation and configuration
- Comprehensive test suite creation
- Test file organization
- Documentation

⚠️ **Needs Configuration**:
- Manual verification of test execution
- Environment-specific adjustments
- Test user account setup
- Backend service validation

The testing infrastructure is ready for use. Some configuration adjustments may be needed based on your specific environment setup.