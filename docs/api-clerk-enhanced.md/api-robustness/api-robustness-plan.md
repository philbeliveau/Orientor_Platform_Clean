# API Robustness & Standardization Implementation Plan
## Making Orientor Platform Endpoints Bulletproof

**Document Version:** 1.0  
**Created:** 2025-01-11  
**Last Updated:** 2025-01-11  
**Status:** Planning Phase  

---

## 🎯 Executive Summary

This document outlines a comprehensive plan to transform the Orientor Platform's API architecture from a fragile, inconsistent system to a bulletproof, self-healing infrastructure. The goal is to make it **impossible** for any single endpoint to deviate from established standards.

### Current Pain Points
- Manual endpoint construction leads to inconsistencies
- Multiple API utility files create confusion
- Authentication patterns vary across services
- No compile-time validation of endpoint correctness
- No automated detection of broken endpoints
- Developer freedom allows bypassing standards

### Target Outcomes
- **Zero endpoint drift** - Backend changes automatically update frontend
- **Impossible inconsistencies** - Compile-time errors prevent deployment
- **Self-healing system** - Automatic monitoring and error recovery
- **Developer productivity** - Type safety and auto-completion
- **Production reliability** - Comprehensive testing and monitoring

---

## 🏗️ Architecture Overview

### Current State Analysis
```
Frontend Services
├── utils/api.ts (centralized helper)
├── services/api.ts (redundant utilities)
├── services/avatarService.ts (mixed patterns)
├── services/careerGoalsService.ts (mixed patterns)
└── ... (inconsistent implementations)

Backend Routes
├── main.py (all routes with /api/v1 prefix ✅)
├── routers/*.py (consistent prefixes ✅)
└── ... (well-structured)
```

### Target Architecture
```
Centralized API System
├── Generated Client (from OpenAPI spec)
├── Single Source of Truth
├── Compile-time Validation
├── Runtime Monitoring
└── Automated Testing
```

---

## 📋 Implementation Phases

## **Phase 1: Foundation & Centralization (Weeks 1-2)**
*Priority: HIGH - Immediate Impact*

### 1.1 Consolidated API Client

**Objective:** Create single, authoritative API client that handles ALL requests.

**Implementation:**
```typescript
// src/api/client.ts
import { useAuth } from '@clerk/nextjs';

interface ApiEndpoint {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  path: string;
  requiresAuth?: boolean;
}

class OrientorApiClient {
  private static instance: OrientorApiClient;
  private baseUrl: string;
  
  // Singleton pattern prevents multiple instances
  private constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  }
  
  static getInstance(): OrientorApiClient {
    if (!OrientorApiClient.instance) {
      OrientorApiClient.instance = new OrientorApiClient();
    }
    return OrientorApiClient.instance;
  }
  
  // Centralized request method with consistent auth
  private async request<T>(
    endpoint: ApiEndpoint,
    data?: any,
    getToken?: () => Promise<string | null>
  ): Promise<T> {
    const url = `${this.baseUrl}/api/v1${endpoint.path}`;
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    
    // Standardized Clerk authentication
    if (endpoint.requiresAuth !== false && getToken) {
      const token = await getToken();
      if (!token) {
        window.location.href = '/sign-in';
        throw new Error('Authentication required');
      }
      headers.Authorization = `Bearer ${token}`;
    }
    
    const response = await fetch(url, {
      method: endpoint.method,
      headers,
      ...(data && endpoint.method !== 'GET' && { body: JSON.stringify(data) }),
    });
    
    if (!response.ok) {
      throw new ApiError(`${endpoint.method} ${endpoint.path}`, response.status, await response.text());
    }
    
    return response.json();
  }
  
  // Typed service methods
  async getUserAvatar(getToken: () => Promise<string | null>): Promise<AvatarData> {
    return this.request<AvatarData>({ method: 'GET', path: '/avatar/me' }, null, getToken);
  }
  
  async generateAvatar(getToken: () => Promise<string | null>): Promise<GenerateAvatarResponse> {
    return this.request<GenerateAvatarResponse>({ method: 'POST', path: '/avatar/generate-avatar/me' }, null, getToken);
  }
  
  async getActiveCareerGoal(getToken: () => Promise<string | null>): Promise<ActiveCareerGoalData> {
    return this.request<ActiveCareerGoalData>({ method: 'GET', path: '/career-goals/active' }, null, getToken);
  }
  
  async setCareerGoal(data: CareerGoalCreate, getToken: () => Promise<string | null>): Promise<CareerGoalResponse> {
    return this.request<CareerGoalResponse>({ method: 'POST', path: '/career-goals' }, data, getToken);
  }
  
  // Add all other endpoints here...
}

class ApiError extends Error {
  constructor(
    public endpoint: string,
    public status: number,
    public details: string
  ) {
    super(`API Error: ${endpoint} returned ${status}`);
  }
}

export { OrientorApiClient, ApiError };
```

**React Hook Integration:**
```typescript
// src/hooks/useOrientorApi.ts
import { useAuth } from '@clerk/nextjs';
import { OrientorApiClient } from '@/api/client';

export const useOrientorApi = () => {
  const { getToken } = useAuth();
  const client = OrientorApiClient.getInstance();
  
  return {
    // Avatar operations
    getUserAvatar: () => client.getUserAvatar(getToken),
    generateAvatar: () => client.generateAvatar(getToken),
    
    // Career Goals operations
    getActiveCareerGoal: () => client.getActiveCareerGoal(getToken),
    setCareerGoal: (data: CareerGoalCreate) => client.setCareerGoal(data, getToken),
    
    // Add more as needed...
  };
};
```

### 1.2 ESLint Rules for Enforcement

**Objective:** Prevent developers from bypassing the centralized system.

**Configuration:**
```json
// .eslintrc.js
{
  "rules": {
    "no-restricted-imports": [
      "error",
      {
        "patterns": [
          {
            "group": ["**/fetch", "**/axios"],
            "message": "Use OrientorApiClient.getInstance() instead of direct HTTP calls"
          }
        ]
      }
    ],
    "no-restricted-globals": [
      "error",
      {
        "name": "fetch",
        "message": "Use OrientorApiClient.getInstance() instead of global fetch"
      }
    ],
    "no-restricted-syntax": [
      "error",
      {
        "selector": "CallExpression[callee.name='fetch']",
        "message": "Direct fetch calls are not allowed. Use OrientorApiClient.getInstance()"
      }
    ]
  },
  "overrides": [
    {
      "files": ["src/api/client.ts"],
      "rules": {
        "no-restricted-globals": "off",
        "no-restricted-syntax": "off"
      }
    }
  ]
}
```

### 1.3 TypeScript Strict Typing

**Objective:** Compile-time validation of all API interactions.

**Type Definitions:**
```typescript
// src/api/types.ts
export interface AvatarData {
  success: boolean;
  message?: string;
  avatar_name?: string;
  avatar_description?: string;
  avatar_image_url?: string;
  generated_at?: string;
}

export interface GenerateAvatarResponse {
  success: boolean;
  message: string;
  avatar_name: string;
  avatar_description: string;
  avatar_image_url: string;
  generated_at: string;
}

export interface CareerGoal {
  id: number;
  user_id: number;
  esco_occupation_id?: string;
  oasis_code?: string;
  title: string;
  description?: string;
  target_date: string;
  is_active: boolean;
  progress_percentage: number;
  created_at: string;
  updated_at: string;
  achieved_at?: string;
  source?: string;
  milestones_count?: number;
  completed_milestones?: number;
}

export interface CareerGoalCreate {
  esco_occupation_id?: string;
  oasis_code?: string;
  title: string;
  description?: string;
  target_date?: string;
  source?: string;
  source_metadata?: Record<string, any>;
}

export interface ActiveCareerGoalData {
  goal: CareerGoal | null;
  progression: any;
  milestones: any[];
  message: string;
}

export interface CareerGoalResponse {
  goal: CareerGoal;
  timeline: any;
  message: string;
}

// Endpoint mapping for type safety
export interface ApiEndpoints {
  '/avatar/me': {
    GET: { response: AvatarData };
  };
  '/avatar/generate-avatar/me': {
    POST: { response: GenerateAvatarResponse };
  };
  '/career-goals/active': {
    GET: { response: ActiveCareerGoalData };
  };
  '/career-goals': {
    POST: { body: CareerGoalCreate; response: CareerGoalResponse };
  };
  // Add all endpoints here...
}
```

### 1.4 Migration from Current Services

**Strategy:** Gradual replacement with backwards compatibility.

**Step 1 - Update AvatarService:**
```typescript
// src/services/avatarService.ts - UPDATED
import { useOrientorApi } from '@/hooks/useOrientorApi';

export class AvatarService {
  // Replace with hook-based approach
  static useAvatarOperations() {
    const api = useOrientorApi();
    
    return {
      getUserAvatar: api.getUserAvatar,
      generateAvatar: api.generateAvatar,
      hasAvatar: async () => {
        try {
          const avatarData = await api.getUserAvatar();
          return avatarData.success && !!avatarData.avatar_name;
        } catch {
          return false;
        }
      }
    };
  }
  
  // Legacy methods - DEPRECATED
  /** @deprecated Use useAvatarOperations() hook instead */
  static async getUserAvatar(getToken: () => Promise<string | null>) {
    const client = OrientorApiClient.getInstance();
    return client.getUserAvatar(getToken);
  }
}
```

**Step 2 - Update CareerGoalsService:**
```typescript
// src/services/careerGoalsService.ts - UPDATED
import { useOrientorApi } from '@/hooks/useOrientorApi';

export class CareerGoalsService {
  static useCareerGoalsOperations() {
    const api = useOrientorApi();
    
    return {
      getActiveCareerGoal: api.getActiveCareerGoal,
      setCareerGoalFromJob: api.setCareerGoal,
      // Add other operations...
    };
  }
  
  // Legacy methods - DEPRECATED
  /** @deprecated Use useCareerGoalsOperations() hook instead */
  static async getActiveCareerGoal(getToken: () => Promise<string>) {
    const client = OrientorApiClient.getInstance();
    return client.getActiveCareerGoal(getToken);
  }
}
```

---

## **Phase 2: Automated Code Generation (Weeks 3-4)**
*Priority: MEDIUM - Prevents Future Regressions*

### 2.1 Backend OpenAPI Specification

**Objective:** Generate authoritative API contract from FastAPI routes.

**Implementation:**
```python
# backend/scripts/generate_openapi.py
import json
from pathlib import Path
from fastapi.openapi.utils import get_openapi
from app.main import app

def generate_openapi_spec():
    """Generate OpenAPI specification from FastAPI app"""
    openapi_schema = get_openapi(
        title="Orientor Platform API",
        version="1.0.0",
        description="Comprehensive API for the Orientor Career Guidance Platform",
        routes=app.routes,
    )
    
    # Save to frontend directory for client generation
    frontend_path = Path("../frontend/api-spec.json")
    with open(frontend_path, "w") as f:
        json.dump(openapi_schema, f, indent=2)
    
    print(f"✅ OpenAPI spec generated: {frontend_path}")
    return openapi_schema

if __name__ == "__main__":
    generate_openapi_spec()
```

**Package.json Integration:**
```json
{
  "scripts": {
    "generate-api-spec": "cd backend && python scripts/generate_openapi.py",
    "generate-api-client": "openapi-typescript api-spec.json --output src/api/generated-types.ts",
    "build-api": "npm run generate-api-spec && npm run generate-api-client"
  },
  "devDependencies": {
    "openapi-typescript": "^6.0.0"
  }
}
```

### 2.2 Automated Client Generation

**Generated Types:**
```typescript
// src/api/generated-types.ts (auto-generated)
export interface paths {
  "/api/v1/avatar/me": {
    get: operations["get_user_avatar"];
  };
  "/api/v1/avatar/generate-avatar/me": {
    post: operations["generate_avatar"];
  };
  "/api/v1/career-goals/active": {
    get: operations["get_active_career_goal"];
  };
  "/api/v1/career-goals": {
    post: operations["create_career_goal"];
  };
}

export interface operations {
  get_user_avatar: {
    responses: {
      200: {
        content: {
          "application/json": components["schemas"]["AvatarData"];
        };
      };
    };
  };
  generate_avatar: {
    responses: {
      200: {
        content: {
          "application/json": components["schemas"]["GenerateAvatarResponse"];
        };
      };
    };
  };
  // ... etc
}

export interface components {
  schemas: {
    AvatarData: {
      success: boolean;
      message?: string;
      avatar_name?: string;
      avatar_description?: string;
      avatar_image_url?: string;
      generated_at?: string;
    };
    // ... etc
  };
}
```

### 2.3 Pre-commit Validation

**Git Hooks:**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: api-spec-sync
        name: Validate API specification is synchronized
        entry: ./scripts/validate-api-sync.sh
        language: system
        files: '^(backend/app/routers/.*\.py|frontend/src/api/.*)$'
        
      - id: eslint-api-usage
        name: Validate API usage patterns
        entry: npx eslint
        language: node
        files: '^frontend/src/.*\.(ts|tsx)$'
        args: ['--rule', 'no-restricted-imports:error']
```

**Validation Script:**
```bash
#!/bin/bash
# scripts/validate-api-sync.sh

echo "🔍 Validating API specification synchronization..."

# Generate current spec
cd backend && python scripts/generate_openapi.py

# Check if frontend types are up to date
cd ../frontend
npm run generate-api-client

# Check for uncommitted changes
if git diff --quiet api-spec.json src/api/generated-types.ts; then
    echo "✅ API specification is synchronized"
    exit 0
else
    echo "❌ API specification is out of sync!"
    echo "Run 'npm run build-api' to update generated types"
    exit 1
fi
```

---

## **Phase 3: Runtime Monitoring & Validation (Weeks 5-6)**
*Priority: MEDIUM - Production Reliability*

### 3.1 Request/Response Interceptors

**Objective:** Validate all API interactions at runtime.

**Implementation:**
```typescript
// src/api/interceptors.ts
import Ajv from 'ajv';
import { ApiError } from './client';

interface ApiSchema {
  request?: any;
  response?: any;
}

class ApiInterceptor {
  private static ajv = new Ajv();
  private static schemas = new Map<string, ApiSchema>();
  
  static registerSchema(endpoint: string, schema: ApiSchema) {
    this.schemas.set(endpoint, schema);
  }
  
  static validateRequest(endpoint: string, data: any): boolean {
    const schema = this.schemas.get(endpoint)?.request;
    if (!schema) return true; // Skip validation if no schema
    
    const isValid = this.ajv.validate(schema, data);
    if (!isValid) {
      console.error(`❌ Request validation failed for ${endpoint}:`, this.ajv.errors);
      throw new ApiError(endpoint, 400, 'Invalid request data');
    }
    return true;
  }
  
  static validateResponse(endpoint: string, data: any): boolean {
    const schema = this.schemas.get(endpoint)?.response;
    if (!schema) return true; // Skip validation if no schema
    
    const isValid = this.ajv.validate(schema, data);
    if (!isValid) {
      console.error(`❌ Response validation failed for ${endpoint}:`, this.ajv.errors);
      // Don't throw - log and continue with potentially invalid data
    }
    return isValid;
  }
  
  static handleError(error: ApiError): void {
    // Centralized error handling
    switch (error.status) {
      case 404:
        console.error(`🚨 Endpoint not found: ${error.endpoint}`);
        this.logEndpointNotFound(error.endpoint);
        break;
        
      case 401:
        console.error(`🔐 Authentication failed for: ${error.endpoint}`);
        window.location.href = '/sign-in';
        break;
        
      case 500:
        console.error(`💥 Server error: ${error.endpoint}`);
        this.logServerError(error);
        break;
        
      default:
        console.error(`❌ API error: ${error.endpoint}`, error);
    }
  }
  
  private static logEndpointNotFound(endpoint: string) {
    // Send to analytics/monitoring service
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', 'api_endpoint_not_found', {
        endpoint,
        timestamp: new Date().toISOString(),
      });
    }
  }
  
  private static logServerError(error: ApiError) {
    // Send to error reporting service (e.g., Sentry)
    if (typeof window !== 'undefined' && (window as any).Sentry) {
      (window as any).Sentry.captureException(error);
    }
  }
}

export { ApiInterceptor };
```

### 3.2 Health Check System

**Objective:** Proactive monitoring of endpoint availability.

**Implementation:**
```typescript
// src/api/health-monitor.ts
interface HealthCheckResult {
  endpoint: string;
  status: 'healthy' | 'degraded' | 'unhealthy';
  responseTime: number;
  error?: string;
}

interface HealthReport {
  timestamp: string;
  overall: 'healthy' | 'degraded' | 'unhealthy';
  total: number;
  healthy: number;
  degraded: number;
  unhealthy: number;
  results: HealthCheckResult[];
}

class EndpointHealthMonitor {
  private static instance: EndpointHealthMonitor;
  private healthResults = new Map<string, HealthCheckResult>();
  private monitoringInterval?: NodeJS.Timeout;
  
  static getInstance(): EndpointHealthMonitor {
    if (!EndpointHealthMonitor.instance) {
      EndpointHealthMonitor.instance = new EndpointHealthMonitor();
    }
    return EndpointHealthMonitor.instance;
  }
  
  async checkEndpoint(endpoint: string): Promise<HealthCheckResult> {
    const startTime = performance.now();
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1${endpoint}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });
      
      const responseTime = performance.now() - startTime;
      const status = response.ok ? 'healthy' : 
                    response.status < 500 ? 'degraded' : 'unhealthy';
      
      const result: HealthCheckResult = {
        endpoint,
        status,
        responseTime,
        ...(response.ok ? {} : { error: `HTTP ${response.status}` }),
      };
      
      this.healthResults.set(endpoint, result);
      return result;
      
    } catch (error) {
      const responseTime = performance.now() - startTime;
      const result: HealthCheckResult = {
        endpoint,
        status: 'unhealthy',
        responseTime,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
      
      this.healthResults.set(endpoint, result);
      return result;
    }
  }
  
  async checkAllEndpoints(): Promise<HealthReport> {
    const endpoints = [
      '/avatar/me',
      '/career-goals/active',
      '/profiles/me',
      '/peers/compatible',
      '/tests/holland/user-results',
      '/tests/hexaco/user-results',
      // Add all critical endpoints
    ];
    
    const results = await Promise.all(
      endpoints.map(endpoint => this.checkEndpoint(endpoint))
    );
    
    const healthy = results.filter(r => r.status === 'healthy').length;
    const degraded = results.filter(r => r.status === 'degraded').length;
    const unhealthy = results.filter(r => r.status === 'unhealthy').length;
    
    const overall = unhealthy > 0 ? 'unhealthy' : 
                   degraded > 0 ? 'degraded' : 'healthy';
    
    return {
      timestamp: new Date().toISOString(),
      overall,
      total: results.length,
      healthy,
      degraded,
      unhealthy,
      results,
    };
  }
  
  startMonitoring(intervalMs: number = 60000): void {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
    }
    
    this.monitoringInterval = setInterval(async () => {
      const report = await this.checkAllEndpoints();
      
      if (report.overall !== 'healthy') {
        console.warn('🚨 API Health Check Alert:', report);
        this.sendHealthAlert(report);
      }
    }, intervalMs);
  }
  
  stopMonitoring(): void {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = undefined;
    }
  }
  
  private sendHealthAlert(report: HealthReport): void {
    // Send to monitoring service
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', 'api_health_alert', {
        overall_status: report.overall,
        unhealthy_count: report.unhealthy,
        degraded_count: report.degraded,
      });
    }
  }
}

export { EndpointHealthMonitor, type HealthReport };
```

### 3.3 Real-time Alerting

**Implementation:**
```typescript
// src/api/alert-system.ts
interface AlertConfig {
  enableConsoleAlerts: boolean;
  enableAnalyticsReporting: boolean;
  enableSlackWebhook: boolean;
  slackWebhookUrl?: string;
}

class AlertSystem {
  private static config: AlertConfig = {
    enableConsoleAlerts: true,
    enableAnalyticsReporting: true,
    enableSlackWebhook: false,
  };
  
  static configure(config: Partial<AlertConfig>): void {
    this.config = { ...this.config, ...config };
  }
  
  static async onEndpointFailure(endpoint: string, error: Error): Promise<void> {
    const isProduction = process.env.NODE_ENV === 'production';
    const message = `🚨 Endpoint Failure: ${endpoint} - ${error.message}`;
    
    if (this.config.enableConsoleAlerts) {
      console.error(message, error);
    }
    
    if (this.config.enableAnalyticsReporting) {
      this.reportToAnalytics('endpoint_failure', {
        endpoint,
        error: error.message,
        timestamp: new Date().toISOString(),
      });
    }
    
    if (isProduction && this.config.enableSlackWebhook && this.config.slackWebhookUrl) {
      await this.sendSlackAlert(message, error);
    }
  }
  
  static async onHealthDegradation(report: any): Promise<void> {
    const message = `⚠️ API Health Degraded: ${report.unhealthy} unhealthy, ${report.degraded} degraded`;
    
    if (this.config.enableConsoleAlerts) {
      console.warn(message, report);
    }
    
    if (this.config.enableAnalyticsReporting) {
      this.reportToAnalytics('api_health_degraded', {
        overall_status: report.overall,
        unhealthy_count: report.unhealthy,
        degraded_count: report.degraded,
        timestamp: report.timestamp,
      });
    }
  }
  
  private static reportToAnalytics(eventName: string, data: Record<string, any>): void {
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', eventName, data);
    }
  }
  
  private static async sendSlackAlert(message: string, error?: Error): Promise<void> {
    if (!this.config.slackWebhookUrl) return;
    
    try {
      await fetch(this.config.slackWebhookUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: message,
          attachments: error ? [{
            color: 'danger',
            fields: [
              { title: 'Error', value: error.message, short: false },
              { title: 'Stack', value: error.stack?.substring(0, 500), short: false },
            ],
          }] : [],
        }),
      });
    } catch (slackError) {
      console.error('Failed to send Slack alert:', slackError);
    }
  }
}

export { AlertSystem };
```

---

## **Phase 4: Comprehensive Testing (Weeks 7-8)**
*Priority: HIGH - Bulletproof Reliability*

### 4.1 Contract Testing

**Objective:** Ensure frontend and backend always remain compatible.

**Installation:**
```bash
npm install --save-dev @pact-foundation/pact
```

**Implementation:**
```typescript
// src/tests/contracts/avatar.contract.test.ts
import { Pact, Matchers } from '@pact-foundation/pact';
import { OrientorApiClient } from '@/api/client';

describe('Avatar API Contract', () => {
  let provider: Pact;
  
  beforeAll(async () => {
    provider = new Pact({
      consumer: 'orientor-frontend',
      provider: 'orientor-backend',
      port: 1234,
      log: path.resolve(process.cwd(), 'logs', 'pact.log'),
      dir: path.resolve(process.cwd(), 'pacts'),
    });
    
    await provider.setup();
  });
  
  afterAll(async () => {
    await provider.finalize();
  });
  
  describe('GET /api/v1/avatar/me', () => {
    beforeEach(async () => {
      await provider.addInteraction({
        state: 'user has avatar',
        uponReceiving: 'get user avatar request',
        withRequest: {
          method: 'GET',
          path: '/api/v1/avatar/me',
          headers: {
            'Authorization': Matchers.regex('Bearer .*', 'Bearer token123'),
            'Content-Type': 'application/json',
          },
        },
        willRespondWith: {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
          body: Matchers.like({
            success: true,
            avatar_name: 'Test Avatar',
            avatar_description: 'A test avatar description',
            avatar_image_url: '/static/avatars/test.png',
            generated_at: '2023-01-01T00:00:00Z',
          }),
        },
      });
    });
    
    it('should return user avatar data', async () => {
      const client = OrientorApiClient.getInstance();
      const mockGetToken = jest.fn().mockResolvedValue('token123');
      
      const result = await client.getUserAvatar(mockGetToken);
      
      expect(result).toMatchObject({
        success: true,
        avatar_name: expect.any(String),
        avatar_description: expect.any(String),
      });
    });
  });
  
  describe('POST /api/v1/avatar/generate-avatar/me', () => {
    beforeEach(async () => {
      await provider.addInteraction({
        state: 'user can generate avatar',
        uponReceiving: 'generate avatar request',
        withRequest: {
          method: 'POST',
          path: '/api/v1/avatar/generate-avatar/me',
          headers: {
            'Authorization': Matchers.regex('Bearer .*', 'Bearer token123'),
            'Content-Type': 'application/json',
          },
        },
        willRespondWith: {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
          body: Matchers.like({
            success: true,
            message: 'Avatar generated successfully',
            avatar_name: 'Generated Avatar',
            avatar_description: 'A generated avatar description',
            avatar_image_url: '/static/avatars/generated.png',
            generated_at: '2023-01-01T00:00:00Z',
          }),
        },
      });
    });
    
    it('should generate new avatar', async () => {
      const client = OrientorApiClient.getInstance();
      const mockGetToken = jest.fn().mockResolvedValue('token123');
      
      const result = await client.generateAvatar(mockGetToken);
      
      expect(result).toMatchObject({
        success: true,
        message: expect.any(String),
        avatar_name: expect.any(String),
      });
    });
  });
});
```

### 4.2 Integration Test Suite

**Objective:** Validate every endpoint with real backend.

**Implementation:**
```typescript
// src/tests/integration/api.integration.test.ts
import { OrientorApiClient } from '@/api/client';

describe('API Integration Tests', () => {
  let client: OrientorApiClient;
  let mockGetToken: jest.Mock;
  
  beforeAll(() => {
    client = OrientorApiClient.getInstance();
    mockGetToken = jest.fn().mockResolvedValue('valid-jwt-token');
  });
  
  describe('Avatar Endpoints', () => {
    it('should handle avatar retrieval', async () => {
      const result = await client.getUserAvatar(mockGetToken);
      expect(result).toHaveProperty('success');
      expect(typeof result.success).toBe('boolean');
    });
    
    it('should handle avatar generation', async () => {
      const result = await client.generateAvatar(mockGetToken);
      expect(result).toHaveProperty('success');
      expect(result).toHaveProperty('message');
    });
  });
  
  describe('Career Goals Endpoints', () => {
    it('should handle active goal retrieval', async () => {
      const result = await client.getActiveCareerGoal(mockGetToken);
      expect(result).toHaveProperty('goal');
      expect(result).toHaveProperty('progression');
      expect(result).toHaveProperty('milestones');
    });
    
    it('should handle goal creation', async () => {
      const goalData = {
        title: 'Test Career Goal',
        description: 'A test career goal',
        target_date: '2024-12-31',
      };
      
      const result = await client.setCareerGoal(goalData, mockGetToken);
      expect(result).toHaveProperty('goal');
      expect(result).toHaveProperty('message');
    });
  });
  
  describe('Error Handling', () => {
    it('should handle 401 authentication errors', async () => {
      const invalidTokenFn = jest.fn().mockResolvedValue(null);
      
      await expect(client.getUserAvatar(invalidTokenFn))
        .rejects.toThrow('Authentication required');
    });
    
    it('should handle 404 endpoint errors', async () => {
      // Mock a non-existent endpoint
      const invalidClient = new (OrientorApiClient as any)();
      invalidClient.request = jest.fn().mockRejectedValue(
        new Response(null, { status: 404 })
      );
      
      await expect(invalidClient.getUserAvatar(mockGetToken))
        .rejects.toThrow();
    });
  });
});
```

### 4.3 End-to-End Authentication Flow

**Objective:** Verify complete user journey works correctly.

**Installation:**
```bash
npm install --save-dev @playwright/test
```

**Implementation:**
```typescript
// src/tests/e2e/authentication-flow.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Set up authentication state
    await page.goto('/');
  });
  
  test('complete user journey with API calls', async ({ page }) => {
    // Navigate to dashboard
    await page.goto('/dashboard');
    
    // Wait for authentication to complete
    await expect(page.locator('[data-testid="user-avatar"]')).toBeVisible({ timeout: 10000 });
    
    // Verify avatar API call worked
    const avatarElement = page.locator('[data-testid="user-avatar"]');
    await expect(avatarElement).not.toHaveAttribute('src', '');
    
    // Navigate to career goals
    await page.click('[data-testid="career-goals-tab"]');
    await expect(page.locator('[data-testid="career-goals-content"]')).toBeVisible();
    
    // Verify career goals API call worked
    const goalElement = page.locator('[data-testid="active-goal"]');
    if (await goalElement.isVisible()) {
      await expect(goalElement).toContainText(/\w+/); // Contains some text
    }
    
    // Test API error handling
    await page.route('**/api/v1/avatar/me', route => {
      route.fulfill({ status: 500, body: 'Server Error' });
    });
    
    await page.reload();
    
    // Should handle API error gracefully
    await expect(page.locator('[data-testid="error-message"]')).not.toBeVisible();
  });
  
  test('authentication redirect flow', async ({ page }) => {
    // Mock unauthenticated state
    await page.route('**/api/v1/**', route => {
      route.fulfill({ status: 401, body: 'Unauthorized' });
    });
    
    await page.goto('/dashboard');
    
    // Should redirect to sign-in page
    await expect(page).toHaveURL(/.*\/sign-in.*/);
  });
});
```

### 4.4 Performance Testing

**Objective:** Ensure API performance meets requirements.

**Implementation:**
```typescript
// src/tests/performance/api.performance.test.ts
describe('API Performance Tests', () => {
  let client: OrientorApiClient;
  let mockGetToken: jest.Mock;
  
  beforeAll(() => {
    client = OrientorApiClient.getInstance();
    mockGetToken = jest.fn().mockResolvedValue('valid-jwt-token');
  });
  
  describe('Response Time Requirements', () => {
    it('avatar retrieval should complete within 2 seconds', async () => {
      const startTime = performance.now();
      
      await client.getUserAvatar(mockGetToken);
      
      const endTime = performance.now();
      const responseTime = endTime - startTime;
      
      expect(responseTime).toBeLessThan(2000);
    });
    
    it('career goals retrieval should complete within 1 second', async () => {
      const startTime = performance.now();
      
      await client.getActiveCareerGoal(mockGetToken);
      
      const endTime = performance.now();
      const responseTime = endTime - startTime;
      
      expect(responseTime).toBeLessThan(1000);
    });
  });
  
  describe('Concurrent Request Handling', () => {
    it('should handle 10 concurrent avatar requests', async () => {
      const requests = Array(10).fill(null).map(() => 
        client.getUserAvatar(mockGetToken)
      );
      
      const startTime = performance.now();
      const results = await Promise.all(requests);
      const endTime = performance.now();
      
      expect(results).toHaveLength(10);
      expect(results.every(r => r.success !== undefined)).toBe(true);
      expect(endTime - startTime).toBeLessThan(5000); // All within 5 seconds
    });
  });
});
```

---

## 📊 Monitoring & Observability

### Development Monitoring

**Console Integration:**
```typescript
// src/api/dev-monitor.ts
class DevelopmentMonitor {
  static logApiCall(endpoint: string, method: string, responseTime: number, status: number) {
    const emoji = status < 300 ? '✅' : status < 500 ? '⚠️' : '❌';
    const color = status < 300 ? 'color: green' : status < 500 ? 'color: orange' : 'color: red';
    
    console.groupCollapsed(
      `${emoji} %c${method} ${endpoint} %c${status} %c(${responseTime.toFixed(0)}ms)`,
      'font-weight: bold',
      `${color}; font-weight: bold`,
      'color: gray'
    );
    
    console.log('URL:', `${process.env.NEXT_PUBLIC_API_URL}/api/v1${endpoint}`);
    console.log('Response Time:', `${responseTime.toFixed(2)}ms`);
    console.log('Status:', status);
    
    if (status >= 400) {
      console.error('Error occurred in API call');
    }
    
    console.groupEnd();
  }
}

export { DevelopmentMonitor };
```

### Production Analytics

**Google Analytics Integration:**
```typescript
// src/api/analytics.ts
interface ApiMetrics {
  endpoint: string;
  method: string;
  status: number;
  responseTime: number;
  userAgent: string;
  timestamp: string;
}

class ApiAnalytics {
  static trackApiCall(metrics: ApiMetrics) {
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', 'api_call', {
        event_category: 'API',
        event_label: `${metrics.method} ${metrics.endpoint}`,
        custom_map: {
          custom1: 'response_time',
          custom2: 'status_code',
        },
        custom1: Math.round(metrics.responseTime),
        custom2: metrics.status,
        non_interaction: true,
      });
      
      // Track errors separately
      if (metrics.status >= 400) {
        window.gtag('event', 'api_error', {
          event_category: 'Error',
          event_label: `${metrics.status} ${metrics.endpoint}`,
          value: metrics.status,
        });
      }
    }
  }
  
  static trackEndpointHealth(healthReport: any) {
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', 'api_health_check', {
        event_category: 'System',
        event_label: 'Endpoint Health',
        custom_map: {
          custom1: 'healthy_count',
          custom2: 'unhealthy_count',
        },
        custom1: healthReport.healthy,
        custom2: healthReport.unhealthy,
      });
    }
  }
}

export { ApiAnalytics, type ApiMetrics };
```

---

## 🚀 Deployment & CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/api-validation.yml
name: API Validation & Testing

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  api-contract-validation:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install Frontend Dependencies
      working-directory: ./frontend
      run: npm ci
    
    - name: Install Backend Dependencies
      working-directory: ./backend
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Generate API Specification
      working-directory: ./backend
      run: python scripts/generate_openapi.py
    
    - name: Generate TypeScript Client
      working-directory: ./frontend
      run: npm run generate-api-client
    
    - name: Validate API Contract
      working-directory: ./frontend
      run: npm run test:contracts
    
    - name: Run Integration Tests
      working-directory: ./frontend
      run: npm run test:integration
      env:
        API_URL: http://localhost:8000
    
    - name: Run E2E Tests
      working-directory: ./frontend
      run: npm run test:e2e
      env:
        BASE_URL: http://localhost:3000
    
    - name: Upload Test Results
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: test-results
        path: |
          frontend/test-results/
          frontend/pacts/
```

### Pre-deployment Validation

```bash
#!/bin/bash
# scripts/pre-deploy-validation.sh

echo "🚀 Starting pre-deployment API validation..."

# Step 1: Generate fresh API specification
echo "📋 Generating API specification..."
cd backend && python scripts/generate_openapi.py
if [ $? -ne 0 ]; then
    echo "❌ Failed to generate API specification"
    exit 1
fi

# Step 2: Update TypeScript client
echo "🔧 Updating TypeScript client..."
cd ../frontend && npm run generate-api-client
if [ $? -ne 0 ]; then
    echo "❌ Failed to generate TypeScript client"
    exit 1
fi

# Step 3: Run contract tests
echo "🧪 Running contract tests..."
npm run test:contracts
if [ $? -ne 0 ]; then
    echo "❌ Contract tests failed"
    exit 1
fi

# Step 4: Run integration tests
echo "🔗 Running integration tests..."
npm run test:integration
if [ $? -ne 0 ]; then
    echo "❌ Integration tests failed"
    exit 1
fi

# Step 5: Validate endpoint health
echo "💊 Validating endpoint health..."
npm run health-check:all
if [ $? -ne 0 ]; then
    echo "❌ Endpoint health check failed"
    exit 1
fi

echo "✅ All pre-deployment validations passed!"
echo "🚢 Safe to deploy!"
```

---

## 📈 Success Metrics

### Key Performance Indicators

**Reliability Metrics:**
- **API Error Rate:** < 1% (target: 0.1%)
- **Endpoint Availability:** > 99.9%
- **Authentication Success Rate:** > 99.5%
- **Response Time P95:** < 2 seconds
- **Response Time P99:** < 5 seconds

**Development Metrics:**
- **Time to Add New Endpoint:** < 30 minutes
- **Contract Test Coverage:** 100%
- **Integration Test Coverage:** 100%
- **Deployment Confidence:** 100% (zero rollbacks due to API issues)

**Code Quality Metrics:**
- **TypeScript Strict Mode:** 100% compliance
- **ESLint API Rules:** 0 violations
- **Dead Code:** 0 unreachable endpoints
- **Documentation Coverage:** 100% of endpoints documented

### Monitoring Dashboard

Create a simple monitoring dashboard:

```typescript
// src/pages/admin/api-dashboard.tsx
import React, { useEffect, useState } from 'react';
import { EndpointHealthMonitor } from '@/api/health-monitor';

export default function ApiDashboard() {
  const [healthReport, setHealthReport] = useState(null);
  
  useEffect(() => {
    const monitor = EndpointHealthMonitor.getInstance();
    
    const updateHealth = async () => {
      const report = await monitor.checkAllEndpoints();
      setHealthReport(report);
    };
    
    updateHealth();
    const interval = setInterval(updateHealth, 30000); // Update every 30 seconds
    
    return () => clearInterval(interval);
  }, []);
  
  if (!healthReport) return <div>Loading...</div>;
  
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">API Health Dashboard</h1>
      
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-lg font-semibold">Overall Status</h3>
          <p className={`text-2xl font-bold ${
            healthReport.overall === 'healthy' ? 'text-green-500' :
            healthReport.overall === 'degraded' ? 'text-yellow-500' : 'text-red-500'
          }`}>
            {healthReport.overall.toUpperCase()}
          </p>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-lg font-semibold">Healthy</h3>
          <p className="text-2xl font-bold text-green-500">{healthReport.healthy}</p>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-lg font-semibold">Degraded</h3>
          <p className="text-2xl font-bold text-yellow-500">{healthReport.degraded}</p>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-lg font-semibold">Unhealthy</h3>
          <p className="text-2xl font-bold text-red-500">{healthReport.unhealthy}</p>
        </div>
      </div>
      
      <div className="bg-white rounded-lg shadow">
        <div className="p-4 border-b">
          <h2 className="text-xl font-semibold">Endpoint Details</h2>
        </div>
        <div className="divide-y">
          {healthReport.results.map((result, index) => (
            <div key={index} className="p-4 flex justify-between items-center">
              <div>
                <span className="font-mono text-sm">{result.endpoint}</span>
                {result.error && (
                  <p className="text-red-500 text-sm mt-1">{result.error}</p>
                )}
              </div>
              <div className="text-right">
                <div className={`inline-block px-2 py-1 rounded text-sm font-medium ${
                  result.status === 'healthy' ? 'bg-green-100 text-green-800' :
                  result.status === 'degraded' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {result.status}
                </div>
                <p className="text-gray-500 text-sm mt-1">
                  {result.responseTime.toFixed(0)}ms
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
```

---

## 🎯 Migration Strategy

### Phase-by-Phase Migration

**Week 1-2: Foundation**
1. Create centralized `OrientorApiClient`
2. Add ESLint rules to prevent bypass
3. Update 2-3 critical services (Avatar, Career Goals)
4. Test with existing functionality

**Week 3-4: Automation**
1. Set up OpenAPI generation pipeline
2. Create TypeScript client generation
3. Add pre-commit hooks
4. Migrate remaining services

**Week 5-6: Monitoring**
1. Add request/response interceptors
2. Implement health monitoring
3. Set up alerting system
4. Create admin dashboard

**Week 7-8: Testing**
1. Write contract tests for all endpoints
2. Create comprehensive integration tests
3. Add E2E authentication flow tests
4. Performance test critical paths

### Risk Mitigation

**Backwards Compatibility:**
- Keep old services functional during migration
- Use feature flags for gradual rollout
- Implement rollback procedures

**Testing Strategy:**
- Test each migrated service thoroughly
- Use staging environment for validation
- Gradual production rollout

**Monitoring:**
- Monitor error rates during migration
- Set up alerts for regression detection
- Track user experience metrics

---

## 🔮 Future Enhancements

### Advanced Features (Post-Implementation)

1. **GraphQL Integration**
   - Unified query interface
   - Reduced over-fetching
   - Real-time subscriptions

2. **Caching Strategy**
   - Response caching with TTL
   - Optimistic updates
   - Cache invalidation strategies

3. **Offline Support**
   - Service worker integration
   - Offline queue for mutations
   - Sync when back online

4. **Advanced Error Handling**
   - Exponential backoff retry
   - Circuit breaker pattern
   - Fallback responses

5. **Performance Optimization**
   - Request batching
   - Connection pooling
   - Response compression

---

## 📚 Resources & References

### Documentation
- [FastAPI OpenAPI Documentation](https://fastapi.tiangolo.com/advanced/extending-openapi/)
- [TypeScript API Client Generation](https://openapi-ts.pages.dev/)
- [Pact Contract Testing](https://docs.pact.io/)
- [Playwright E2E Testing](https://playwright.dev/)

### Tools & Libraries
- **openapi-typescript:** Generate TypeScript types from OpenAPI spec
- **@pact-foundation/pact:** Contract testing framework
- **@playwright/test:** E2E testing framework
- **ajv:** JSON schema validation

### Best Practices
- [API Design Guidelines](https://github.com/microsoft/api-guidelines)
- [TypeScript Best Practices](https://typescript-eslint.io/rules/)
- [Testing Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)

---

## 👥 Team Responsibilities

### Backend Team
- Maintain consistent router patterns
- Keep OpenAPI spec generation updated
- Monitor backend performance metrics
- Handle breaking changes communication

### Frontend Team
- Follow centralized API client usage
- Write and maintain contract tests
- Update integration tests for new features
- Monitor frontend error rates

### DevOps Team
- Maintain CI/CD pipeline validation
- Set up production monitoring alerts
- Manage deployment rollback procedures
- Monitor system health metrics

---

**Document Status:** ✅ Ready for Implementation  
**Next Review Date:** 2025-02-11  
**Implementation Lead:** TBD  
**Stakeholder Approval:** Pending