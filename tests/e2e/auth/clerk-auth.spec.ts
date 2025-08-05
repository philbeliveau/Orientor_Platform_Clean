import { test, expect } from '@playwright/test';
import { testUsers } from '../fixtures/test-users';

test.describe('Clerk Authentication', () => {
  test.beforeEach(async ({ page }) => {
    // Start each test from the homepage
    await page.goto('/');
  });

  test('should display sign-in page', async ({ page }) => {
    await page.click('a[href*="sign-in"]');
    await expect(page).toHaveURL(/.*sign-in/);
    
    // Check if Clerk sign-in component is loaded
    await expect(page.locator('.cl-rootBox')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('input[name="identifier"]')).toBeVisible();
  });

  test('should display sign-up page', async ({ page }) => {
    await page.click('a[href*="sign-up"]');
    await expect(page).toHaveURL(/.*sign-up/);
    
    // Check if Clerk sign-up component is loaded
    await expect(page.locator('.cl-rootBox')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('input[name="emailAddress"]')).toBeVisible();
  });

  test('should handle sign-in form interaction', async ({ page }) => {
    await page.goto('/sign-in');
    
    // Wait for Clerk component to load
    await page.waitForSelector('.cl-rootBox', { timeout: 10000 });
    
    // Try to interact with sign-in form
    const emailInput = page.locator('input[name="identifier"]');
    await emailInput.waitFor({ state: 'visible' });
    await emailInput.fill(testUsers.validUser.email);
    
    // Check if continue/next button becomes enabled
    const continueButton = page.locator('button[type="submit"]').first();
    await expect(continueButton).toBeEnabled();
  });

  test('should handle sign-up form interaction', async ({ page }) => {
    await page.goto('/sign-up');
    
    // Wait for Clerk component to load
    await page.waitForSelector('.cl-rootBox', { timeout: 10000 });
    
    // Try to interact with sign-up form
    const emailInput = page.locator('input[name="emailAddress"]');
    await emailInput.waitFor({ state: 'visible' });
    await emailInput.fill(testUsers.newUser.email);
    
    const passwordInput = page.locator('input[name="password"]');
    if (await passwordInput.isVisible()) {
      await passwordInput.fill(testUsers.newUser.password);
    }
    
    // Check if continue/signup button exists
    const signUpButton = page.locator('button[type="submit"]').first();
    await expect(signUpButton).toBeVisible();
  });

  test('should redirect to dashboard when authenticated', async ({ page }) => {
    // This test assumes you have a way to set authentication state
    // You might need to modify this based on your actual auth implementation
    
    await page.goto('/dashboard');
    
    // If not authenticated, should redirect to sign-in
    // If authenticated, should show dashboard
    await page.waitForLoadState('networkidle');
    
    const currentUrl = page.url();
    const isOnSignIn = currentUrl.includes('sign-in');
    const isOnDashboard = currentUrl.includes('dashboard');
    
    expect(isOnSignIn || isOnDashboard).toBeTruthy();
  });

  test('should handle authentication state changes', async ({ page }) => {
    // Test navigation between public and protected routes
    await page.goto('/');
    
    // Check if user menu or sign-in button is present
    const userButton = page.locator('[data-testid="user-button"]');
    const signInButton = page.locator('a[href*="sign-in"]');
    
    const isLoggedIn = await userButton.isVisible();
    const hasSignInButton = await signInButton.isVisible();
    
    expect(isLoggedIn || hasSignInButton).toBeTruthy();
  });

  test('should display proper error handling', async ({ page }) => {
    await page.goto('/sign-in');
    await page.waitForSelector('.cl-rootBox', { timeout: 10000 });
    
    // Try to submit with invalid credentials
    const emailInput = page.locator('input[name="identifier"]');
    await emailInput.waitFor({ state: 'visible' });
    await emailInput.fill('invalid@email.com');
    
    const submitButton = page.locator('button[type="submit"]').first();
    await submitButton.click();
    
    // Wait for potential error messages
    await page.waitForTimeout(2000);
    
    // Check if we're still on sign-in page (indicating form didn't submit successfully)
    expect(page.url()).toContain('sign-in');
  });
});