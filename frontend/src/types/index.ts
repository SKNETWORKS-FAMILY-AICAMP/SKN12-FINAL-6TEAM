// 캐릭터 정보
export interface SearchResult {
  id: string;
  name: string;
  description: string;
  avatar: string;
}

// 채팅 메시지 (백엔드 API 응답 형식에 맞춤)
export interface ChatMessage {
  chat_messages_id: string;
  session_id: string;
  sender_type: 'user' | 'assistant';
  content: string;
  created_at: string;
}

// 프론트엔드 전용 메시지 타입 (기존 코드와 호환성 유지)
export interface FrontendChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

// 채팅 세션 (백엔드 API 응답 형식)
export interface ChatSession {
  chat_sessions_id: string;
  user_id: number;
  friends_id: number;
  session_name?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// 채팅 세션 상세 정보 (메시지 포함)
export interface ChatSessionDetail extends ChatSession {
  messages: ChatMessage[];
}

// 메시지 전송 요청
export interface SendMessageRequest {
  content: string;
  enable_tts?: boolean;
  voice_type?: string;
}

// 메시지 전송 응답
export interface SendMessageResponse {
  user_message: ChatMessage;
  assistant_message: ChatMessage;
  session_updated: boolean;
}

// 세션 생성 요청
export interface CreateSessionRequest {
  user_id: number;
  friends_id: number;
  session_name?: string;
}


// 평가 정보
export interface Rating {
  id: string;
  name: string;
  rating: number;
  comment: string;
}

// 채팅 기록 (프론트엔드용)
export interface ChatHistory {
  id: string;
  characterId: string;
  characterName: string;
  characterAvatar: string;
  messages: FrontendChatMessage[];
  date: string;
  lastMessage: string;
}

// 테스트 결과 (기존)
export interface TestResult {
  id: string;
  testType: 'HTP' | 'Drawing';
  result: string;
  characterMatch: string;
  date: string;
  description: string;
  images?: string[];
}

// 백엔드 API - 친구 정보
export interface FriendInfo {
  friends_id: number;
  friends_name: string;
  friends_description: string;
  tts_audio_url?: string;
  tts_voice_type?: string;
}

// 백엔드 API - 그림 테스트 결과
export interface DrawingTestResult {
  result_id: number;
  friends_type?: number;
  summary_text?: string;
  created_at: string;
  friend_info?: FriendInfo;
}

// 백엔드 API - 그림 테스트
export interface DrawingTest {
  test_id: number;
  user_id: number;
  image_url: string;
  submitted_at: string;
  result?: DrawingTestResult;
}

// 사용자 프로필
export interface UserProfile {
  id: string;
  name: string;
  email: string;
  joinDate: string;
  totalTests: number;
  totalChats: number;
}

// 화면 타입
export type ScreenType = 'landing' | 'main' | 'chat' | 'results' | 'mypage';

// 앱 상태
export interface AppState {
  currentScreen: ScreenType;
  selectedCharacter: SearchResult | null;
  chatMessages: FrontendChatMessage[];
  chatHistory: ChatHistory[];
  testResults: TestResult[];
  userProfile: UserProfile | null;
  showModal: boolean;
  showRatingModal: boolean;
}

// API 에러 응답
export interface ApiError {
  error: string;
  detail?: string;
  code?: number;
}