import { test, expect } from '@playwright/test';

test.describe('Backend API Endpoints', () => {
  const baseURL = 'http://localhost:8000';

  test('should respond to health check', async ({ request }) => {
    const response = await request.get(`${baseURL}/health`);
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    expect(data.status).toBe('healthy');
  });

  test('should serve API documentation', async ({ page }) => {
    await page.goto(`${baseURL}/docs`);
    await expect(page.locator('.swagger-ui')).toBeVisible();
    await expect(page.locator('h2.title')).toContainText('Navigo API');
  });

  test('should handle CORS for frontend requests', async ({ request }) => {
    const response = await request.options(`${baseURL}/api/v1/profiles`, {
      headers: {
        'Origin': 'http://localhost:3000',
        'Access-Control-Request-Method': 'GET',
        'Access-Control-Request-Headers': 'Content-Type,Authorization'
      }
    });
    
    expect(response.ok()).toBeTruthy();
    expect(response.headers()['access-control-allow-origin']).toBeTruthy();
  });

  test('should require authentication for protected endpoints', async ({ request }) => {
    const protectedEndpoints = [
      '/api/v1/profiles',
      '/api/v1/chat/conversations',
      '/api/v1/recommendations',
      '/api/v1/users/me'
    ];

    for (const endpoint of protectedEndpoints) {
      const response = await request.get(`${baseURL}${endpoint}`);
      // Should return 401 Unauthorized or redirect
      expect([401, 403, 422].includes(response.status())).toBeTruthy();
    }
  });

  test('should handle chat endpoints', async ({ request }) => {
    // Test chat endpoints without authentication
    const chatResponse = await request.get(`${baseURL}/api/v1/chat/conversations`);
    expect([401, 403, 422].includes(chatResponse.status())).toBeTruthy();
  });

  test('should handle assessment endpoints', async ({ request }) => {
    const endpoints = [
      '/api/v1/assessments/hexaco',
      '/api/v1/assessments/holland',
      '/api/v1/tree/competence'
    ];

    for (const endpoint of endpoints) {
      const response = await request.get(`${baseURL}${endpoint}`);
      // Should handle requests appropriately (might require auth)
      expect(response.status()).toBeLessThan(500);
    }
  });

  test('should handle career endpoints', async ({ request }) => {
    const endpoints = [
      '/api/v1/careers',
      '/api/v1/jobs',
      '/api/v1/recommendations'
    ];

    for (const endpoint of endpoints) {
      const response = await request.get(`${baseURL}${endpoint}`);
      expect(response.status()).toBeLessThan(500);
    }
  });

  test('should handle search endpoints', async ({ request }) => {
    const response = await request.get(`${baseURL}/api/v1/search?query=software`);
    expect(response.status()).toBeLessThan(500);
  });

  test('should return proper JSON responses', async ({ request }) => {
    const response = await request.get(`${baseURL}/health`);
    expect(response.ok()).toBeTruthy();
    
    const contentType = response.headers()['content-type'];
    expect(contentType).toContain('application/json');
    
    const data = await response.json();
    expect(typeof data).toBe('object');
  });

  test('should handle invalid endpoints gracefully', async ({ request }) => {
    const response = await request.get(`${baseURL}/api/v1/nonexistent`);
    expect(response.status()).toBe(404);
  });

  test('should handle malformed requests', async ({ request }) => {
    const response = await request.post(`${baseURL}/api/v1/chat/conversations`, {
      data: 'invalid json'
    });
    expect([400, 401, 403, 422].includes(response.status())).toBeTruthy();
  });
});