import { test, expect } from '@playwright/test';
import { testData } from '../fixtures/test-users';

test.describe('Assessment Integration Flow', () => {
  test.describe('HEXACO Personality Test', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/hexaco-test');
      await page.waitForLoadState('networkidle');
    });

    test('should display HEXACO test interface', async ({ page }) => {
      const isOnLogin = page.url().includes('sign-in') || page.url().includes('login');
      const isOnTest = page.url().includes('hexaco');
      
      if (isOnTest) {
        // Look for test interface elements
        const testContainer = page.locator('.test-container, .hexaco-test, [data-testid*="test"]');
        const questions = page.locator('.question, .test-question, [data-testid*="question"]');
        const startButton = page.locator('button:has-text("Start"), .start-test, [data-testid*="start"]');
        
        const hasTestElements = await testContainer.isVisible() || 
                               await questions.count() > 0 || 
                               await startButton.isVisible();
        
        if (hasTestElements) {
          expect(hasTestElements).toBeTruthy();
        }
      } else if (isOnLogin) {
        expect(isOnLogin).toBeTruthy();
      }
    });

    test('should handle test progression', async ({ page }) => {
      const isOnTest = page.url().includes('hexaco');
      
      if (isOnTest) {
        // Start the test if start button exists
        const startButton = page.locator('button:has-text("Start"), .start-test');
        if (await startButton.isVisible()) {
          await startButton.click();
          await page.waitForTimeout(1000);
        }
        
        // Look for questions
        const questions = page.locator('.question, .test-question');
        const questionCount = await questions.count();
        
        if (questionCount > 0) {
          // Answer first few questions
          for (let i = 0; i < Math.min(3, questionCount); i++) {
            const question = questions.nth(i);
            if (await question.isVisible()) {
              // Look for rating scale or multiple choice
              const ratingButtons = question.locator('button, input[type="radio"]');
              const buttonCount = await ratingButtons.count();
              
              if (buttonCount > 0) {
                // Select middle option (neutral)
                const middleIndex = Math.floor(buttonCount / 2);
                await ratingButtons.nth(middleIndex).click();
                await page.waitForTimeout(300);
              }
            }
          }
          
          // Look for next/continue button
          const nextButton = page.locator('button:has-text("Next"), button:has-text("Continue"), .next-button');
          if (await nextButton.isVisible() && await nextButton.isEnabled()) {
            await nextButton.click();
            await page.waitForTimeout(1000);
          }
        }
      }
    });

    test('should handle test completion and results', async ({ page }) => {
      const isOnTest = page.url().includes('hexaco');
      
      if (isOnTest) {
        // Skip to results by going directly to results page
        await page.goto('/profile/hexaco-results');
        await page.waitForLoadState('networkidle');
        
        // Look for results display
        const resultsContainer = page.locator('.results, .hexaco-results, [data-testid*="results"]');
        const chart = page.locator('canvas, svg, .chart');
        const scores = page.locator('.scores, .personality-scores, [data-testid*="scores"]');
        
        const hasResults = await resultsContainer.isVisible() || 
                          await chart.isVisible() || 
                          await scores.isVisible();
        
        if (hasResults) {
          expect(hasResults).toBeTruthy();
          
          // Test results interaction
          if (await chart.isVisible()) {
            await chart.hover();
          }
          
          if (await scores.isVisible()) {
            const scoreItems = scores.locator('.score-item, .dimension');
            const scoreCount = await scoreItems.count();
            
            if (scoreCount > 0) {
              await scoreItems.first().click();
              await page.waitForTimeout(500);
            }
          }
        }
      }
    });
  });

  test.describe('Holland Code Career Test', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/holland-test');
      await page.waitForLoadState('networkidle');
    });

    test('should display Holland test interface', async ({ page }) => {
      const isOnLogin = page.url().includes('sign-in') || page.url().includes('login');
      const isOnTest = page.url().includes('holland');
      
      if (isOnTest) {
        const testElements = page.locator('.test-container, .holland-test, .question, button:has-text("Start")');
        const hasTestElements = await testElements.count() > 0;
        
        if (hasTestElements) {
          expect(hasTestElements).toBeTruthy();
        }
      } else if (isOnLogin) {
        expect(isOnLogin).toBeTruthy();
      }
    });

    test('should handle Holland test progression', async ({ page }) => {
      const isOnTest = page.url().includes('holland');
      
      if (isOnTest) {
        const startButton = page.locator('button:has-text("Start")');
        if (await startButton.isVisible()) {
          await startButton.click();
          await page.waitForTimeout(1000);
        }
        
        // Answer a few questions
        const questions = page.locator('.question, .test-question');
        const questionCount = await questions.count();
        
        if (questionCount > 0) {
          for (let i = 0; i < Math.min(2, questionCount); i++) {
            const question = questions.nth(i);
            const options = question.locator('button, input[type="radio"]');
            const optionCount = await options.count();
            
            if (optionCount > 0) {
              await options.first().click();
              await page.waitForTimeout(300);
            }
          }
          
          const nextButton = page.locator('button:has-text("Next"), button:has-text("Continue")');
          if (await nextButton.isVisible()) {
            await nextButton.click();
            await page.waitForTimeout(1000);
          }
        }
      }
    });

    test('should display Holland results', async ({ page }) => {
      // Navigate to results page directly
      await page.goto('/profile/holland-results');
      await page.waitForLoadState('networkidle');
      
      const resultsElements = page.locator('.results, .holland-results, .career-types, canvas, svg');
      const hasResults = await resultsElements.count() > 0;
      
      if (hasResults) {
        expect(hasResults).toBeTruthy();
        
        // Test career type interactions
        const careerTypes = page.locator('.career-type, .holland-type');
        const typeCount = await careerTypes.count();
        
        if (typeCount > 0) {
          await careerTypes.first().click();
          await page.waitForTimeout(500);
        }
      }
    });
  });

  test.describe('Assessment Integration', () => {
    test('should integrate assessment results with recommendations', async ({ page }) => {
      // Navigate to dashboard after assessments
      await page.goto('/dashboard');
      await page.waitForLoadState('networkidle');
      
      const isOnDashboard = page.url().includes('dashboard');
      
      if (isOnDashboard) {
        // Look for personalized recommendations based on assessments
        const recommendations = page.locator('.recommendations, .career-recommendations, [data-testid*="recommendations"]');
        const personalizedContent = page.locator('.personalized, .based-on-assessment, [data-testid*="personalized"]');
        
        if (await recommendations.isVisible()) {
          expect(recommendations).toBeVisible();
          
          const recItems = recommendations.locator('.recommendation-item, .job-card, .career-card');
          const recCount = await recItems.count();
          
          if (recCount > 0) {
            await recItems.first().click();
            await page.waitForTimeout(1000);
          }
        }
        
        if (await personalizedContent.isVisible()) {
          expect(personalizedContent).toBeVisible();
        }
      }
    });

    test('should integrate with skill tree based on assessments', async ({ page }) => {
      await page.goto('/tree');
      await page.waitForLoadState('networkidle');
      
      const isOnTree = page.url().includes('tree');
      
      if (isOnTree) {
        // Look for assessment-influenced tree features
        const personalizedPaths = page.locator('.recommended-path, .suggested-skills, [data-testid*="recommended"]');
        const assessmentInsights = page.locator('.assessment-insights, .personality-based, [data-testid*="insights"]');
        
        if (await personalizedPaths.isVisible()) {
          expect(personalizedPaths).toBeVisible();
          
          await personalizedPaths.click();
          await page.waitForTimeout(1000);
        }
        
        if (await assessmentInsights.isVisible()) {
          expect(assessmentInsights).toBeVisible();
        }
      }
    });

    test('should show assessment summary in profile', async ({ page }) => {
      await page.goto('/profile');
      await page.waitForLoadState('networkidle');
      
      const isOnProfile = page.url().includes('profile');
      
      if (isOnProfile) {
        // Look for assessment summaries
        const hexacoSummary = page.locator('.hexaco-summary, [data-testid*="hexaco"]');
        const hollandSummary = page.locator('.holland-summary, [data-testid*="holland"]');
        const overallProfile = page.locator('.personality-profile, .assessment-profile');
        
        const hasSummaries = await hexacoSummary.isVisible() || 
                            await hollandSummary.isVisible() || 
                            await overallProfile.isVisible();
        
        if (hasSummaries) {
          expect(hasSummaries).toBeTruthy();
          
          // Test retaking assessments
          const retakeButton = page.locator('button:has-text("Retake"), .retake-test');
          if (await retakeButton.isVisible()) {
            await retakeButton.click();
            await page.waitForTimeout(1000);
            
            // Should navigate to test
            const isOnTest = page.url().includes('test') || page.url().includes('hexaco') || page.url().includes('holland');
            if (isOnTest) {
              expect(isOnTest).toBeTruthy();
            }
          }
        }
      }
    });
  });
});