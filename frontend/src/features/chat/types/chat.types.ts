// Chat Feature Types
export interface Message {
  id: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at: string;
  tokens_used?: number;
}

export interface Conversation {
  id: number;
  title: string;
  auto_generated_title: boolean;
  category_id: number | null;
  is_favorite: boolean;
  is_archived: boolean;
  created_at: string;
  updated_at: string;
  last_message_at: string | null;
  message_count: number;
  total_tokens_used: number;
}

export interface Category {
  id: number;
  name: string;
  description: string | null;
  color: string | null;
  conversation_count: number;
  created_at: string;
}

export type ChatMode = 'default' | 'socratic' | 'claude';

export interface ChatState {
  messages: Message[];
  currentConversation: Conversation | null;
  selectedCategory: Category | null;
  isTyping: boolean;
  chatMode: ChatMode;
}

export interface ChatActions {
  sendMessage: (message: string) => Promise<void>;
  selectConversation: (conversation: Conversation) => void;
  createNewConversation: () => void;
  archiveConversation: () => Promise<void>;
  deleteConversation: () => Promise<void>;
  updateTitle: (title: string) => Promise<void>;
}