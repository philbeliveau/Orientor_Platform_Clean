# Orientator AI Frontend Components

This directory contains all the frontend components for the Orientator AI chat interface feature.

## Component Overview

### Core Components

1. **MessageComponent.tsx** - Main component renderer that handles routing to specific message type components
2. **ToolInvocationLoader.tsx** - Shows loading state when AI is invoking tools
3. **SaveActionButton.tsx** - Reusable save button with loading and saved states

### Message Type Components

1. **SkillTreeMessage.tsx** - Displays hierarchical skill requirements for jobs
2. **CareerPathMessage.tsx** - Shows career progression timeline with milestones
3. **JobCardMessage.tsx** - Renders job opportunities with match scores
4. **PeerCardMessage.tsx** - Shows compatible peers for networking
5. **TestResultMessage.tsx** - Displays personality test results (HEXACO/Holland)
6. **ChallengeCardMessage.tsx** - Shows skill-building challenges with XP rewards
7. **SaveConfirmationMessage.tsx** - Confirms when items are saved to My Space

## Integration with ChatInterface

The ChatInterface component has been extended to support Orientator AI mode:

```typescript
<ChatInterface 
  currentUserId={userId} 
  enableOrientator={true} 
/>
```

When `enableOrientator` is true:
- Messages are sent to the `/orientator/message` endpoint
- Rich message components are rendered below AI responses
- Component actions (save, explore, etc.) are handled automatically

## Message Format

Messages now support an extended format:

```typescript
interface Message {
  id: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at: string;
  tokens_used?: number;
  components?: MessageComponent[];
  metadata?: {
    tools_invoked?: string[];
    processing_time_ms?: number;
    confidence_score?: number;
  };
}
```

## Component Actions

Each component can define actions that users can take:

```typescript
interface ComponentAction {
  type: 'save' | 'expand' | 'explore' | 'share' | 'start';
  label: string;
  endpoint?: string;
  params?: Record<string, any>;
}
```

## Testing

Unit tests are provided for all components in the `__tests__` directories:
- `/components/chat/__tests__/` - Tests for core chat components
- `/components/orientator/__tests__/` - Tests for message type components

Run tests with:
```bash
npm test
```

## Usage Example

```typescript
// In your page component
import ChatInterface from '@/components/chat/ChatInterface';

export default function OrientatorPage() {
  const currentUserId = getUserId();
  
  return (
    <ChatInterface 
      currentUserId={currentUserId} 
      enableOrientator={true} 
    />
  );
}
```

## Styling

All components use Tailwind CSS classes for styling and maintain consistency with the existing chat interface design. The paper-like aesthetic is preserved with:
- Clean, minimal borders
- Subtle hover effects
- Consistent color scheme (blue for primary actions, green for saves, etc.)
- Responsive design for all screen sizes