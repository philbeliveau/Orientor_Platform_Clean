import { chromium, FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  console.log('🚀 Starting global test setup...');

  // Create a browser instance for setup
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // Wait for backend to be ready
    console.log('⏳ Waiting for backend to be ready...');
    await page.goto('http://localhost:8000/health', { waitUntil: 'domcontentloaded' });
    
    // Wait for frontend to be ready
    console.log('⏳ Waiting for frontend to be ready...');
    await page.goto('http://localhost:3000', { waitUntil: 'domcontentloaded' });
    
    console.log('✅ Global setup completed successfully');
  } catch (error) {
    console.error('❌ Global setup failed:', error);
    throw error;
  } finally {
    await browser.close();
  }
}

export default globalSetup;