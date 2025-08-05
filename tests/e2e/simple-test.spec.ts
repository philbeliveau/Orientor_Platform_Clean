import { test, expect } from '@playwright/test';

test.describe('Simple Test Suite', () => {
  test('should pass a basic test', async ({ page }) => {
    // This is a simple test to verify Playwright is working
    await page.goto('https://www.google.com');
    await expect(page).toHaveTitle(/Google/);
  });

  test('should handle basic page navigation', async ({ page }) => {
    await page.goto('https://example.com');
    await expect(page.locator('h1')).toContainText('Example Domain');
  });
});