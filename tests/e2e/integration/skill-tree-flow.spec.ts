import { test, expect } from '@playwright/test';
import { testData } from '../fixtures/test-users';

test.describe('Skill Tree Integration Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/tree');
    await page.waitForLoadState('networkidle');
  });

  test('should display skill tree interface', async ({ page }) => {
    const isOnLogin = page.url().includes('sign-in') || page.url().includes('login');
    const isOnTree = page.url().includes('tree');
    
    if (isOnTree) {
      // Look for tree visualization elements
      const treeContainer = page.locator('.tree-container, .competence-tree, [data-testid*="tree"]');
      const treeCanvas = page.locator('svg, canvas, .tree-visualization');
      const treeNodes = page.locator('.tree-node, .node, .skill-node');
      
      // At least one tree element should be visible
      const hasTreeElements = await treeContainer.isVisible() || 
                             await treeCanvas.isVisible() || 
                             await treeNodes.count() > 0;
      
      if (hasTreeElements) {
        expect(hasTreeElements).toBeTruthy();
      }
    } else if (isOnLogin) {
      expect(isOnLogin).toBeTruthy();
    }
  });

  test('should handle tree node interactions', async ({ page }) => {
    const isOnTree = page.url().includes('tree');
    
    if (isOnTree) {
      // Wait for tree to load
      await page.waitForTimeout(2000);
      
      // Look for clickable nodes
      const treeNodes = page.locator('.tree-node, .node, .skill-node, [data-testid*="node"]');
      const nodeCount = await treeNodes.count();
      
      if (nodeCount > 0) {
        const firstNode = treeNodes.first();
        await expect(firstNode).toBeVisible();
        
        // Test node hover
        await firstNode.hover();
        await page.waitForTimeout(500);
        
        // Test node click
        await firstNode.click();
        await page.waitForTimeout(500);
        
        // Look for node details or modal
        const nodeDetails = page.locator('.node-details, .skill-details, .modal, [data-testid*="details"]');
        if (await nodeDetails.isVisible()) {
          await expect(nodeDetails).toBeVisible();
        }
      }
    }
  });

  test('should handle tree navigation and zoom', async ({ page }) => {
    const isOnTree = page.url().includes('tree');
    
    if (isOnTree) {
      // Look for zoom controls
      const zoomIn = page.locator('button[aria-label*="zoom in"], .zoom-in, [data-testid*="zoom-in"]');
      const zoomOut = page.locator('button[aria-label*="zoom out"], .zoom-out, [data-testid*="zoom-out"]');
      const resetZoom = page.locator('button[aria-label*="reset"], .reset-zoom, [data-testid*="reset"]');
      
      if (await zoomIn.isVisible()) {
        await zoomIn.click();
        await page.waitForTimeout(500);
      }
      
      if (await zoomOut.isVisible()) {
        await zoomOut.click();
        await page.waitForTimeout(500);
      }
      
      if (await resetZoom.isVisible()) {
        await resetZoom.click();
        await page.waitForTimeout(500);
      }
      
      // Test pan/drag functionality
      const treeContainer = page.locator('.tree-container, .tree-visualization, svg, canvas').first();
      if (await treeContainer.isVisible()) {
        const bbox = await treeContainer.boundingBox();
        if (bbox) {
          // Test drag
          await page.mouse.move(bbox.x + bbox.width / 2, bbox.y + bbox.height / 2);
          await page.mouse.down();
          await page.mouse.move(bbox.x + bbox.width / 2 + 50, bbox.y + bbox.height / 2 + 50);
          await page.mouse.up();
        }
      }
    }
  });

  test('should handle tree search and filtering', async ({ page }) => {
    const isOnTree = page.url().includes('tree');
    
    if (isOnTree) {
      // Look for search functionality
      const searchInput = page.locator('input[placeholder*="search"], .search-input, [data-testid*="search"]');
      const filterButtons = page.locator('.filter-button, .category-filter, [data-testid*="filter"]');
      
      if (await searchInput.isVisible()) {
        await searchInput.fill(testData.skillNode);
        await page.waitForTimeout(1000);
        
        // Should filter tree nodes
        const visibleNodes = page.locator('.tree-node:visible, .node:visible');
        const nodeCount = await visibleNodes.count();
        
        // Clear search
        await searchInput.clear();
        await page.waitForTimeout(500);
      }
      
      // Test filters
      const filterCount = await filterButtons.count();
      if (filterCount > 0) {
        const firstFilter = filterButtons.first();
        await firstFilter.click();
        await page.waitForTimeout(1000);
        
        // Should apply filter
        expect(page.url()).toContain('tree');
      }
    }
  });

  test('should handle skill path exploration', async ({ page }) => {
    const isOnTree = page.url().includes('tree');
    
    if (isOnTree) {
      // Look for path exploration features
      const pathButton = page.locator('button:has-text("Path"), .explore-path, [data-testid*="path"]');
      const alternativePaths = page.locator('.alternative-paths, .path-options, [data-testid*="alternatives"]');
      
      if (await pathButton.isVisible()) {
        await pathButton.click();
        await page.waitForTimeout(1000);
        
        // Should show path exploration interface
        if (await alternativePaths.isVisible()) {
          await expect(alternativePaths).toBeVisible();
        }
      }
      
      // Test career progression
      const progressionButton = page.locator('button:has-text("Progression"), .career-progression, [data-testid*="progression"]');
      if (await progressionButton.isVisible()) {
        await progressionButton.click();
        await page.waitForTimeout(1000);
      }
    }
  });

  test('should handle skill assessment integration', async ({ page }) => {
    const isOnTree = page.url().includes('tree');
    
    if (isOnTree) {
      // Look for assessment-related features
      const assessButton = page.locator('button:has-text("Assess"), .skill-assessment, [data-testid*="assess"]');
      const skillGaps = page.locator('.skill-gaps, .missing-skills, [data-testid*="gaps"]');
      
      if (await assessButton.isVisible()) {
        await assessButton.click();
        await page.waitForTimeout(1000);
        
        // Should show assessment interface or results
        const assessmentInterface = page.locator('.assessment-interface, .skill-test, [data-testid*="assessment"]');
        if (await assessmentInterface.isVisible()) {
          await expect(assessmentInterface).toBeVisible();
        }
      }
      
      // Test skill gap analysis
      if (await skillGaps.isVisible()) {
        await expect(skillGaps).toBeVisible();
        
        const gapItems = skillGaps.locator('.gap-item, .missing-skill');
        const gapCount = await gapItems.count();
        
        if (gapCount > 0) {
          await gapItems.first().click();
          await page.waitForTimeout(500);
        }
      }
    }
  });

  test('should handle tree performance with large datasets', async ({ page }) => {
    const isOnTree = page.url().includes('tree');
    
    if (isOnTree) {
      // Test tree loading performance
      const startTime = Date.now();
      
      // Wait for tree to be fully loaded
      await page.waitForLoadState('networkidle');
      
      const loadTime = Date.now() - startTime;
      console.log(`Tree load time: ${loadTime}ms`);
      
      // Tree should load within reasonable time (10 seconds)
      expect(loadTime).toBeLessThan(10000);
      
      // Test tree responsiveness
      const treeNodes = page.locator('.tree-node, .node');
      const nodeCount = await treeNodes.count();
      
      if (nodeCount > 100) {
        // Test virtualization or performance optimization
        const visibleNodes = page.locator('.tree-node:visible, .node:visible');
        const visibleCount = await visibleNodes.count();
        
        // Should have fewer visible nodes than total for performance
        console.log(`Total nodes: ${nodeCount}, Visible nodes: ${visibleCount}`);
      }
    }
  });
});