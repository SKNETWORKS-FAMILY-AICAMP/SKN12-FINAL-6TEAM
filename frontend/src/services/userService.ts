import { apiClient } from './apiClient';
import { UserProfile, ChatHistory, TestResult } from '../types';

export interface UserProfileResponse {
  user_id: number;
  name: string;
  nickname: string;
  email: string | null;
  user_type: string;
  status: string;
  join_date: string;
  total_chats: number;
  total_tests: number;
}

export interface ChatHistoryResponse {
  chat_history: Array<{
    id: string;
    character_name: string;
    character_avatar: string;
    date: string;
    last_message_time: string;
    messages: Array<{
      text: string;
      sender: string;
      timestamp: string;
    }>;
  }>;
  total: number;
  has_more: boolean;
}

export interface TestResultResponse {
  test_results: Array<{
    id: string;
    test_type: string;
    character_match: string;
    interpretation: string;
    date: string;
    created_at: string;
    images: string[];
  }>;
  total: number;
  has_more: boolean;
}

export interface NicknameCheckResponse {
  available: boolean;
  message: string;
}

class UserService {
  // 간단한 캐시 구현
  private profileCache = new Map<number, { data: UserProfile; timestamp: number }>();
  private readonly CACHE_DURATION = 5 * 60 * 1000; // 5분

  // 사용자 프로필 조회 (캐싱 적용)
  async getUserProfile(userId: number): Promise<UserProfile> {
    // 캐시 확인
    const cached = this.profileCache.get(userId);
    if (cached && Date.now() - cached.timestamp < this.CACHE_DURATION) {
      return cached.data;
    }
    const response = await apiClient.get<UserProfileResponse>(`/users/users/${userId}/profile`);
    
    // 백엔드 응답을 프론트엔드 타입으로 변환
    const profile: UserProfile = {
      id: response.user_id.toString(),
      name: response.name,
      email: response.email || '',
      joinDate: response.join_date,
      totalTests: response.total_tests,
      totalChats: response.total_chats
    };

    // 캐시에 저장
    this.profileCache.set(userId, { data: profile, timestamp: Date.now() });
    
    return profile;
  }

  // 채팅 히스토리 조회
  async getChatHistory(userId: number, skip: number = 0, limit: number = 10): Promise<ChatHistory[]> {
    const response = await apiClient.get<ChatHistoryResponse>(`/users/users/${userId}/chat-history`, {
      skip,
      limit
    });
    
    // 백엔드 응답을 프론트엔드 타입으로 변환
    return response.chat_history.map(chat => ({
      id: chat.id,
      characterId: chat.id, // 임시로 세션 ID를 캐릭터 ID로 사용
      characterName: chat.character_name,
      characterAvatar: chat.character_avatar,
      date: chat.date,
      lastMessage: (chat.messages && chat.messages.length > 0) ? (chat.messages[chat.messages.length - 1]?.text || '') : '',
      messages: (chat.messages || []).filter(msg => msg && msg.timestamp).map(msg => ({
        id: `${chat.id}-${msg.timestamp}`, // 임시 ID 생성
        type: msg.sender as 'user' | 'assistant',
        content: msg.text || '',
        timestamp: msg.timestamp
      }))
    }));
  }

  // 테스트 결과 조회
  async getTestResults(userId: number, skip: number = 0, limit: number = 10): Promise<TestResult[]> {
    const response = await apiClient.get<TestResultResponse>(`/users/users/${userId}/test-results`, {
      skip,
      limit
    });
    
    // 백엔드 응답을 프론트엔드 타입으로 변환
    return response.test_results.map(test => ({
      id: test.id,
      testType: 'Drawing' as const, // 현재는 그림 검사만 지원
      result: test.character_match,
      characterMatch: test.character_match,
      date: test.date,
      description: test.interpretation,
      images: test.images
    }));
  }

  // 닉네임 중복 확인
  async checkNickname(userId: number, nickname: string): Promise<NicknameCheckResponse> {
    return await apiClient.post<NicknameCheckResponse>(`/users/users/${userId}/check-nickname?nickname=${encodeURIComponent(nickname)}`);
  }

  // 사용자 정보 업데이트
  async updateUser(userId: number, data: { nickname?: string }): Promise<UserProfileResponse> {
    const result = await apiClient.put<UserProfileResponse>(`/users/users/${userId}`, data);
    
    // 업데이트 후 캐시 무효화
    this.profileCache.delete(userId);
    
    return result;
  }

  // 캐시 수동 무효화 (필요시)
  clearCache(userId?: number): void {
    if (userId) {
      this.profileCache.delete(userId);
    } else {
      this.profileCache.clear();
    }
  }
}

export const userService = new UserService();