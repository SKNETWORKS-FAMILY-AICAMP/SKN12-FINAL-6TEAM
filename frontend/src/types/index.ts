export interface SearchResult {
  id: string;
  name: string;
  description: string;
  avatar: string;
}

export interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface Rating {
  id: string;
  name: string;
  rating: number;
  comment: string;
}

export interface ChatHistory {
  id: string;
  characterId: string;
  characterName: string;
  characterAvatar: string;
  messages: ChatMessage[];
  date: string;
  lastMessage: string;
}

export interface TestResult {
  id: string;
  testType: 'HTP' | 'Drawing';
  result: string;
  characterMatch: string;
  date: string;
  description: string;
  images?: string[];
}

export interface UserProfile {
  id: string;
  name: string;
  email: string;
  joinDate: string;
  totalTests: number;
  totalChats: number;
}

export type ScreenType = 'landing' | 'main' | 'chat' | 'results' | 'mypage';

export interface AppState {
  currentScreen: ScreenType;
  selectedCharacter: SearchResult | null;
  chatMessages: ChatMessage[];
  chatHistory: ChatHistory[];
  testResults: TestResult[];
  userProfile: UserProfile | null;
  showModal: boolean;
  showRatingModal: boolean;
}