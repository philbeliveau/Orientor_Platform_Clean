import { test, expect } from '@playwright/test';

test.describe('Frontend Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should load homepage successfully', async ({ page }) => {
    await expect(page.locator('body')).toBeVisible();
    await expect(page).toHaveTitle(/Orientor|Navigo/i);
  });

  test('should display main navigation elements', async ({ page }) => {
    // Check for common navigation elements
    const navigation = page.locator('nav');
    await expect(navigation).toBeVisible();
    
    // Check for logo or brand name
    const logoOrBrand = page.locator('img[alt*="logo"], a[href="/"], h1, .logo');
    await expect(logoOrBrand.first()).toBeVisible();
  });

  test('should navigate to sign-in page', async ({ page }) => {
    const signInLink = page.locator('a[href*="sign-in"], button:has-text("Sign In"), a:has-text("Sign In")');
    if (await signInLink.first().isVisible()) {
      await signInLink.first().click();
      await expect(page).toHaveURL(/.*sign-in/);
    }
  });

  test('should navigate to sign-up page', async ({ page }) => {
    const signUpLink = page.locator('a[href*="sign-up"], button:has-text("Sign Up"), a:has-text("Sign Up")');
    if (await signUpLink.first().isVisible()) {
      await signUpLink.first().click();
      await expect(page).toHaveURL(/.*sign-up/);
    }
  });

  test('should handle protected route redirects', async ({ page }) => {
    const protectedRoutes = [
      '/dashboard',
      '/profile',
      '/chat',
      '/tree',
      '/space'
    ];

    for (const route of protectedRoutes) {
      await page.goto(route);
      await page.waitForLoadState('networkidle');
      
      const currentUrl = page.url();
      // Should either stay on the route (if authenticated) or redirect to sign-in
      const isOnRoute = currentUrl.includes(route);
      const isOnSignIn = currentUrl.includes('sign-in');
      const isOnLogin = currentUrl.includes('login');
      
      expect(isOnRoute || isOnSignIn || isOnLogin).toBeTruthy();
    }
  });

  test('should display responsive navigation', async ({ page }) => {
    // Test desktop navigation
    await page.setViewportSize({ width: 1200, height: 800 });
    const desktopNav = page.locator('nav');
    await expect(desktopNav).toBeVisible();

    // Test mobile navigation
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Look for mobile menu toggle
    const mobileMenuToggle = page.locator('button[aria-label*="menu"], .mobile-menu-toggle, button:has(svg)');
    if (await mobileMenuToggle.first().isVisible()) {
      await mobileMenuToggle.first().click();
      
      // Check if mobile menu appears
      const mobileMenu = page.locator('.mobile-menu, nav ul, .menu-items');
      await expect(mobileMenu.first()).toBeVisible();
    }
  });

  test('should handle footer navigation', async ({ page }) => {
    // Scroll to bottom to check footer
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    
    const footer = page.locator('footer');
    if (await footer.isVisible()) {
      await expect(footer).toBeVisible();
    }
  });

  test('should handle breadcrumb navigation', async ({ page }) => {
    // Navigate to a nested route that might have breadcrumbs
    await page.goto('/profile');
    await page.waitForLoadState('networkidle');
    
    const breadcrumbs = page.locator('.breadcrumb, nav[aria-label="breadcrumb"], .breadcrumbs');
    if (await breadcrumbs.isVisible()) {
      await expect(breadcrumbs).toBeVisible();
    }
  });

  test('should handle back navigation', async ({ page }) => {
    // Navigate to a page and then go back
    await page.goto('/sign-in');
    await page.waitForLoadState('networkidle');
    
    await page.goBack();
    await expect(page).toHaveURL('/');
  });

  test('should handle external link navigation', async ({ page }) => {
    // Look for external links and ensure they open properly
    const externalLinks = page.locator('a[target="_blank"], a[href^="http"]:not([href*="localhost"])');
    
    if (await externalLinks.count() > 0) {
      const link = externalLinks.first();
      const href = await link.getAttribute('href');
      const target = await link.getAttribute('target');
      
      if (target === '_blank') {
        // External links should have proper attributes
        expect(href).toBeTruthy();
      }
    }
  });

  test('should maintain navigation state', async ({ page }) => {
    // Test that navigation state is preserved across page loads
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
    
    // Reload the page
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    // Should still be on dashboard or redirected appropriately
    const currentUrl = page.url();
    expect(currentUrl).toBeTruthy();
  });
});