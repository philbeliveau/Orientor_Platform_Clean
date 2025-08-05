# Orientor Frontend - Next.js AI Career Platform

## 🚀 Frontend Overview

The Orientor frontend is a modern Next.js 13+ application providing an intuitive interface for AI-powered career guidance, skill assessments, and interactive visualizations. Built with TypeScript, TailwindCSS, and advanced React patterns.

### Core Technologies
- **Next.js 13+**: App Router with server-side rendering
- **TypeScript**: Type-safe development
- **TailwindCSS**: Utility-first styling with custom themes
- **Framer Motion**: Smooth animations and transitions
- **React Flow**: Interactive skill tree visualizations
- **Chart.js/Recharts**: Data visualization and analytics

## 📁 Architecture Overview

```
frontend/
├── src/
│   ├── app/                   # Next.js App Router (13+)
│   │   ├── (pages)/          # Route groups
│   │   ├── globals.css       # Global styles and Tailwind imports
│   │   ├── layout.tsx        # Root layout component
│   │   └── page.tsx          # Homepage
│   ├── components/           # Reusable React components
│   │   ├── ui/              # Base UI components (buttons, cards, inputs)
│   │   ├── chat/            # Chat interface components
│   │   ├── tree/            # Skill tree visualization components
│   │   ├── landing/         # Landing page components
│   │   └── layout/          # Layout components (navbar, sidebar)
│   ├── services/            # API client services
│   ├── hooks/               # Custom React hooks
│   ├── stores/              # State management (Zustand)
│   ├── types/               # TypeScript type definitions
│   └── utils/               # Utility functions
├── public/                  # Static assets
├── package.json             # Dependencies and scripts
├── next.config.js           # Next.js configuration
├── tailwind.config.js       # TailwindCSS configuration
└── tsconfig.json           # TypeScript configuration
```

## 🎨 Design System & Theming

### TailwindCSS Configuration
```javascript
// tailwind.config.js
module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // Custom color palette
        primary: {
          50: '#f0f9ff',
          500: '#3b82f6',
          900: '#1e3a8a',
        },
        secondary: {
          50: '#f8fafc',
          500: '#64748b',
          900: '#0f172a',
        }
      },
      fontFamily: {
        'departure': ['DepartureMono', 'monospace'],
        'khand': ['Khand', 'sans-serif'],
        'technor': ['Technor', 'sans-serif'],
      }
    }
  }
}
```

### Component Themes
- **Premium Theme**: Dark mode with gradients and animations
- **White Sheet Theme**: Clean, minimal design for focused work
- **Standard Theme**: Balanced light/dark mode with accessibility

### Typography System
```css
/* Global typography classes */
.text-display-1 { @apply text-4xl font-bold tracking-tight; }
.text-heading-1 { @apply text-2xl font-semibold; }
.text-body-1 { @apply text-base font-normal; }
.text-caption { @apply text-sm text-gray-600; }
```

## 🧩 Component Architecture

### UI Components (`src/components/ui/`)
```typescript
// Base components following Radix UI patterns
- Button: Variants (primary, secondary, ghost, destructive)
- Card: Container with header, content, footer
- Input: Form inputs with validation states
- Badge: Status indicators and tags
- Tabs: Tabbed navigation interface
```

### Feature Components

#### Chat System (`src/components/chat/`)
```typescript
// AI Chat Interface
- ChatInterface: Main chat container
- MessageList: Scrollable message history
- MessageInput: Input with file upload and commands
- StreamingMessage: Real-time AI response streaming
- ToolInvocationLoader: Visual feedback for AI tool use

// Chat Management
- ConversationList: Sidebar with conversation history
- ConversationManager: CRUD operations for conversations
- CategoryManager: Chat categorization and organization
```

#### Skill Trees (`src/components/tree/`)
```typescript
// Interactive Visualizations
- CompetenceTreeView: Main skill tree interface
- TreeNode: Individual skill nodes with interactions
- DynamicDepthControl: Zoom and navigation controls
- AlternativePathsExplorer: Career path discovery

// Performance Optimized
- OptimizedCompetenceTreeView: Large dataset handling
- VirtualizedTreeView: Virtualization for 1000+ nodes
- WebGLTreeRenderer: Hardware-accelerated rendering
```

#### Assessments (`src/components/hexaco-test/`, `src/components/holland-test/`)
```typescript
// Personality Assessments
- TestInterface: Question presentation and navigation
- ResultScreen: Comprehensive results visualization
- HexacoChart: Radar chart for personality dimensions
```

### Layout Components (`src/components/layout/`)
```typescript
- MainLayout: Primary application shell
- WhiteSheetLayout: Minimal layout for focused tasks
- Navbar: Main navigation with user menu
- NewSidebar: Collapsible sidebar with navigation
```

## 🔄 State Management

### Zustand Stores (`src/stores/`)
```typescript
// Onboarding State
interface OnboardingStore {
  currentStep: number;
  userData: UserData;
  assessmentResults: AssessmentResults;
  setCurrentStep: (step: number) => void;
  updateUserData: (data: Partial<UserData>) => void;
}

// Dynamic Tree State
interface DynamicTreeStore {
  selectedNode: TreeNode | null;
  expandedNodes: Set<string>;
  treeData: TreeData;
  setSelectedNode: (node: TreeNode) => void;
  toggleNodeExpansion: (nodeId: string) => void;
}
```

### Context Providers (`src/contexts/`)
```typescript
// Theme Management
const ThemeContext = createContext<{
  theme: 'light' | 'dark' | 'premium';
  setTheme: (theme: string) => void;
}>();

// Color Customization
const ColorContext = createContext<{
  primaryColor: string;
  accentColor: string;
  updateColors: (colors: ColorScheme) => void;
}>();
```

## 🌐 API Integration

### Service Layer (`src/services/`)
```typescript
// Base API Client
class ApiService {
  private baseURL = process.env.NEXT_PUBLIC_BACKEND_URL;
  
  async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const token = localStorage.getItem('authToken');
    return fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    }).then(res => res.json());
  }
}

// Specialized Services
- AuthService: Authentication and user management
- ChatService: AI conversation handling
- AssessmentService: Personality and career tests
- CareerService: Job recommendations and career data
- SkillTreeService: Competence tree operations
```

### API Client Examples
```typescript
// Authentication
const authService = new AuthService();
const user = await authService.login(email, password);
const profile = await authService.getCurrentUser();

// AI Chat
const chatService = new ChatService();
const response = await chatService.sendMessage(conversationId, message);
const conversation = await chatService.createConversation(title);

// Career Recommendations
const careerService = new CareerService();
const jobs = await careerService.getRecommendations(userId);
const savedJobs = await careerService.getSavedJobs();
```

## 🎯 Routing & Navigation

### App Router Structure (`src/app/`)
```typescript
// Public Routes
/                          → Landing page
/login                     → Authentication
/register                  → User registration

// Protected Routes
/dashboard                 → User dashboard
/profile                   → User profile management
/chat                      → AI conversation interface
/tree                      → Interactive skill trees
/assessments/hexaco        → HEXACO personality test
/assessments/holland       → Holland Code career test
/space                     → Personal workspace
/peers                     → Peer networking
/education                 → Course recommendations

// Dynamic Routes
/chat/[conversationId]     → Specific conversation
/peers/[peerId]           → Peer profile
/classes/[classId]        → Course details
```

### Route Protection
```typescript
// Authentication Middleware
export function middleware(request: NextRequest) {
  const token = request.cookies.get('authToken');
  const isAuthPage = request.nextUrl.pathname.startsWith('/login');
  const isProtectedPage = !isPublicRoute(request.nextUrl.pathname);

  if (!token && isProtectedPage) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  if (token && isAuthPage) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }
}
```

## ⚡ Performance Optimization

### Bundle Optimization (`next.config.js`)
```javascript
const nextConfig = {
  // Code splitting and tree shaking
  webpack: (config, { isServer, dev }) => {
    if (!dev && !isServer) {
      config.optimization.splitChunks = {
        chunks: 'all',
        cacheGroups: {
          framework: {
            name: 'framework',
            test: /[\\/]node_modules[\\/](react|react-dom)[\\/]/,
            priority: 40,
          },
          lib: {
            test: (module) => module.size() > 160000,
            name: (module) => `lib-${crypto.createHash('sha1').update(module.identifier()).digest('hex').substring(0, 8)}`,
            priority: 30,
          }
        }
      };
    }
    return config;
  },

  // Image optimization
  images: {
    domains: ['localhost', 'orientor.com'],
    formats: ['image/avif', 'image/webp'],
  },

  // Compression and caching
  compress: true,
  poweredByHeader: false,
};
```

### Lazy Loading & Code Splitting
```typescript
// Component lazy loading
const LazySkillTree = lazy(() => import('@/components/tree/CompetenceTreeView'));
const LazyChat = lazy(() => import('@/components/chat/ChatInterface'));

// Route-based splitting
const DynamicTreePage = dynamic(() => import('./tree/page'), {
  loading: () => <LoadingSpinner />,
  ssr: false, // Disable SSR for heavy components
});
```

### Performance Monitoring
```typescript
// Performance utilities
export const performanceMonitor = {
  measureRender: (componentName: string) => {
    performance.mark(`${componentName}-start`);
    return () => {
      performance.mark(`${componentName}-end`);
      performance.measure(componentName, `${componentName}-start`, `${componentName}-end`);
    };
  },

  trackUserInteraction: (action: string, metadata?: object) => {
    // Analytics tracking
    analytics.track(action, metadata);
  }
};
```

## 🎨 Animation & Interactions

### Framer Motion Integration
```typescript
// Page transitions
const pageVariants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 }
};

// Component animations
const cardVariants = {
  hover: { scale: 1.02, boxShadow: "0 10px 30px rgba(0,0,0,0.1)" },
  tap: { scale: 0.98 }
};

// Stagger animations for lists
const containerVariants = {
  animate: {
    transition: {
      staggerChildren: 0.1
    }
  }
};
```

### Interactive Elements
```typescript
// Skill tree interactions
const TreeNode = ({ node, onClick, onHover }) => (
  <motion.div
    whileHover={{ scale: 1.1 }}
    whileTap={{ scale: 0.95 }}
    onClick={() => onClick(node)}
    onHoverStart={() => onHover(node)}
    className="cursor-pointer"
  >
    {node.title}
  </motion.div>
);
```

## 🔐 Authentication & Security

### Auth Flow
```typescript
// Login process
const handleLogin = async (email: string, password: string) => {
  try {
    const response = await authService.login(email, password);
    localStorage.setItem('authToken', response.access_token);
    router.push('/dashboard');
  } catch (error) {
    setError('Invalid credentials');
  }
};

// Token management
const useAuth = () => {
  const [user, setUser] = useState<User | null>(null);
  
  useEffect(() => {
    const token = localStorage.getItem('authToken');
    if (token) {
      authService.getCurrentUser()
        .then(setUser)
        .catch(() => {
          localStorage.removeItem('authToken');
          router.push('/login');
        });
    }
  }, []);

  return { user, logout: () => {
    localStorage.removeItem('authToken');
    setUser(null);
    router.push('/login');
  }};
};
```

### Protected Routes
```typescript
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { user } = useAuth();
  const router = useRouter();

  if (!user) {
    router.push('/login');
    return <LoadingSpinner />;
  }

  return <>{children}</>;
};
```

## 🚀 Development Workflow

### Local Development Setup
```bash
# 1. Install dependencies
npm install

# 2. Set up environment variables
cp .env.example .env.local
# Edit .env.local with your configuration

# 3. Run development server
npm run dev

# 4. Open browser
# http://localhost:3000
```

### Environment Variables
```bash
# .env.local
NEXT_PUBLIC_API_URL=/api
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_ANALYTICS_ID=your-analytics-id
```

### Build & Deployment
```bash
# Production build
npm run build

# Analyze bundle size
npm run build:analyze

# Test production build locally
npm run start

# Lint and format
npm run lint
npm run lint:fix
```

## 🧪 Testing Strategy

### Component Testing
```typescript
// Example test with React Testing Library
import { render, screen, fireEvent } from '@testing-library/react';
import { ChatInterface } from '@/components/chat/ChatInterface';

describe('ChatInterface', () => {
  test('sends message when form is submitted', async () => {
    render(<ChatInterface conversationId="123" />);
    
    const input = screen.getByPlaceholderText('Type your message...');
    const sendButton = screen.getByRole('button', { name: /send/i });
    
    fireEvent.change(input, { target: { value: 'Hello AI' } });
    fireEvent.click(sendButton);
    
    expect(mockSendMessage).toHaveBeenCalledWith('123', 'Hello AI');
  });
});
```

### Integration Testing
```typescript
// API integration tests
describe('AuthService', () => {
  test('login returns user data on success', async () => {
    const mockResponse = { access_token: 'token123', user: { id: 1 } };
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockResponse)
    });

    const result = await authService.login('test@example.com', 'password');
    expect(result).toEqual(mockResponse);
  });
});
```

## 🎨 Styling Guidelines

### TailwindCSS Best Practices
```typescript
// Component styling with consistent patterns
const Button = ({ variant = 'primary', size = 'md', children, ...props }) => {
  const baseClasses = 'font-medium rounded-lg transition-colors duration-200';
  const variantClasses = {
    primary: 'bg-blue-500 hover:bg-blue-600 text-white',
    secondary: 'bg-gray-200 hover:bg-gray-300 text-gray-900',
    ghost: 'hover:bg-gray-100 text-gray-700'
  };
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg'
  };

  return (
    <button
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]}`}
      {...props}
    >
      {children}
    </button>
  );
};
```

### Custom CSS Modules
```css
/* component.module.css */
.card {
  @apply bg-white rounded-lg shadow-sm border border-gray-200;
  transition: all 0.2s ease-in-out;
}

.card:hover {
  @apply shadow-md border-gray-300;
  transform: translateY(-2px);
}

.darkMode .card {
  @apply bg-gray-800 border-gray-700;
}
```

## 📱 Responsive Design

### Breakpoint Strategy
```typescript
// Responsive utilities
const useBreakpoint = () => {
  const [breakpoint, setBreakpoint] = useState('lg');

  useEffect(() => {
    const updateBreakpoint = () => {
      if (window.innerWidth < 640) setBreakpoint('sm');
      else if (window.innerWidth < 768) setBreakpoint('md');
      else if (window.innerWidth < 1024) setBreakpoint('lg');
      else setBreakpoint('xl');
    };

    updateBreakpoint();
    window.addEventListener('resize', updateBreakpoint);
    return () => window.removeEventListener('resize', updateBreakpoint);
  }, []);

  return breakpoint;
};
```

### Mobile-First Components
```typescript
const ResponsiveNavigation = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const breakpoint = useBreakpoint();

  return (
    <nav className="bg-white shadow-sm">
      {/* Mobile menu button */}
      <div className="md:hidden">
        <button onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}>
          <MenuIcon />
        </button>
      </div>

      {/* Navigation items */}
      <div className={`${isMobileMenuOpen ? 'block' : 'hidden'} md:block`}>
        <NavigationItems />
      </div>
    </nav>
  );
};
```

## 🔍 Debugging & DevTools

### Development Tools
```typescript
// Debug utilities
const debugLog = (message: string, data?: any) => {
  if (process.env.NODE_ENV === 'development') {
    console.log(`[DEBUG] ${message}`, data);
  }
};

// Performance profiling
const usePerformanceProfiler = (componentName: string) => {
  useEffect(() => {
    const startTime = performance.now();
    return () => {
      const endTime = performance.now();
      debugLog(`${componentName} render time`, `${endTime - startTime}ms`);
    };
  });
};
```

### Error Boundaries
```typescript
class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    // Log to error reporting service
  }

  render() {
    if (this.state.hasError) {
      return <ErrorFallback onRetry={() => this.setState({ hasError: false })} />;
    }

    return this.props.children;
  }
}
```

## 📈 Analytics & Monitoring

### User Analytics
```typescript
const analytics = {
  track: (event: string, properties?: object) => {
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', event, properties);
    }
  },

  page: (url: string) => {
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('config', process.env.NEXT_PUBLIC_GA_ID, {
        page_path: url,
      });
    }
  }
};

// Usage in components
const ChatInterface = () => {
  const sendMessage = (message: string) => {
    analytics.track('chat_message_sent', { message_length: message.length });
    // ... send message logic
  };
};
```

---

## 🤖 AI Assistant Guidelines

When working with the frontend:

1. **Follow TypeScript best practices** - Use proper typing for all components and functions
2. **Maintain responsive design** - Test components on mobile, tablet, and desktop
3. **Use performance optimization** - Implement lazy loading for heavy components
4. **Follow component patterns** - Use consistent prop interfaces and state management
5. **Test user interactions** - Verify all interactive elements work correctly
6. **Optimize bundle size** - Use dynamic imports and code splitting
7. **Maintain accessibility** - Include proper ARIA labels and keyboard navigation
8. **Update type definitions** - Keep TypeScript types in sync with backend API changes

The frontend provides a modern, responsive, and performant interface for the AI career guidance platform with comprehensive features for user interaction and visualization.