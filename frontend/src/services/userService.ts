import { apiClient } from './apiClient';
import { UserProfile, ChatHistory, TestResult, DrawingTest } from '../types';

export interface UserProfileResponse {
  user_id: number;
  name: string;
  nickname: string;
  email: string | null;
  profile_image_url?: string;
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
    const response = await apiClient.get<UserProfileResponse>(`/users/${userId}/profile`);
    
    // 백엔드 응답을 프론트엔드 타입으로 변환
    const profile: UserProfile = {
      id: response.user_id.toString(),
      name: response.name,
      email: response.email || '',
      profileImageUrl: response.profile_image_url ? 
        (response.profile_image_url.startsWith('http') ? 
          response.profile_image_url : 
          `${process.env.REACT_APP_API_URL || 'http://ec2-3-34-245-132.ap-northeast-2.compute.amazonaws.com/api'}${response.profile_image_url}`
        ) : undefined,
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
    const response = await apiClient.get<ChatHistoryResponse>(`/users/${userId}/chat-history`, {
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
    const response = await apiClient.get<DrawingTest[]>(`/api/v1/test/drawing-test-results/my-results`, {
      skip,
      limit
    });
    
    // 백엔드 응답을 프론트엔드 타입으로 변환
    return response.map(test => ({
      id: test.test_id.toString(),
      testType: 'Drawing' as const,
      result: test.result?.summary_text || '결과 분석 중입니다.',
      characterMatch: test.result?.persona_info?.persona_name || '분석 중',
      date: test.submitted_at,
      description: test.result?.summary_text || '자세한 내용은 결과보기를 확인하세요.',
      images: [test.image_url]
    }));
  }

  // 닉네임 중복 확인
  async checkNickname(userId: number, nickname: string): Promise<NicknameCheckResponse> {
    return await apiClient.post<NicknameCheckResponse>(`/users/${userId}/check-nickname?nickname=${encodeURIComponent(nickname)}`);
  }

  // 사용자 정보 업데이트
  async updateUser(userId: number, data: { nickname?: string }): Promise<UserProfileResponse> {
    const result = await apiClient.put<UserProfileResponse>(`/users/${userId}`, data);
    
    // 업데이트 후 캐시 무효화
    this.profileCache.delete(userId);
    
    return result;
  }

  // 프로필 이미지 업로드
  async uploadProfileImage(userId: number, file: File): Promise<{ message: string; profile_image_url: string }> {
    try {
      console.log('🖼️ 프로필 이미지 업로드 시작 - 사용자 ID:', userId);
      console.log('📁 파일 정보:', { name: file.name, size: file.size, type: file.type });
      
      // 토큰 확인
      const token = localStorage.getItem('access_token');
      if (!token) {
        throw new Error('인증 토큰이 없습니다. 다시 로그인해주세요.');
      }
      console.log('🔑 토큰 확인 완료:', token.substring(0, 20) + '...');
      
      const formData = new FormData();
      formData.append('file', file);
      
      console.log('📤 업로드 요청 전송...');
      const result = await apiClient.postFormData<{ message: string; profile_image_url: string }>(
        `/users/${userId}/upload-profile-image`,
        formData
      );
      
      console.log('✅ 업로드 성공:', result);
      
      // 업로드 후 캐시 무효화
      this.profileCache.delete(userId);
      
      // URL을 절대 경로로 변환하여 반환
      const absoluteUrl = result.profile_image_url.startsWith('http') ? 
        result.profile_image_url : 
        `${process.env.REACT_APP_API_URL || 'http://ec2-3-34-245-132.ap-northeast-2.compute.amazonaws.com/api'}${result.profile_image_url}`;
      
      return {
        ...result,
        profile_image_url: absoluteUrl
      };
    } catch (error: any) {
      console.error('❌ 프로필 이미지 업로드 실패:', error);
      
      // 401 에러 처리
      if (error.response?.status === 401) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_info');
        throw new Error('인증이 만료되었습니다. 다시 로그인해주세요.');
      }
      
      // 기타 에러
      throw new Error(error.response?.data?.detail || error.message || '이미지 업로드 중 오류가 발생했습니다.');
    }
  }

  // 캐시 수동 무효화 (필요시)
  clearCache(userId?: number): void {
    if (userId) {
      this.profileCache.delete(userId);
    } else {
      this.profileCache.clear();
    }
  }

  /**
   * 회원 탈퇴 (계정 완전 삭제)
   */
  async deleteAccount(userId: number): Promise<{ message: string; deleted_user_id: number }> {
    try {
      const result = await apiClient.delete<{ message: string; deleted_user_id: number }>(`/users/${userId}/account`);
      // 캐시 클리어
      this.clearCache();
      return result;
    } catch (error) {
      console.error('Failed to delete account:', error);
      throw error;
    }
  }
}

export const userService = new UserService();