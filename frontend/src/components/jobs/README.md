# Job Cards - Modern UI Implementation

This directory contains the enhanced job card components with modern styling, animations, and interactive features.

## Components

### JobCard.tsx
The main job card component with modern design:

**Features:**
- ✨ Modern gradient backgrounds with hover effects
- 🎯 Match percentage badges with color coding (excellent/good/fair/low)
- 🏢 Company logo placeholders with initials
- 🏷️ Skills tags with hover animations
- 🔥 Action buttons (Apply, Save, Like) with state management
- 📱 Responsive design for all screen sizes
- ⚡ Smooth animations using Framer Motion
- 🌙 Dark mode support

**Props:**
```typescript
interface JobCardProps {
  job: Job;                    // Job data
  isSelected: boolean;         // Selection state
  onClick: () => void;         // Click handler
  className?: string;          // Additional CSS classes
  showActions?: boolean;       // Show/hide action buttons
  onApply?: (job: Job) => void;     // Apply button handler
  onSave?: (job: Job) => void;      // Save button handler
  onLike?: (job: Job) => void;      // Like button handler
  isLiked?: boolean;               // Like state
  isSaved?: boolean;               // Save state
}
```

### JobCardSkeleton.tsx
Loading skeleton component that mimics the job card structure:

**Features:**
- 💀 Skeleton loading animation
- 📐 Matches JobCard dimensions exactly
- ⚡ Smooth pulse animations
- 🎨 Consistent with design system

### JobRecommendationList.tsx
Container component for displaying multiple job cards:

**Features:**
- 📋 Grid layout with responsive columns
- 🔄 Loading states with skeletons
- 🚨 Error handling with user-friendly messages
- 🔗 Navigation to full recommendations page
- ⭐ Modern call-to-action button

### JobCard.css
Enhanced CSS with modern styling:

**Features:**
- 🎨 Modern gradients and shadows
- ✨ Hover effects and transitions
- 🎯 Color-coded match badges
- 📱 Responsive breakpoints
- 🌙 Dark mode variables
- ⚡ Entrance animations

## Usage Examples

### Basic Usage
```tsx
import { JobCard } from '@/components/jobs';

<JobCard
  job={jobData}
  isSelected={false}
  onClick={() => handleJobClick(jobData)}
/>
```

### With Actions
```tsx
<JobCard
  job={jobData}
  isSelected={false}
  onClick={() => handleJobClick(jobData)}
  showActions={true}
  onApply={handleApply}
  onSave={handleSave}
  onLike={handleLike}
  isLiked={likedJobs.has(jobData.id)}
  isSaved={savedJobs.has(jobData.id)}
/>
```

### Loading State
```tsx
import { JobCardSkeleton } from '@/components/jobs';

{isLoading ? (
  <JobCardSkeleton />
) : (
  <JobCard job={jobData} ... />
)}
```

### Full List
```tsx
import { JobRecommendationList } from '@/components/jobs';

<JobRecommendationList
  recommendations={jobs}
  isLoading={loading}
  error={error}
  onSelectJob={handleSelectJob}
/>
```

## Styling

### CSS Classes
- `.job-card` - Main card container
- `.job-card.selected` - Selected state
- `.match-badge.excellent` - 85%+ match (green)
- `.match-badge.good` - 70-84% match (blue)
- `.match-badge.fair` - 55-69% match (yellow)
- `.match-badge.low` - <55% match (red)

### CSS Variables
The component supports CSS custom properties for theming:
- `--accent-color` - Primary accent color
- `--text-color` - Main text color
- `--background` - Background color

## Integration Points

### Home Page (`/src/app/page.tsx`)
- Shows 3 job cards in grid layout
- Hides action buttons for cleaner look
- Links to full recommendations page

### Recommendations Page (`/src/app/career/recommendations/page.tsx`)
- Shows all available job recommendations
- Full action buttons functionality
- Interactive job selection with skills tree
- Statistics dashboard

## Data Structure

### Job Interface
```typescript
interface Job {
  id: string;
  score: number;
  metadata: {
    title: string;
    description?: string;
    skills?: string[];
    match_percentage?: number;
    isco_group?: string;
    preferred_label?: string;
    alt_labels?: string[];
    company?: string;
    [key: string]: any;
  };
}
```

## Performance Optimizations

1. **Lazy Loading**: Components support progressive loading
2. **Memoization**: Cards only re-render when props change
3. **Skeleton Loading**: Immediate visual feedback during data fetching
4. **Responsive Images**: Company logos are optimized for different screen sizes
5. **CSS Animations**: Hardware-accelerated transforms for smooth performance

## Accessibility

- ♿ ARIA labels on interactive elements
- ⌨️ Keyboard navigation support
- 🎨 High contrast ratios for text
- 📱 Touch-friendly button sizes
- 🔊 Screen reader compatibility

## Browser Support

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## Migration Notes

If upgrading from the old glass card design:

1. Replace imports: `import JobCard from './JobCard'` stays the same
2. Update props: Add new optional props as needed
3. Remove old CSS: The new `JobCard.css` replaces `JobCard.module.css`
4. Update animations: Framer Motion animations are now built-in

## Future Enhancements

- 🔍 Search and filter functionality
- 🏷️ Tag-based categorization
- 📊 Detailed analytics view
- 💾 Persistent state management
- 🔔 Real-time updates
- 🎯 AI-powered recommendations