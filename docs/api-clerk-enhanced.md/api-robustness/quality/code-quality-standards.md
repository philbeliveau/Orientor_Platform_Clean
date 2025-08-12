# Code Quality Standards - Orientor Platform

## Code Quality Audit Report

### 🟢 What's Good?

#### Frontend Strengths
- **Clerk Authentication Integration**: Proper use of `useAuth` hooks and `getToken()` methods
- **TypeScript Configuration**: Strict mode enabled with proper path mapping and modern module resolution
- **Service Layer Architecture**: Well-organized service files with clear separation of concerns
- **Environment Configuration**: Proper use of environment variables for API URLs
- **React Hooks Pattern**: Consistent use of custom hooks like `useClerkApi()`

#### Backend Strengths  
- **FastAPI Framework**: Modern async framework with automatic OpenAPI documentation
- **Pydantic Models**: Strong typing with request/response validation
- **Database Architecture**: SQLAlchemy ORM with proper session management
- **Authentication Caching**: Advanced JWKS caching system for performance
- **Router Organization**: 42 well-organized routers with clear separation of concerns
- **Security Headers**: Proper JWT token validation and authorization patterns

### 🔴 What's Broken?

#### Critical Issues Found

1. **Mixed API Client Patterns**
   ```typescript
   // Problem: Dual axios/fetch patterns in api.ts
   // File: /frontend/src/services/api.ts:70
   const response = await fetch(url, {
     ...fetchOptions,
     headers: { ...headers, ...fetchOptions?.headers },
   });
   
   // vs axios usage in same file:
   export const apiClient = axios.create({
     baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
   });
   ```

2. **Inconsistent Error Handling**
   ```typescript
   // Inconsistent redirect patterns
   window.location.href = '/sign-in'; // Hard redirect
   // vs proper router usage needed
   ```

3. **TypeScript Target Outdated**
   ```json
   // frontend/tsconfig.json - Line 3
   "target": "es5" // Should be ES2020+ for modern features
   ```

### 🟡 What Works But Shouldn't?

#### Technical Debt Items

1. **Minimal ESLint Rules**
   ```json
   // .eslintrc.json - Too permissive
   {
     "extends": ["next/core-web-vitals"],
     "rules": {
       "@next/next/no-img-element": "off",
       "react/no-unescaped-entities": "off",
       "prefer-const": "warn"
     }
   }
   ```
   **Issue**: Missing security, accessibility, and performance rules

2. **Service Layer Duplication**
   - Two API service patterns: `ClerkApiService` class and hook-based `useClerkApi`
   - Potential for inconsistent authentication handling

3. **Hardcoded Configuration**
   ```typescript
   timeout: 10000, // Should be configurable
   ```

### 🟠 What Doesn't Work But Pretends To?

#### Silent Failure Patterns

1. **Token Error Swallowing**
   ```typescript
   // clerkApi.ts:28 - Silent failure
   } catch (error) {
     console.warn('Failed to get authentication token:', error);
     // Continues without token - potential security issue
   }
   ```

2. **Missing Response Validation**
   - API responses not validated against schemas
   - Potential runtime errors from malformed data

## ESLint Configuration Standards

### Recommended .eslintrc.json
```json
{
  "extends": [
    "next/core-web-vitals",
    "@typescript-eslint/recommended",
    "plugin:security/recommended",
    "plugin:jsx-a11y/recommended"
  ],
  "plugins": [
    "@typescript-eslint",
    "security",
    "jsx-a11y",
    "react-hooks"
  ],
  "rules": {
    // Security Rules
    "security/detect-object-injection": "error",
    "security/detect-non-literal-fs-filename": "error",
    "security/detect-unsafe-regex": "error",
    
    // TypeScript Rules
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/no-explicit-any": "warn",
    "@typescript-eslint/explicit-function-return-type": "warn",
    "@typescript-eslint/no-non-null-assertion": "error",
    
    // React Rules
    "react-hooks/rules-of-hooks": "error",
    "react-hooks/exhaustive-deps": "warn",
    "react/prop-types": "off",
    "react/no-unescaped-entities": "error",
    
    // Code Quality
    "prefer-const": "error",
    "no-var": "error",
    "no-console": ["warn", { "allow": ["warn", "error"] }],
    "eqeqeq": ["error", "always"],
    "curly": ["error", "all"],
    
    // Performance
    "no-await-in-loop": "warn",
    "require-await": "warn"
  },
  "overrides": [
    {
      "files": ["**/*.test.ts", "**/*.test.tsx"],
      "rules": {
        "@typescript-eslint/no-explicit-any": "off",
        "security/detect-object-injection": "off"
      }
    }
  ]
}
```

## TypeScript Configuration Standards

### Enhanced tsconfig.json
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["dom", "dom.iterable", "ES2020"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    
    // Enhanced type checking
    "noImplicitReturns": true,
    "noImplicitOverride": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    
    // Path mapping
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"],
      "@/components/*": ["./src/components/*"],
      "@/services/*": ["./src/services/*"],
      "@/types/*": ["./src/types/*"],
      "@/utils/*": ["./src/utils/*"]
    },
    
    "plugins": [{ "name": "next" }],
    "typeRoots": ["./node_modules/@types", "./src/types"]
  },
  "include": [
    "next-env.d.ts",
    "**/*.ts",
    "**/*.tsx",
    ".next/types/**/*.ts",
    "src/types/**/*.d.ts"
  ],
  "exclude": ["node_modules"]
}
```

## Code Style Guidelines

### Naming Conventions
```typescript
// Components: PascalCase
export const UserProfile: React.FC = () => {};

// Hooks: camelCase with 'use' prefix
export const useClerkAuth = () => {};

// Services: camelCase with 'Service' suffix
export class AuthService {}

// Constants: SCREAMING_SNAKE_CASE
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;

// Files: kebab-case
// user-profile.tsx, auth-service.ts
```

### Function Organization
```typescript
// 1. Imports (grouped)
import React from 'react';
import { useAuth } from '@clerk/nextjs';

import { apiService } from '@/services/api';
import { UserProfile } from '@/types/user';

// 2. Type definitions
interface ComponentProps {
  userId: string;
}

// 3. Component/Function
export const UserComponent: React.FC<ComponentProps> = ({ userId }) => {
  // Hooks first
  const { getToken } = useAuth();
  
  // State and effects
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    // Effect logic
  }, []);
  
  // Event handlers
  const handleSubmit = async () => {
    // Handler logic
  };
  
  // Render
  return <div>{/* JSX */}</div>;
};
```

## Import Organization Standards

### Import Order
```typescript
// 1. React and external libraries
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '@clerk/nextjs';

// 2. Internal modules (absolute imports)
import { apiService } from '@/services/api';
import { UserProfile } from '@/types/user';
import { validateInput } from '@/utils/validation';

// 3. Relative imports
import './component.styles.css';
```

## Quality Gates

### Pre-commit Requirements
1. **ESLint**: Zero errors, warnings acceptable with justification
2. **TypeScript**: Strict compilation with no errors
3. **Tests**: All existing tests must pass
4. **Format**: Prettier formatting applied
5. **Commits**: Conventional commit format

### Build Requirements
1. **Bundle Size**: No increase >10% without justification
2. **Type Safety**: 100% TypeScript coverage
3. **Dependencies**: No new dependencies without security audit
4. **Performance**: Lighthouse scores maintained

## Recommended VS Code Settings

### .vscode/settings.json
```json
{
  "typescript.preferences.importModuleSpecifier": "relative",
  "typescript.preferences.includePackageJsonAutoImports": "on",
  "typescript.suggest.autoImports": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true,
    "source.organizeImports": true
  },
  "files.associations": {
    "*.css": "tailwindcss"
  },
  "emmet.includeLanguages": {
    "javascript": "javascriptreact"
  }
}
```

## Performance Standards

### Bundle Optimization
- Tree shaking enabled
- Dynamic imports for heavy components
- Service workers for caching
- Image optimization with Next.js Image component

### Code Splitting Strategy
```typescript
// Route-based splitting
const LazyComponent = lazy(() => import('./HeavyComponent'));

// Feature-based splitting
const AnalyticsModule = lazy(() => import('@/features/analytics'));
```

This represents the foundation of our code quality standards. Next, I'll create the API design guidelines.