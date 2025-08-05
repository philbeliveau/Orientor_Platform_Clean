import { lazyWithPreload } from '../utils/lazyWithPreload';

// Tree components - Heavy visualization components
export const CompetenceTreeView = lazyWithPreload(
  () => import(/* webpackChunkName: "competence-tree" */ './tree/CompetenceTreeView.refactored')
);

export const EnhancedDynamicCareerTree = lazyWithPreload(
  () => import(/* webpackChunkName: "career-tree" */ './tree/EnhancedDynamicCareerTree')
);

export const AlternativePathsExplorer = lazyWithPreload(
  () => import(/* webpackChunkName: "paths-explorer" */ './tree/AlternativePathsExplorer')
);

export const JobSkillsTree = lazyWithPreload(
  () => import(/* webpackChunkName: "job-skills-tree" */ './jobs/JobSkillsTree')
);

// Chat components - Interactive components
export const ChatInterface = lazyWithPreload(
  () => import(/* webpackChunkName: "chat-interface" */ './chat/ChatInterface')
);

export const EnhancedChat = lazyWithPreload(
  () => import(/* webpackChunkName: "enhanced-chat" */ './chat/EnhancedChat')
);

export const SocraticChat = lazyWithPreload(
  () => import(/* webpackChunkName: "socratic-chat" */ './chat/SocraticChat')
);

// Career components
export const CareerAnalysisChat = lazyWithPreload(
  () => import(/* webpackChunkName: "career-analysis" */ './classes/CareerAnalysisChat')
);

export const CareerInsightsDashboard = lazyWithPreload(
  () => import(/* webpackChunkName: "career-insights" */ './classes/CareerInsightsDashboard')
);

export const TimelineVisualization = lazyWithPreload(
  () => import(/* webpackChunkName: "timeline-viz" */ './career/TimelineVisualization')
);

export const SkillRelationshipGraph = lazyWithPreload(
  () => import(/* webpackChunkName: "skill-graph" */ './career/SkillRelationshipGraph')
);

export const CareerFitAnalyzer = lazyWithPreload(
  () => import(/* webpackChunkName: "career-fit" */ './space/CareerFitAnalyzer')
);

// Onboarding components
export const ChatOnboard = lazyWithPreload(
  () => import(/* webpackChunkName: "chat-onboard" */ './onboarding/ChatOnboard')
);

export const SwipeRecommendations = lazyWithPreload(
  () => import(/* webpackChunkName: "swipe-rec" */ './onboarding/SwipeRecommendations')
);

// Landing page
export const LandingPage = lazyWithPreload(
  () => import(/* webpackChunkName: "landing" */ './landing/LandingPage')
);

// Layout components
export const MainLayout = lazyWithPreload(
  () => import(/* webpackChunkName: "main-layout" */ './layout/MainLayout')
);

// UI components
export const SkillShowcase = lazyWithPreload(
  () => import(/* webpackChunkName: "skill-showcase" */ './ui/SkillShowcase')
);

// Preload critical components after initial render
export const preloadCriticalComponents = () => {
  // Preload commonly used components
  setTimeout(() => {
    CompetenceTreeView.preload();
    ChatInterface.preload();
  }, 2000);
};