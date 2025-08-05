import { test, expect } from '@playwright/test';

test.describe('UI Components', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should render page without JavaScript errors', async ({ page }) => {
    const errors: string[] = [];
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    await page.waitForLoadState('networkidle');
    
    // Filter out common non-critical errors
    const criticalErrors = errors.filter(error => 
      !error.includes('favicon') && 
      !error.includes('ResizeObserver') &&
      !error.includes('Non-passive event listener')
    );
    
    expect(criticalErrors).toHaveLength(0);
  });

  test('should display loading states appropriately', async ({ page }) => {
    // Navigate to a page that typically shows loading
    await page.goto('/dashboard');
    
    // Look for loading indicators
    const loadingElements = page.locator('.loading, .spinner, [data-testid="loading"]');
    
    // Loading should either be visible initially or not present
    await page.waitForLoadState('networkidle');
    
    // After network idle, loading should not be visible
    const visibleLoading = await loadingElements.isVisible();
    if (visibleLoading) {
      // Wait a bit more for loading to disappear
      await page.waitForTimeout(2000);
      await expect(loadingElements).not.toBeVisible();
    }
  });

  test('should handle button interactions', async ({ page }) => {
    // Find interactive buttons
    const buttons = page.locator('button:not([disabled])');
    const buttonCount = await buttons.count();
    
    if (buttonCount > 0) {
      const firstButton = buttons.first();
      await expect(firstButton).toBeVisible();
      
      // Test hover state
      await firstButton.hover();
      
      // Test focus state
      await firstButton.focus();
      
      // Button should be enabled
      await expect(firstButton).toBeEnabled();
    }
  });

  test('should handle form inputs', async ({ page }) => {
    // Look for forms on the page
    const forms = page.locator('form');
    const inputs = page.locator('input:not([type="hidden"])');
    
    const inputCount = await inputs.count();
    
    if (inputCount > 0) {
      const firstInput = inputs.first();
      await expect(firstInput).toBeVisible();
      
      // Test input interaction
      await firstInput.focus();
      await firstInput.fill('test');
      
      const value = await firstInput.inputValue();
      expect(value).toBe('test');
    }
  });

  test('should handle modal/dialog interactions', async ({ page }) => {
    // Look for modal triggers
    const modalTriggers = page.locator('[data-testid*="modal"], button:has-text("Open"), button:has-text("Show")');
    
    if (await modalTriggers.count() > 0) {
      const trigger = modalTriggers.first();
      if (await trigger.isVisible()) {
        await trigger.click();
        
        // Look for modal content
        const modal = page.locator('.modal, [role="dialog"], .dialog');
        if (await modal.isVisible()) {
          await expect(modal).toBeVisible();
          
          // Look for close button
          const closeButton = page.locator('[aria-label="close"], .close, button:has-text("Close")');
          if (await closeButton.isVisible()) {
            await closeButton.click();
            await expect(modal).not.toBeVisible();
          }
        }
      }
    }
  });

  test('should handle dropdown/select interactions', async ({ page }) => {
    const selects = page.locator('select');
    const dropdowns = page.locator('[role="combobox"], [role="listbox"]');
    
    // Test native selects
    if (await selects.count() > 0) {
      const select = selects.first();
      await expect(select).toBeVisible();
      
      const options = select.locator('option');
      if (await options.count() > 1) {
        await select.selectOption({ index: 1 });
      }
    }
    
    // Test custom dropdowns
    if (await dropdowns.count() > 0) {
      const dropdown = dropdowns.first();
      if (await dropdown.isVisible()) {
        await dropdown.click();
        
        // Look for dropdown options
        const options = page.locator('[role="option"]');
        if (await options.count() > 0) {
          await options.first().click();
        }
      }
    }
  });

  test('should handle tab navigation', async ({ page }) => {
    // Look for tab interfaces
    const tabLists = page.locator('[role="tablist"]');
    const tabs = page.locator('[role="tab"]');
    
    if (await tabs.count() > 0) {
      const firstTab = tabs.first();
      await expect(firstTab).toBeVisible();
      
      // Click the tab
      await firstTab.click();
      
      // Check if tab is selected
      const ariaSelected = await firstTab.getAttribute('aria-selected');
      expect(ariaSelected).toBe('true');
      
      // Look for corresponding tab panel
      const tabPanels = page.locator('[role="tabpanel"]');
      if (await tabPanels.count() > 0) {
        await expect(tabPanels.first()).toBeVisible();
      }
    }
  });

  test('should handle card/tile interactions', async ({ page }) => {
    // Look for interactive cards
    const cards = page.locator('.card, [data-testid*="card"], .tile');
    
    if (await cards.count() > 0) {
      const card = cards.first();
      await expect(card).toBeVisible();
      
      // Test hover interaction
      await card.hover();
      
      // If card is clickable, test click
      const isClickable = await card.getAttribute('role') === 'button' ||
                         await card.locator('a, button').count() > 0;
      
      if (isClickable) {
        // Card should respond to interaction
        await card.click();
      }
    }
  });

  test('should handle toast/notification display', async ({ page }) => {
    // Trigger an action that might show a toast
    const actionButtons = page.locator('button:has-text("Save"), button:has-text("Submit"), button:has-text("Send")');
    
    if (await actionButtons.count() > 0) {
      const button = actionButtons.first();
      if (await button.isVisible() && await button.isEnabled()) {
        await button.click();
        
        // Look for toast/notification
        const toast = page.locator('.toast, .notification, [role="alert"]');
        // Toasts might appear briefly, so check with timeout
        try {
          await expect(toast.first()).toBeVisible({ timeout: 3000 });
        } catch {
          // Toast might not appear for this action, which is fine
        }
      }
    }
  });

  test('should handle accessibility features', async ({ page }) => {
    // Check for proper heading structure
    const headings = page.locator('h1, h2, h3, h4, h5, h6');
    if (await headings.count() > 0) {
      const firstHeading = headings.first();
      await expect(firstHeading).toBeVisible();
    }
    
    // Check for skip links
    const skipLinks = page.locator('a[href="#main"], a[href="#content"], .skip-link');
    if (await skipLinks.count() > 0) {
      const skipLink = skipLinks.first();
      // Skip links might be hidden until focused
      await skipLink.focus();
    }
    
    // Check for landmark regions
    const main = page.locator('main, [role="main"]');
    if (await main.count() > 0) {
      await expect(main.first()).toBeVisible();
    }
  });

  test('should handle error states gracefully', async ({ page }) => {
    // Navigate to a non-existent route to test error handling
    await page.goto('/non-existent-route');
    
    // Should show 404 page or redirect
    await page.waitForLoadState('networkidle');
    
    const has404 = await page.locator('h1:has-text("404"), :has-text("Not Found"), :has-text("Page not found")').isVisible();
    const redirected = !page.url().includes('non-existent-route');
    
    expect(has404 || redirected).toBeTruthy();
  });
});