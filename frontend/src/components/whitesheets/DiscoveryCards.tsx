'use client';

import React, { useState } from 'react';

interface DiscoveryCard {
  id: string;
  title: string;
  description: string;
  category: 'values' | 'interests' | 'skills' | 'dreams';
  prompt: string;
  icon?: React.ReactNode;
}

interface DiscoveryCardsProps {
  onCardSelect?: (card: DiscoveryCard) => void;
  className?: string;
}

const discoveryCards: DiscoveryCard[] = [
  {
    id: 'values-core',
    title: 'Core Values',
    description: 'What matters most to you?',
    category: 'values',
    prompt: 'Think about moments when you felt most authentic. What values were you honoring?',
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
      </svg>
    )
  },
  {
    id: 'interests-passion',
    title: 'Hidden Passions',
    description: 'What secretly excites you?',
    category: 'interests',
    prompt: 'What activities make you lose track of time? What would you do if no one was watching?',
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"></path>
      </svg>
    )
  },
  {
    id: 'skills-natural',
    title: 'Natural Talents',
    description: 'What comes easily to you?',
    category: 'skills',
    prompt: 'What do others often ask for your help with? What feels effortless when you do it?',
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
      </svg>
    )
  },
  {
    id: 'dreams-vision',
    title: 'Future Vision',
    description: 'What life do you envision?',
    category: 'dreams',
    prompt: 'Imagine your ideal day 5 years from now. What are you doing? How do you feel?',
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
        <circle cx="12" cy="12" r="3"></circle>
      </svg>
    )
  },
  {
    id: 'values-growth',
    title: 'Growth Mindset',
    description: 'How do you want to evolve?',
    category: 'values',
    prompt: 'What version of yourself are you becoming? What growth excites you most?',
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
      </svg>
    )
  },
  {
    id: 'interests-curiosity',
    title: 'Deep Curiosity',
    description: 'What questions drive you?',
    category: 'interests',
    prompt: 'What topics make you endlessly curious? What would you research for hours?',
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <circle cx="12" cy="12" r="10"></circle>
        <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
        <path d="M12 17h.01"></path>
      </svg>
    )
  }
];

const categoryColors = {
  values: 'var(--white-sheet-text)',
  interests: 'var(--white-sheet-text-secondary)',
  skills: 'var(--white-sheet-text)',
  dreams: 'var(--white-sheet-text-secondary)'
};

export default function DiscoveryCards({ onCardSelect, className = '' }: DiscoveryCardsProps) {
  const [selectedCard, setSelectedCard] = useState<string | null>(null);
  const [hoveredCard, setHoveredCard] = useState<string | null>(null);

  const handleCardClick = (card: DiscoveryCard) => {
    setSelectedCard(card.id);
    onCardSelect?.(card);
  };

  return (
    <div className={`discovery-cards ${className}`}>
      <div className="discovery-cards-header">
        <h2 className="white-sheet-heading white-sheet-heading-lg">Discover Yourself</h2>
        <p className="white-sheet-text-secondary">Choose a card to begin your exploration</p>
      </div>
      
      <div className="discovery-cards-grid">
        {discoveryCards.map((card) => {
          const isSelected = selectedCard === card.id;
          const isHovered = hoveredCard === card.id;
          
          return (
            <div
              key={card.id}
              className={`discovery-card ${isSelected ? 'selected' : ''}`}
              onMouseEnter={() => setHoveredCard(card.id)}
              onMouseLeave={() => setHoveredCard(null)}
              onClick={() => handleCardClick(card)}
            >
              <div className="discovery-card-content">
                <div className="discovery-card-icon" style={{ color: categoryColors[card.category] }}>
                  {card.icon}
                </div>
                
                <div className="discovery-card-text">
                  <h3 className="discovery-card-title">{card.title}</h3>
                  <p className="discovery-card-description">{card.description}</p>
                </div>
              </div>
              
              {(isHovered || isSelected) && (
                <div className="discovery-card-prompt white-sheet-fade-in">
                  <p className="discovery-card-prompt-text">{card.prompt}</p>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

// Discovery Cards specific styles
const discoveryCardsStyles = `
.discovery-cards {
  padding: var(--white-sheet-space-xl) 0;
}

.discovery-cards-header {
  text-align: center;
  margin-bottom: var(--white-sheet-space-2xl);
}

.discovery-cards-header h2 {
  margin-bottom: var(--white-sheet-space-sm);
}

.discovery-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--white-sheet-space-lg);
  max-width: 1200px;
  margin: 0 auto;
}

.discovery-card {
  background: var(--white-sheet-primary);
  border: 1px solid var(--white-sheet-border-subtle);
  border-radius: var(--white-sheet-radius-lg);
  padding: var(--white-sheet-space-lg);
  cursor: pointer;
  transition: all var(--white-sheet-transition-medium);
  min-height: 120px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.discovery-card:hover {
  border-color: var(--white-sheet-border);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px var(--white-sheet-shadow-hover);
}

.discovery-card.selected {
  border-color: var(--white-sheet-text-subtle);
  background: var(--white-sheet-secondary);
  box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.05);
}

.discovery-card-content {
  display: flex;
  align-items: flex-start;
  gap: var(--white-sheet-space-md);
}

.discovery-card-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: var(--white-sheet-radius-sm);
  background: var(--white-sheet-tertiary);
  transition: all var(--white-sheet-transition-fast);
}

.discovery-card:hover .discovery-card-icon {
  background: var(--white-sheet-hover);
}

.discovery-card-text {
  flex: 1;
}

.discovery-card-title {
  font-family: var(--white-sheet-font-primary);
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--white-sheet-text);
  margin: 0 0 var(--white-sheet-space-xs) 0;
}

.discovery-card-description {
  font-size: 0.875rem;
  color: var(--white-sheet-text-secondary);
  margin: 0;
  line-height: 1.5;
}

.discovery-card-prompt {
  margin-top: var(--white-sheet-space-md);
  padding-top: var(--white-sheet-space-md);
  border-top: 1px solid var(--white-sheet-border-subtle);
}

.discovery-card-prompt-text {
  font-size: 0.875rem;
  color: var(--white-sheet-text-subtle);
  font-style: italic;
  margin: 0;
  line-height: 1.6;
}

@media (max-width: 768px) {
  .discovery-cards-grid {
    grid-template-columns: 1fr;
    gap: var(--white-sheet-space-md);
  }
  
  .discovery-card {
    padding: var(--white-sheet-space-md);
  }
  
  .discovery-card-content {
    gap: var(--white-sheet-space-sm);
  }
  
  .discovery-card-icon {
    width: 32px;
    height: 32px;
  }
  
  .discovery-card-title {
    font-size: 1rem;
  }
}
`;

// Inject styles
if (typeof document !== 'undefined') {
  const styleSheet = document.createElement('style');
  styleSheet.textContent = discoveryCardsStyles;
  document.head.appendChild(styleSheet);
}