'use client';

import React, { useState } from 'react';
import WhiteSheetLayout from '@/components/layout/WhiteSheetLayout';
import BlankCanvas from '@/components/whitesheets/BlankCanvas';
import DiscoveryCards from '@/components/whitesheets/DiscoveryCards';
import FlowingTransitions, { FloatingElements, BreathingAnimation } from '@/components/whitesheets/FlowingTransitions';

interface DiscoveryCard {
  id: string;
  title: string;
  description: string;
  category: 'values' | 'interests' | 'skills' | 'dreams';
  prompt: string;
  icon?: React.ReactNode;
}

export default function WhiteSheetDemo() {
  const [selectedCard, setSelectedCard] = useState<DiscoveryCard | null>(null);
  const [canvasContent, setCanvasContent] = useState('');
  const [currentStep, setCurrentStep] = useState<'explore' | 'discover' | 'reflect'>('discover');

  const handleCardSelect = (card: DiscoveryCard) => {
    setSelectedCard(card);
    setCurrentStep('reflect');
  };

  const handleContentChange = (content: string) => {
    setCanvasContent(content);
  };

  const handleReset = () => {
    setSelectedCard(null);
    setCanvasContent('');
    setCurrentStep('explore');
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 'explore':
        return (
          <FlowingTransitions direction="fade" duration={800} delay={200}>
            <div className="white-sheet-welcome">
              <BreathingAnimation intensity={0.01} duration={6000}>
                <div className="white-sheet-welcome-content">
                  <h1 className="white-sheet-heading white-sheet-heading-xl">Your Story Begins Here</h1>
                  <p className="white-sheet-text white-sheet-text-secondary welcome-description">
                    This is your space—clean, open, and entirely yours. Like a blank page waiting for your story, 
                    this platform invites you to explore, discover, and write your own path forward.
                  </p>
                  <div className="white-sheet-cta">
                    <button 
                      className="white-sheet-button white-sheet-button-primary"
                      onClick={() => setCurrentStep('discover')}
                    >
                      Begin Your Journey
                    </button>
                  </div>
                </div>
              </BreathingAnimation>
            </div>
          </FlowingTransitions>
        );

      case 'discover':
        return (
          <FlowingTransitions direction="slide-up" duration={600} delay={100}>
            <DiscoveryCards onCardSelect={handleCardSelect} />
          </FlowingTransitions>
        );

      case 'reflect':
        return (
          <FlowingTransitions direction="scale" duration={500} delay={150}>
            <div className="white-sheet-reflection">
              {selectedCard && (
                <div className="white-sheet-reflection-header">
                  <h2 className="white-sheet-heading white-sheet-heading-md">{selectedCard.title}</h2>
                  <p className="white-sheet-text white-sheet-text-secondary">{selectedCard.prompt}</p>
                </div>
              )}
              
              <BlankCanvas 
                onContentChange={handleContentChange}
                placeholder="Start writing your thoughts here..."
                autoFocus
              />
              
              <div className="white-sheet-reflection-actions">
                <button 
                  className="white-sheet-button"
                  onClick={handleReset}
                >
                  Start Over
                </button>
                <button 
                  className="white-sheet-button white-sheet-button-primary"
                  disabled={!canvasContent.trim()}
                >
                  Save Reflection
                </button>
              </div>
            </div>
          </FlowingTransitions>
        );

      default:
        return null;
    }
  };

  return (
    <WhiteSheetLayout>
      <FloatingElements count={6} />
      
      <div className="white-sheet-demo-container">
        {/* Progress indicator */}
        <div className="white-sheet-progress">
          <div className="white-sheet-progress-steps">
            <div className={`white-sheet-progress-step ${currentStep === 'discover' ? 'active' : currentStep === 'reflect' ? 'completed' : ''}`}>
              <div className="white-sheet-progress-step-indicator"></div>
              <span className="white-sheet-progress-step-label">Explore</span>
            </div>
            <div className={`white-sheet-progress-step ${currentStep === 'discover' ? 'active' : currentStep === 'reflect' ? 'completed' : ''}`}>
              <div className="white-sheet-progress-step-indicator"></div>
              <span className="white-sheet-progress-step-label">Discover</span>
            </div>
            <div className={`white-sheet-progress-step ${currentStep === 'reflect' ? 'active' : ''}`}>
              <div className="white-sheet-progress-step-indicator"></div>
              <span className="white-sheet-progress-step-label">Reflect</span>
            </div>
          </div>
        </div>

        {/* Main content */}
        <div className="white-sheet-demo-content">
          {renderStepContent()}
        </div>
      </div>
    </WhiteSheetLayout>
  );
}

// Demo-specific styles
const demoStyles = `
.white-sheet-demo-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 1;
}

.white-sheet-progress {
  position: sticky;
  top: 0;
  background: var(--white-sheet-primary);
  border-bottom: 1px solid var(--white-sheet-border-subtle);
  padding: var(--white-sheet-space-lg) 0;
  z-index: 10;
}

.white-sheet-progress-steps {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--white-sheet-space-2xl);
  max-width: 600px;
  margin: 0 auto;
}

.white-sheet-progress-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--white-sheet-space-sm);
  opacity: 0.5;
  transition: all var(--white-sheet-transition-medium);
}

.white-sheet-progress-step.active {
  opacity: 1;
}

.white-sheet-progress-step.completed {
  opacity: 0.8;
}

.white-sheet-progress-step-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--white-sheet-border);
  transition: all var(--white-sheet-transition-medium);
}

.white-sheet-progress-step.active .white-sheet-progress-step-indicator {
  background: var(--white-sheet-accent);
  transform: scale(1.2);
}

.white-sheet-progress-step.completed .white-sheet-progress-step-indicator {
  background: var(--white-sheet-text-secondary);
}

.white-sheet-progress-step-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--white-sheet-text-secondary);
}

.white-sheet-progress-step.active .white-sheet-progress-step-label {
  color: var(--white-sheet-accent);
}

.white-sheet-demo-content {
  flex: 1;
  padding: var(--white-sheet-space-xl) 0;
}

.white-sheet-welcome {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  text-align: center;
}

.white-sheet-welcome-content {
  max-width: 600px;
  padding: var(--white-sheet-space-xl);
}

.welcome-description {
  font-size: 1.125rem;
  line-height: 1.7;
  margin-bottom: var(--white-sheet-space-2xl);
}

.white-sheet-cta {
  display: flex;
  justify-content: center;
}

.white-sheet-reflection {
  max-width: 800px;
  margin: 0 auto;
  padding: var(--white-sheet-space-lg);
}

.white-sheet-reflection-header {
  margin-bottom: var(--white-sheet-space-2xl);
  text-align: center;
}

.white-sheet-reflection-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: var(--white-sheet-space-lg);
  padding-top: var(--white-sheet-space-lg);
  border-top: 1px solid var(--white-sheet-border-subtle);
}

.white-sheet-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.white-sheet-button:disabled:hover {
  background: var(--white-sheet-primary);
  transform: none;
}

@media (max-width: 768px) {
  .white-sheet-progress-steps {
    gap: var(--white-sheet-space-lg);
  }
  
  .white-sheet-welcome-content {
    padding: var(--white-sheet-space-lg);
  }
  
  .welcome-description {
    font-size: 1rem;
  }
  
  .white-sheet-reflection {
    padding: var(--white-sheet-space-md);
  }
  
  .white-sheet-reflection-actions {
    flex-direction: column;
    gap: var(--white-sheet-space-sm);
  }
}
`;

// Inject styles
if (typeof document !== 'undefined') {
  const styleSheet = document.createElement('style');
  styleSheet.textContent = demoStyles;
  document.head.appendChild(styleSheet);
}