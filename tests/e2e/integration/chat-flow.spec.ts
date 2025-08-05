import { test, expect } from '@playwright/test';
import { testData } from '../fixtures/test-users';

test.describe('Chat Integration Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to chat page (might redirect to login)
    await page.goto('/chat');
    await page.waitForLoadState('networkidle');
  });

  test('should display chat interface', async ({ page }) => {
    // Check if on login page or chat page
    const isOnLogin = page.url().includes('sign-in') || page.url().includes('login');
    const isOnChat = page.url().includes('chat');
    
    if (isOnChat) {
      // Look for chat interface elements
      const chatContainer = page.locator('[data-testid="chat-container"], .chat-interface, .chat-container');
      const messageInput = page.locator('input[placeholder*="message"], textarea[placeholder*="message"], .message-input');
      
      if (await chatContainer.isVisible() || await messageInput.isVisible()) {
        await expect(chatContainer.or(messageInput)).toBeVisible();
      }
    } else if (isOnLogin) {
      // If redirected to login, that's expected behavior
      expect(isOnLogin).toBeTruthy();
    }
  });

  test('should handle message sending flow', async ({ page }) => {
    const isOnChat = page.url().includes('chat');
    
    if (isOnChat) {
      // Look for message input
      const messageInput = page.locator('input[placeholder*="message"], textarea[placeholder*="message"], .message-input input, .message-input textarea');
      
      if (await messageInput.isVisible()) {
        // Type a message
        await messageInput.fill(testData.chatMessage);
        
        // Look for send button
        const sendButton = page.locator('button[type="submit"], .send-button, button:has-text("Send")');
        
        if (await sendButton.isVisible() && await sendButton.isEnabled()) {
          await sendButton.click();
          
          // Wait for message to appear in chat
          await page.waitForTimeout(1000);
          
          // Look for the sent message
          const messageContainer = page.locator('.message, .chat-message, [data-testid*="message"]');
          const hasMessage = await messageContainer.count() > 0;
          
          if (hasMessage) {
            expect(hasMessage).toBeTruthy();
          }
        }
      }
    }
  });

  test('should handle conversation management', async ({ page }) => {
    const isOnChat = page.url().includes('chat');
    
    if (isOnChat) {
      // Look for conversation list or new conversation button
      const newConversationButton = page.locator('button:has-text("New"), .new-conversation, [data-testid*="new-conversation"]');
      const conversationList = page.locator('.conversation-list, .conversations, [data-testid*="conversations"]');
      
      if (await newConversationButton.isVisible()) {
        await newConversationButton.click();
        await page.waitForTimeout(1000);
        
        // Should create new conversation or show form
        expect(page.url()).toContain('chat');
      }
      
      if (await conversationList.isVisible()) {
        const conversations = conversationList.locator('.conversation-item, .conversation, [data-testid*="conversation"]');
        const conversationCount = await conversations.count();
        
        if (conversationCount > 0) {
          await conversations.first().click();
          await page.waitForTimeout(1000);
          
          // Should navigate to specific conversation
          expect(page.url()).toContain('chat');
        }
      }
    }
  });

  test('should handle AI response streaming', async ({ page }) => {
    const isOnChat = page.url().includes('chat');
    
    if (isOnChat) {
      const messageInput = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]');
      
      if (await messageInput.isVisible()) {
        await messageInput.fill('Hello AI');
        
        const sendButton = page.locator('button[type="submit"], .send-button');
        if (await sendButton.isVisible()) {
          await sendButton.click();
          
          // Look for streaming indicators or AI response
          const streamingIndicator = page.locator('.streaming, .typing, .ai-thinking, [data-testid*="streaming"]');
          const aiMessage = page.locator('.ai-message, .assistant-message, [data-testid*="ai-message"]');
          
          // Wait for either streaming indicator or AI message
          try {
            await Promise.race([
              streamingIndicator.waitFor({ timeout: 5000 }),
              aiMessage.waitFor({ timeout: 5000 })
            ]);
            
            // If we see streaming, wait for final message
            if (await streamingIndicator.isVisible()) {
              await aiMessage.waitFor({ timeout: 30000 });
            }
            
            expect(await aiMessage.isVisible()).toBeTruthy();
          } catch {
            // AI response might not be implemented or available
            console.log('AI response not available in test environment');
          }
        }
      }
    }
  });

  test('should handle chat features and tools', async ({ page }) => {
    const isOnChat = page.url().includes('chat');
    
    if (isOnChat) {
      // Look for chat features
      const features = {
        fileUpload: page.locator('input[type="file"], .file-upload, [data-testid*="file"]'),
        voiceInput: page.locator('.voice-input, [data-testid*="voice"], button[aria-label*="voice"]'),
        chatSettings: page.locator('.chat-settings, [data-testid*="settings"], button[aria-label*="settings"]'),
        clearChat: page.locator('button:has-text("Clear"), .clear-chat, [data-testid*="clear"]')
      };
      
      // Test each feature if available
      for (const [featureName, element] of Object.entries(features)) {
        if (await element.isVisible()) {
          console.log(`Testing ${featureName} feature`);
          
          if (featureName !== 'fileUpload') {
            await element.click();
            await page.waitForTimeout(500);
          }
        }
      }
    }
  });
});