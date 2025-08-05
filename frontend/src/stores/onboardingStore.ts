import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { 
  OnboardingState, 
  OnboardingResponse, 
  ChatMessage, 
  PsychProfile,
  OnboardingQuestion 
} from '../types/onboarding';
import { onboardingService } from '../services/onboardingService';

interface OnboardingStore extends OnboardingState {
  // Actions
  addMessage: (message: Omit<ChatMessage, 'id' | 'timestamp'>) => void;
  addResponse: (response: Omit<OnboardingResponse, 'timestamp'>) => void;
  nextQuestion: () => void;
  setTyping: (isTyping: boolean) => void;
  setPsychProfile: (profile: PsychProfile) => void;
  complete: () => void;
  reset: () => void;
  
  // API Actions
  startOnboarding: () => Promise<void>;
  saveResponseToAPI: (response: OnboardingResponse) => Promise<void>;
  completeOnboarding: () => Promise<void>;
  loadOnboardingStatus: () => Promise<void>;
  
  // Getters
  getCurrentQuestion: () => OnboardingQuestion | null;
  getProgress: () => number;
}

// Predefined onboarding questions based on HEXACO and RIASEC frameworks
const questions: OnboardingQuestion[] = [
  // Emotion-first opener
  {
    id: 'emotion-1',
    text: "What makes you feel most alive?",
    type: 'emotion'
  },
  
  // HEXACO-based questions
  {
    id: 'hexaco-1',
    text: "When working on a team project, do you prefer to lead the discussion or contribute your ideas quietly?",
    type: 'hexaco',
    dimension: 'extraversion',
    weight: 0.8
  },
  {
    id: 'hexaco-2',
    text: "How do you typically handle stressful situations - do you stay calm or do your emotions guide your response?",
    type: 'hexaco',
    dimension: 'emotionality',
    weight: 0.7
  },
  {
    id: 'hexaco-3',
    text: "When planning a project, do you prefer detailed schedules or flexible approaches that can adapt as you go?",
    type: 'hexaco',
    dimension: 'conscientiousness',
    weight: 0.8
  },
  {
    id: 'hexaco-4',
    text: "Are you more interested in tried-and-true methods or exploring innovative, untested approaches?",
    type: 'hexaco',
    dimension: 'openness',
    weight: 0.7
  },
  
  // RIASEC career interest questions
  {
    id: 'riasec-1',
    text: "Would you rather work with your hands building something tangible, or work with ideas and concepts?",
    type: 'riasec',
    dimension: 'realistic',
    weight: 0.9
  },
  {
    id: 'riasec-2',
    text: "Do you find yourself drawn to helping people solve their problems, or analyzing data to find patterns?",
    type: 'riasec',
    dimension: 'social',
    weight: 0.8
  },
  {
    id: 'riasec-3',
    text: "When facing a challenge, do you prefer to research and investigate thoroughly, or take action and learn through doing?",
    type: 'riasec',
    dimension: 'investigative',
    weight: 0.7
  },
  
  // Forward-looking question
  {
    id: 'future-1',
    text: "In 5 years, what impact do you want to have made in the world?",
    type: 'future'
  }
];

const initialState: OnboardingState = {
  currentQuestionIndex: 0,
  responses: [],
  messages: [{
    id: 'welcome',
    type: 'system',
    content: 'Hey',
    timestamp: new Date()
  }],
  isTyping: false,
  isComplete: false,
  psychProfile: undefined
};

export const useOnboardingStore = create<OnboardingStore>()(
  devtools(
    (set, get) => ({
      ...initialState,
      
      addMessage: (message) => {
        const newMessage: ChatMessage = {
          ...message,
          id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          timestamp: new Date()
        };
        
        set((state) => ({
          messages: [...state.messages, newMessage]
        }), false, 'addMessage');
      },
      
      addResponse: (response) => {
        const newResponse: OnboardingResponse = {
          ...response,
          timestamp: new Date()
        };
        
        set((state) => ({
          responses: [...state.responses, newResponse]
        }), false, 'addResponse');
      },
      
      nextQuestion: () => {
        const { currentQuestionIndex } = get();
        const nextIndex = currentQuestionIndex + 1;
        
        if (nextIndex >= questions.length) {
          get().complete();
        } else {
          set({ currentQuestionIndex: nextIndex }, false, 'nextQuestion');
        }
      },
      
      setTyping: (isTyping) => {
        set({ isTyping }, false, 'setTyping');
      },
      
      setPsychProfile: (profile) => {
        set({ psychProfile: profile }, false, 'setPsychProfile');
      },
      
      complete: () => {
        set({ isComplete: true }, false, 'complete');
      },
      
      reset: () => {
        set(initialState, false, 'reset');
      },
      
      // API Actions
      startOnboarding: async () => {
        try {
          await onboardingService.startOnboarding();
        } catch (error) {
          console.error('Failed to start onboarding session:', error);
          // Continue with local flow even if API fails
        }
      },
      
      saveResponseToAPI: async (response: OnboardingResponse) => {
        try {
          await onboardingService.saveResponse(response);
        } catch (error) {
          console.error('Failed to save response to API:', error);
          // Continue with local flow even if API fails
        }
      },
      
      completeOnboarding: async () => {
        try {
          const { responses, psychProfile } = get();
          await onboardingService.completeOnboarding({
            responses,
            psychProfile
          });
          // Mark as complete locally after successful API call
          set({ isComplete: true }, false, 'completeOnboarding');
        } catch (error) {
          console.error('Failed to complete onboarding on API:', error);
          // Still mark as complete locally even if API fails
          set({ isComplete: true }, false, 'completeOnboarding');
        }
      },
      
      loadOnboardingStatus: async () => {
        try {
          const status = await onboardingService.getStatus();
          if (status.isComplete) {
            set({ isComplete: true }, false, 'loadOnboardingStatus');
          }
        } catch (error) {
          console.error('Failed to load onboarding status:', error);
          // Don't update state if API fails
        }
      },
      
      getCurrentQuestion: () => {
        const { currentQuestionIndex } = get();
        return questions[currentQuestionIndex] || null;
      },
      
      getProgress: () => {
        const { currentQuestionIndex } = get();
        return Math.round((currentQuestionIndex / questions.length) * 100);
      }
    }),
    {
      name: 'onboarding-store'
    }
  )
);