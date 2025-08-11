import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import Navigation from '../common/Navigation';
import { ChatHistory, TestResult, UserProfile } from '../../types';
import { MessageCircle, FileText, User, Calendar, Edit2, Camera, Check, X, Loader } from 'lucide-react';
import { userService } from '../../services/userService';
import { authService } from '../../services/authService';
import { chatService } from '../../services/chatService';
import { testService } from '../../services/testService';
import { Button } from "../../components/ui/button";
import DeleteAccountModal from '../common/DeleteAccountModal';

interface MyPageProps {
  onNewChat: () => void;
  onDeleteAccount: () => void;
  onNavigate?: (screen: string) => void;
  onContinueChat?: (chatId: string, characterName: string) => void;
  onUpdateProfile?: (profile: UserProfile) => void;
}

const MyPage: React.FC<MyPageProps> = ({
  onNewChat,
  onDeleteAccount,
  onNavigate,
  onContinueChat,
  onUpdateProfile
}) => {
  const navigate = useNavigate();
  
  // API에서 가져온 실제 데이터 상태
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [chatHistory, setChatHistory] = useState<ChatHistory[]>([]);
  const [testResults, setTestResults] = useState<TestResult[]>([]);
  const [isLoadingProfile, setIsLoadingProfile] = useState(false);
  
  const [isEditingProfile, setIsEditingProfile] = useState(false);
  const [editingName, setEditingName] = useState(userProfile?.name || '');
  const [profileImage, setProfileImage] = useState<string | null>(null);
  const [isUploadingImage, setIsUploadingImage] = useState(false);
  const [isCheckingNickname, setIsCheckingNickname] = useState(false);
  const [nicknameCheckResult, setNicknameCheckResult] = useState<'available' | 'taken' | 'error' | null>(null);
  const [isNicknameChecked, setIsNicknameChecked] = useState(false);
  const [nameError, setNameError] = useState<string | null>(null);
  const [imageError, setImageError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [saveSuccess, setSaveSuccess] = useState(false);
  
  // 회원탈퇴 모달 상태
  const [showDeleteAccountModal, setShowDeleteAccountModal] = useState(false);
  
  // 현재 로그인된 사용자 ID 상태
  const [currentUserId, setCurrentUserId] = useState<number | null>(null);
  
  // 실제 사용자 정보 로드
  useEffect(() => {
    const loadCurrentUser = async () => {
      try {
        console.log('🔍 MyPage - 사용자 인증 상태 확인 시작');
        
        // 1. localStorage에서 토큰 확인
        const token = localStorage.getItem('access_token');
        console.log('🔑 저장된 토큰:', token ? `${token.substring(0, 20)}...` : 'None');
        
        // 2. authService에서 직접 userId 가져오기
        const userId = authService.getCurrentUserId();
        console.log('👤 authService에서 가져온 userId:', userId);
        
        // 3. authService 인증 상태 확인
        const isAuthenticated = authService.isAuthenticated();
        console.log('🔐 인증 상태:', isAuthenticated);
        
        if (userId && isAuthenticated) {
          setCurrentUserId(userId);
          console.log('✅ 마이페이지 - 현재 로그인된 사용자 ID:', userId);
        } else {
          console.log('🔄 API를 통해 사용자 정보 확인 시도');
          // API를 통해 사용자 정보 확인
          const user = await authService.getCurrentUser();
          if (user) {
            setCurrentUserId(user.id);
            console.log('✅ 마이페이지 - API에서 사용자 ID 복구:', user.id);
          } else {
            console.error('❌ 사용자가 로그인되어 있지 않습니다.');
            alert('로그인이 필요합니다. 로그인 페이지로 이동합니다.');
            navigate('/');
          }
        }
      } catch (error) {
        console.error('❌ 사용자 정보 로드 실패:', error);
        alert('사용자 정보를 불러올 수 없습니다. 다시 로그인해주세요.');
        navigate('/');
      }
    };
    
    loadCurrentUser();
  }, [navigate]);
  
  // 디바운스 타이머 레퍼런스
  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null);
  
  // 무한 스크롤 관련 상태
  const [displayedChats, setDisplayedChats] = useState<ChatHistory[]>([]);
  const [displayedTests, setDisplayedTests] = useState<TestResult[]>([]);
  const [chatPage, setChatPage] = useState(0);
  const [testPage, setTestPage] = useState(0);
  const [isLoadingChats, setIsLoadingChats] = useState(false);
  const [isLoadingTests, setIsLoadingTests] = useState(false);
  const [hasMoreChats, setHasMoreChats] = useState(true);
  const [hasMoreTests, setHasMoreTests] = useState(true);
  const chatObserverRef = useRef<HTMLDivElement>(null);
  const testObserverRef = useRef<HTMLDivElement>(null);
  
  const ITEMS_PER_PAGE = 5;

  // 캐릭터 ID에 따른 아바타 매핑
  const getCharacterAvatar = (personaId: number | null): string => {
    const nameMap: { [key: number]: string } = {
      1: '추진이',
      2: '내면이',
      3: '관계이',
      4: '쾌락이',
      5: '안정이',
    };
    const name = personaId ? nameMap[personaId] : '내면이';
    return `/assets/persona/${name}.png`;
  };

  // 페르소나 ID에 따른 이름 매핑
  const getPersonaName = (personaType: number | null): string => {
    const nameMap: { [key: number]: string } = {
      1: '추진이',
      2: '내면이',
      3: '관계이',
      4: '쾌락이',
      5: '안정이',
    };
    return personaType ? nameMap[personaType] : '분석 중';
  };

  // 채팅 히스토리 초기 로드
  const loadInitialChats = useCallback(() => {
    const sortedChats = [...chatHistory].sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
    setDisplayedChats(sortedChats.slice(0, ITEMS_PER_PAGE));
    setChatPage(0);
    setHasMoreChats(sortedChats.length > ITEMS_PER_PAGE);
  }, [chatHistory]);

  // 검사 결과 초기 로드
  const loadInitialTests = useCallback(() => {
    const sortedTests = [...testResults].sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
    setDisplayedTests(sortedTests.slice(0, ITEMS_PER_PAGE));
    setTestPage(0);
    setHasMoreTests(sortedTests.length > ITEMS_PER_PAGE);
  }, [testResults]);

  // 실제 사용자 데이터 로드
  const loadUserData = useCallback(async () => {
    if (!currentUserId) {
      console.log('❌ currentUserId가 없어서 데이터 로드 중단');
      return;
    }
    
    try {
      setIsLoadingProfile(true);
      
      // 토큰 재확인
      const token = localStorage.getItem('access_token');
      if (!token) {
        console.error('❌ 토큰이 없습니다. 로그인이 필요합니다.');
        alert('로그인이 만료되었습니다. 다시 로그인해주세요.');
        navigate('/');
        return;
      }
      
      // 사용자 프로필 로드
      try {
        console.log('👤 프로필 로드 시작...');
        const profile = await userService.getUserProfile(currentUserId);
        console.log('✅ 프로필 로드 성공:', profile);
        setUserProfile(profile);
        setEditingName(profile.name);
      } catch (profileError) {
        console.error('❌ 프로필 로드 실패:', profileError);
        // 프로필 로드 실패 시 기본값 설정
        setUserProfile({
          id: currentUserId.toString(),
          name: '사용자',
          email: '',
          joinDate: new Date().toISOString(),
          totalTests: 0,
          totalChats: 0
        });
        setEditingName('사용자');
      }
      
      // 채팅 히스토리는 간소화
      try {
        const sessions = await chatService.getUserSessions(currentUserId);
        
        // 각 세션의 메시지 데이터 로드
        const chatHistoryWithMessages = await Promise.all(
          sessions.map(async (session) => {
            try {
              const messages = await chatService.getSessionMessages(session.chat_sessions_id);
              const lastMessage = messages.length > 0 
                ? messages[messages.length - 1]
                : null;
              
              const personaName = getPersonaName(session.persona_id);
              const avatar = getCharacterAvatar(session.persona_id);
              
              return {
                id: session.chat_sessions_id,
                characterId: session.persona_id?.toString() || '',
                characterName: session.session_name || personaName,
                characterAvatar: avatar,
                date: session.created_at.split('T')[0],
                lastMessage: lastMessage ? lastMessage.content : '채팅 기록이 있습니다.',
                messages: messages.map(msg => ({
                  id: msg.chat_messages_id,
                  type: msg.sender_type,
                  content: msg.content,
                  timestamp: new Date(msg.created_at).toISOString()
                }))
              };
            } catch (error) {
              console.error(`❌ 세션 ${session.chat_sessions_id} 메시지 로드 실패:`, error);
              const personaName = getPersonaName(session.persona_id);
              const avatar = getCharacterAvatar(session.persona_id);
              
              return {
                id: session.chat_sessions_id,
                characterId: session.persona_id?.toString() || '',
                characterName: session.session_name || personaName,
                characterAvatar: avatar,
                date: session.created_at.split('T')[0],
                lastMessage: '메시지 로드 실패',
                messages: []
              };
            }
          })
        );
        
        setChatHistory(chatHistoryWithMessages);
      } catch (chatError) {
        console.error('❌ 채팅 히스토리 로드 실패:', chatError);
        setChatHistory([]);
      }
      
      // 테스트 결과 로드
      try {
        const tests = await testService.getMyTestResults();
        
        setTestResults(tests.map(test => ({
          id: test.test_id.toString(),
          testType: 'Drawing' as const,
          result: test.result?.summary_text || '결과 분석 중입니다.',
          characterMatch: test.result?.persona_info?.persona_name || getPersonaName(test.result?.persona_type || null),
          date: test.submitted_at,
          description: test.result?.summary_text || '자세한 내용은 결과보기를 확인하세요.',
          images: [test.image_url]
        })));
      } catch (testError) {
        console.error('❌ 테스트 결과 로드 실패:', testError);
        setTestResults([]);
      }
      
    } catch (error: any) {
      console.error('❌ 사용자 데이터 로드 전체 실패:', error);
      
      // 401 에러인 경우 로그인 페이지로 리다이렉트
      if (error.response?.status === 401) {
        alert('인증이 만료되었습니다. 다시 로그인해주세요.');
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_info');
        navigate('/');
      }
    } finally {
      setIsLoadingProfile(false);
    }
  }, [currentUserId, navigate]);

  // API에서 실제 데이터 로드
  useEffect(() => {
    loadUserData();
  }, [loadUserData]);

  // 채팅 히스토리 초기화
  useEffect(() => {
    if (chatHistory.length > 0) {
      loadInitialChats();
    }
  }, [chatHistory, loadInitialChats]);

  // 테스트 결과 초기화
  useEffect(() => {
    if (testResults.length > 0) {
      loadInitialTests();
    }
  }, [testResults, loadInitialTests]);

  // 컴포넌트 언마운트 시 타이머 정리
  useEffect(() => {
    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, []);

  // 더 많은 채팅 로드
  const loadMoreChats = useCallback(async () => {
    if (isLoadingChats || !hasMoreChats) return;
    
    setIsLoadingChats(true);
    
    // 실제 구현에서는 API 호출
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const sortedChats = [...chatHistory].sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
    const nextPage = chatPage + 1;
    const startIndex = nextPage * ITEMS_PER_PAGE;
    const endIndex = startIndex + ITEMS_PER_PAGE;
    const newChats = sortedChats.slice(startIndex, endIndex);
    
    setDisplayedChats(prev => [...prev, ...newChats]);
    setChatPage(nextPage);
    setHasMoreChats(endIndex < sortedChats.length);
    setIsLoadingChats(false);
  }, [chatHistory, chatPage, isLoadingChats, hasMoreChats]);

  // 더 많은 검사 결과 로드
  const loadMoreTests = useCallback(async () => {
    if (isLoadingTests || !hasMoreTests) return;
    
    setIsLoadingTests(true);
    
    // 실제 구현에서는 API 호출
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const sortedTests = [...testResults].sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
    const nextPage = testPage + 1;
    const startIndex = nextPage * ITEMS_PER_PAGE;
    const endIndex = startIndex + ITEMS_PER_PAGE;
    const newTests = sortedTests.slice(startIndex, endIndex);
    
    setDisplayedTests(prev => [...prev, ...newTests]);
    setTestPage(nextPage);
    setHasMoreTests(endIndex < sortedTests.length);
    setIsLoadingTests(false);
  }, [testResults, testPage, isLoadingTests, hasMoreTests]);

  // Intersection Observer 설정
  useEffect(() => {
    const chatObserver = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasMoreChats && !isLoadingChats) {
          loadMoreChats();
        }
      },
      { threshold: 0.1 }
    );

    const testObserver = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasMoreTests && !isLoadingTests) {
          loadMoreTests();
        }
      },
      { threshold: 0.1 }
    );

    if (chatObserverRef.current) {
      chatObserver.observe(chatObserverRef.current);
    }
    if (testObserverRef.current) {
      testObserver.observe(testObserverRef.current);
    }

    return () => {
      chatObserver.disconnect();
      testObserver.disconnect();
    };
  }, [hasMoreChats, hasMoreTests, isLoadingChats, isLoadingTests, loadMoreChats, loadMoreTests]);

  const handleNewChat = () => {
    onNewChat();
    navigate('/main');
  };

  const handleContinueChat = (chat: ChatHistory) => {
    console.log('🔄 이어서 대화하기:', chat.characterName);
    
    if (onContinueChat) {
      onContinueChat(chat.id, chat.characterName);
    }
    // 채팅 세션 ID를 URL 파라미터로 전달하여 채팅 페이지로 이동
    navigate(`/chat?sessionId=${chat.id}`);
  };

  const handleProfileEdit = () => {
    setIsEditingProfile(true);
    setEditingName(userProfile?.name || '');
    setNicknameCheckResult(null);
    setIsNicknameChecked(false);
    setNameError(null);
  };

  const validateNickname = (name: string): string | null => {
    if (name.length < 2) return '닉네임은 2자 이상이어야 합니다.';
    if (name.length > 20) return '닉네임은 20자 이하여야 합니다.';
    if (!/^[가-힣a-zA-Z0-9_]+$/.test(name)) return '닉네임은 한글, 영문, 숫자, 밑줄만 사용할 수 있습니다.';
    return null;
  };

  // 디바운스된 닉네임 검사
  const debouncedNicknameCheck = useCallback(async (nickname: string) => {
    if (!currentUserId) return;
    
    const error = validateNickname(nickname);
    if (error) {
      setNameError(error);
      setNicknameCheckResult(null);
      setIsNicknameChecked(false);
      return;
    }

    if (nickname === userProfile?.name) {
      setNicknameCheckResult('available');
      setIsNicknameChecked(true);
      setNameError(null);
      return;
    }

    setIsCheckingNickname(true);
    setNameError(null);
    
    try {
      const result = await userService.checkNickname(currentUserId, nickname);
      setNicknameCheckResult(result.available ? 'available' : 'taken');
      setIsNicknameChecked(true);
    } catch (error) {
      console.error('닉네임 확인 실패:', error);
      setNicknameCheckResult('error');
      setIsNicknameChecked(false);
    } finally {
      setIsCheckingNickname(false);
    }
  }, [currentUserId, userProfile?.name]);

  const handleNicknameCheck = useCallback(() => {
    debouncedNicknameCheck(editingName);
  }, [debouncedNicknameCheck, editingName]);

  const handleNameChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const newName = e.target.value;
    setEditingName(newName);
    setNicknameCheckResult(null);
    setIsNicknameChecked(false);
    setNameError(null);
    
    // 디바운스된 자동 닉네임 검사 (800ms 후)
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }
    
    debounceTimerRef.current = setTimeout(() => {
      if (newName.trim() && newName !== userProfile?.name) {
        debouncedNicknameCheck(newName);
      }
    }, 800);
  }, [debouncedNicknameCheck, userProfile?.name]);

  const handleProfileSave = useCallback(async () => {
    if (!currentUserId) return;
    
    // 닉네임이 기존과 동일하지 않은 경우에만 중복검사 확인
    if (editingName !== userProfile?.name && (!isNicknameChecked || nicknameCheckResult !== 'available')) {
      setNameError('닉네임 중복 검사를 완료해주세요.');
      return;
    }

    setIsSaving(true);
    setSaveError(null);
    setSaveSuccess(false);

    // Optimistic Update: UI를 먼저 업데이트
    const originalProfile = userProfile;
    if (userProfile) {
      const optimisticProfile: UserProfile = {
        ...userProfile,
        name: editingName,
      };
      setUserProfile(optimisticProfile);
      if (onUpdateProfile) {
        onUpdateProfile(optimisticProfile);
      }
    }

    try {
      // 백엔드 업데이트
      await userService.updateUser(currentUserId, { nickname: editingName });
      
      setSaveSuccess(true);
      // 성공 딜레이 단축: 1.5초 → 0.8초
      setTimeout(() => {
        setIsEditingProfile(false);
        setSaveSuccess(false);
      }, 800);
    } catch (error) {
      console.error('프로필 저장 실패:', error);
      setSaveError('프로필 저장 중 오류가 발생했습니다. 다시 시도해주세요.');
      
      // 실패 시 원래 상태로 롤백
      if (originalProfile) {
        setUserProfile(originalProfile);
        if (onUpdateProfile) {
          onUpdateProfile(originalProfile);
        }
      }
    } finally {
      setIsSaving(false);
    }
  }, [currentUserId, editingName, userProfile, isNicknameChecked, nicknameCheckResult, onUpdateProfile]);

  const handleProfileCancel = () => {
    setIsEditingProfile(false);
    setEditingName(userProfile?.name || '');
    setProfileImage(null);
    setNicknameCheckResult(null);
    setIsNicknameChecked(false);
    setNameError(null);
    setImageError(null);
    setSaveError(null);
    setSaveSuccess(false);
  };

  const validateImageFile = (file: File): string | null => {
    // 파일 크기 제한 (5MB)
    const maxSize = 5 * 1024 * 1024;
    if (file.size > maxSize) {
      return '이미지 파일은 5MB 이하여야 합니다.';
    }

    // 파일 형식 검증
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png'];
    if (!allowedTypes.includes(file.type)) {
      return 'JPG, PNG 형식의 이미지 파일만 업로드 가능합니다.';
    }

    return null;
  };

  const handleImageUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file || !currentUserId) return;

    const error = validateImageFile(file);
    if (error) {
      setImageError(error);
      event.target.value = ''; // 입력 필드 초기화
      return;
    }

    setImageError(null);
    setIsUploadingImage(true);

    try {
      // 미리보기 설정
      const reader = new FileReader();
      reader.onload = (e) => {
        setProfileImage(e.target?.result as string);
      };
      reader.readAsDataURL(file);

      // 서버에 업로드
      const response = await userService.uploadProfileImage(currentUserId, file);
      
      // 프로필 새로고침
      await loadUserData();
      
      console.log('이미지 업로드 성공:', response.message);
    } catch (error) {
      console.error('이미지 업로드 실패:', error);
      setImageError('이미지 업로드 중 오류가 발생했습니다. 다시 시도해주세요.');
      setProfileImage(null);
    } finally {
      setIsUploadingImage(false);
      event.target.value = ''; // 입력 필드 초기화
    }
  };

  const handleDeleteAccountClick = () => {
    setShowDeleteAccountModal(true);
  };

  const handleDeleteAccountClose = () => {
    setShowDeleteAccountModal(false);
  };

  const handleDeleteAccountConfirm = async () => {
    try {
      if (userProfile?.id) {
        const userId = parseInt(userProfile.id);
        console.log('탈퇴 시도 - userProfile:', userProfile);
        console.log('탈퇴 시도 - userId:', userId);
        
        // 회원 탈퇴 API 호출
        await userService.deleteAccount(userId);
        
        // 성공시 로컬 스토리지에서 토큰 제거
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        
        // 모달 닫기
        setShowDeleteAccountModal(false);
        
        // 랜딩페이지로 이동
        navigate('/', { replace: true });
      } else {
        console.error('사용자 프로필 또는 ID가 없습니다:', userProfile);
        alert('사용자 정보를 찾을 수 없습니다.');
      }
    } catch (error) {
      console.error('회원 탈퇴 중 오류가 발생했습니다:', error);
      // 에러 발생시 모달은 그대로 두고 에러 표시
      alert('회원 탈퇴 중 오류가 발생했습니다. 다시 시도해주세요.');
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('ko-KR', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const groupByDate = (items: any[]) => {
  return items.reduce((groups: { [key: string]: any[] }, item) => {
    // 날짜만 추출 (YYYY-MM-DD)
    const dateKey = new Date(item.date).toISOString().split('T')[0];
    if (!groups[dateKey]) {
      groups[dateKey] = [];
    }
    groups[dateKey].push(item);
    return groups;
  }, {});
};


  const chatsByDate = groupByDate(displayedChats);
  const testsByDate = groupByDate(displayedTests);

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0F103F] via-[#1a1b4a] via-[#2a2b5a] to-[#3a3b6a] relative overflow-hidden">
      <Navigation onNavigate={onNavigate} activeTab="mypage" />
      
    {/* Minimal particles background */}
      <div
        className="absolute inset-0 opacity-25"
        style={{
          backgroundImage: `url('/images/minimal-particles.png')`,
          backgroundSize: "cover",
          backgroundPosition: "center",
          backgroundRepeat: "no-repeat",
        }}
      ></div>

      {/* Cosmic spheres */}
      <div
        className="absolute top-1/3 left-1/4 w-80 h-52 opacity-20"
        style={{
          backgroundImage: `url('/images/cosmic-spheres.png')`,
          backgroundSize: "contain",
          backgroundPosition: "center",
          backgroundRepeat: "no-repeat",
          animationDuration: "2s",
        }}
      ></div>

      {/* Enhanced decorative elements */}
      <div className="absolute bottom-20 right-20 w-48 h-48 bg-gradient-to-br from-cyan-400 via-purple-500 to-pink-500 rounded-full opacity-20 blur-2xl animate-pulse"></div>
      <div
        className="absolute top-20 left-20 w-32 h-32 bg-gradient-to-br from-purple-400 via-indigo-500 to-blue-500 rounded-full opacity-30 blur-xl animate-pulse"
      ></div>

      <div className="relative z-10 container mx-auto px-8 py-24 flex-col">
        <h1 className="text-3xl md:text-4xl font-bold text-white text-center mb-12 drop-shadow-2xl">마이페이지</h1>

        {/* User Profile Card */}
        <div className="max-w-5xl mx-auto mb-8">
          <div className="bg-slate-700/50 backdrop-blur-sm border border-white/20 shadow-xl rounded-3xl p-6">
            <div className="flex items-center space-x-4">
              <div className="relative">
              <div className="w-16 h-16 bg-gradient-to-br from-purple-400/30 via-pink-400/20 to-cyan-400/30 rounded-full flex items-center justify-center border-2 border-white/30 overflow-hidden">
                  {profileImage || userProfile?.profileImageUrl ? (
                    <img 
                      src={profileImage || userProfile?.profileImageUrl || ''} 
                      alt="Profile" 
                      className="w-full h-full object-cover"  
                      style={{ 
                        objectFit: 'cover',
                        aspectRatio: '1 / 1'
                      }}
                    />
                  ) : (
                    <User className="w-8 h-8 text-white" />
                  )}
                </div>
                {isEditingProfile && (
                  <label className="absolute -bottom-2 -right-2 bg-white rounded-full p-2 shadow-lg cursor-pointer hover:bg-gray-50 transition-colors">
                    {isUploadingImage ? (
                      <Loader className="w-4 h-4 text-gray-600 animate-spin" />
                    ) : (
                      <Camera className="w-4 h-4 text-gray-600" />
                    )}
                    <input
                      type="file"
                      accept="image/jpeg,image/jpg,image/png,image/gif"
                      onChange={handleImageUpload}
                      disabled={isUploadingImage}
                      className="hidden"
                    />
                  </label>
                )}
              </div>

              <div className="flex-1">
                {isEditingProfile ? (
                  <div className="space-y-3">
                    {/* 닉네임 입력 */}
                    <div>
                      <label className="block text-sm font-medium text-white mb-1">닉네임</label>
                      <div className="flex space-x-2">
                        <input
                          type="text"
                          value={editingName}
                          onChange={handleNameChange}
                          className={`flex-1 px-3 py-2 border rounded-md bg-white/90 text-gray-800 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
                            nameError ? 'border-red-300' : 'border-gray-300'
                          }`}
                          placeholder="닉네임을 입력하세요"
                        />
                      </div>

                      {/* 닉네임 검사 결과 */}
                      {nicknameCheckResult && (
                        <div className={`mt-2 flex items-center space-x-1 text-sm ${
                          nicknameCheckResult === 'available' ? 'text-green-400' : 'text-red-400'
                        }`}>
                          {nicknameCheckResult === 'available' ? (
                            <>
                              <Check className="w-4 h-4" />
                              <span>사용 가능한 닉네임입니다.</span>
                            </>
                          ) : nicknameCheckResult === 'taken' ? (
                            <>
                              <X className="w-4 h-4" />
                              <span>이미 사용 중인 닉네임입니다.</span>
                            </>
                          ) : (
                            <>
                              <X className="w-4 h-4" />
                              <span>중복 확인 중 오류가 발생했습니다.</span>
                            </>
                          )}
                        </div>
                      )}

                      {/* 에러 메시지 */}
                      {nameError && (
                        <div className="mt-2 flex items-center space-x-1 text-sm text-red-400">
                          <X className="w-4 h-4" />
                          <span>{nameError}</span>
                        </div>
                      )}
                    </div>

                    {/* 이미지 업로드 에러 */}
                    {imageError && (
                      <div className="flex items-center space-x-1 text-sm text-red-400">
                        <X className="w-4 h-4" />
                        <span>{imageError}</span>
                      </div>
                    )}

                    {/* 저장 성공/실패 메시지 */}
                    {saveError && (
                      <div className="flex items-center space-x-1 text-sm text-red-400">
                        <X className="w-4 h-4" />
                        <span>{saveError}</span>
                      </div>
                    )}
                    {saveSuccess && (
                      <div className="flex items-center space-x-1 text-sm text-green-400">
                        <Check className="w-4 h-4" />
                        <span>프로필이 성공적으로 저장되었습니다.</span>
                      </div>
                    )}

                    {/* 저장/취소 버튼 */}
                    <div className="flex space-x-2">
                      <button
                        onClick={handleProfileSave}
                        disabled={
                          (editingName !== userProfile?.name && (!isNicknameChecked || nicknameCheckResult !== 'available')) || 
                          isSaving
                        }
                        className={`px-4 py-2 rounded-md text-sm transition-colors ${
                          (editingName !== userProfile?.name && (!isNicknameChecked || nicknameCheckResult !== 'available')) || 
                          isSaving
                            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                            : 'bg-indigo-600 text-white hover:bg-indigo-700'
                        }`}
                      >
                        {isSaving ? '저장 중...' : '저장'}
                      </button>
                      <button
                        onClick={handleProfileCancel}
                        disabled={isSaving}
                        className={`px-4 py-2 rounded-md text-sm transition-colors ${
                          isSaving
                            ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                            : 'bg-gray-300 text-gray-700 hover:bg-gray-400'
                        }`}
                      >
                        취소
                      </button>
                    </div>
                  </div>
                ) : (
                  <div>
                    {isLoadingProfile ? (
                      <div className="flex items-center space-x-2">
                        <Loader className="w-5 h-5 animate-spin text-white" />
                        <span className="text-white/70">프로필 로딩 중...</span>
                      </div>
                    ) : (
                      <div>
                        <div className="flex items-center space-x-2">
                          <h2 className="text-2xl font-bold text-white mb-1 drop-shadow-lg">{userProfile?.name || '사용자'}</h2>
                          <button
                            onClick={handleProfileEdit}
                            className="p-1 text-white/60 hover:text-white transition-colors"
                            title="프로필 편집"
                          >
                            <Edit2 className="w-4 h-4" />
                          </button>
                        </div>
                        <p className="text-white/70">{userProfile?.email}</p>
                        <div className="flex items-center space-x-6 mt-2 text-sm text-white/50">
                          <span className="flex items-center space-x-1">
                            <Calendar className="w-4 h-4" />
                            <span>가입일: {userProfile?.joinDate && formatDate(userProfile.joinDate)}</span>
                          </span>
                          <span>총 검사: {userProfile?.totalTests}회</span>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

{/* Chat History와 Test Results - 2분할 배치 */}
<div className="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-8">
  {/* Chat History */}
  <div className="bg-slate-700/50 backdrop-blur-sm rounded-3xl border border-white/20 shadow-2xl p-6">
    <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
      <MessageCircle className="w-5 h-5 text-white" />
      <span>채팅 히스토리</span>
    </h3>
    <div className="space-y-4 max-h-[500px] overflow-y-auto">
      {displayedChats.length === 0 ? (
        <div className="text-center py-8 text-white/50">
          <MessageCircle className="w-12 h-12 mx-auto mb-3 text-white/20" />
          <p>아직 채팅 기록이 없습니다.</p>
        </div>
      ) : (
        <>
          {Object.entries(chatsByDate)
            .sort(([a], [b]) => new Date(b).getTime() - new Date(a).getTime())
            .map(([date, chats]) => (
              <div key={date} className="space-y-2">
                <h4 className="text-sm font-medium text-white/60">{formatDate(date)}</h4>
                {chats.map((chat: ChatHistory) => (
                  <div
                    key={chat.id}
                    className="bg-slate-600/50 rounded-2xl p-4 border border-white/10 hover:bg-slate-600/60 transition-all duration-300"
                  >
                    <div className="flex items-center justify-between">
                      {/* 텍스트 왼쪽 정렬 */}
                      <div className="flex items-center space-x-3">
                        <div className="w-12 h-12 bg-gradient-to-br from-gray-600 to-gray-800 rounded-full flex items-center justify-center shadow-lg overflow-hidden">
                          <img 
                            src={chat.characterAvatar} 
                            alt={chat.characterName}
                            className="w-32 h-32 object-contain"
                          />
                        </div>
                        <div>
                          <p className="font-medium text-white text-left">{chat.characterName}</p>
                          <p className="text-sm text-white/60 text-left">
                            {chat.messages?.length || 0}개 메시지 ·{" "}
                            {chat.messages?.[chat.messages.length - 1]?.timestamp
                              ? formatTime(chat.messages[chat.messages.length - 1].timestamp)
                              : "시간 정보 없음"}
                          </p>
                        </div>
                      </div>
                      {/* 버튼 오른쪽 정렬 */}
                      <button
                        className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 hover:from-purple-500/30 hover:to-pink-500/30 text-white px-4 py-2 rounded-full text-sm border border-white/10"
                        onClick={() => handleContinueChat(chat)}
                      >
                        이어서 대화하기
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ))}
          {isLoadingChats && (
            <div className="flex justify-center py-4">
              <Loader className="w-6 h-6 animate-spin text-white" />
            </div>
          )}
          {hasMoreChats && <div ref={chatObserverRef} className="h-4" />}
          {!hasMoreChats && displayedChats.length > 0 && (
            <div className="text-white/50 text-center text-sm mt-4">
              모든 채팅 기록을 불러왔습니다.
            </div>
          )}
        </>
      )}
    </div>
  </div>

  {/* Test Results */}
<div className="bg-slate-700/50 backdrop-blur-sm rounded-3xl border border-white/20 shadow-2xl p-6">
  <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
    <FileText className="w-5 h-5 text-white" />
    <span>그림 검사 결과</span>
  </h3>
  <div className="space-y-4 max-h-[500px] overflow-y-auto">
    {displayedTests.length === 0 ? (
      <div className="text-center py-8 text-white/50">
        <FileText className="w-12 h-12 mx-auto mb-3 text-white/20" />
        <p>아직 검사 결과가 없습니다.</p>
      </div>
    ) : (
      <>
        {Object.entries(testsByDate)
          .sort(([a], [b]) => new Date(b).getTime() - new Date(a).getTime())
          .map(([date, tests]) => (
            <div key={date} className="space-y-2">
              <h4 className="text-sm font-medium text-white/60">{formatDate(date)}</h4>
                {tests.map((test: TestResult) => (
                  <div
                    key={test.id}
                    className="bg-slate-600/50 rounded-2xl p-4 border border-white/10 hover:bg-slate-600/60 transition-all duration-300"
                  >
                    <div className="flex items-center justify-between">
                      {/* 왼쪽: 페르소나와 정보 */}
                      <div className="flex items-center space-x-3">
                        {test.images?.[0] && (
                          <img
                            src={testService.getImageUrl(test.images[0])}
                            alt="Test Result"
                            className="w-12 h-12 rounded-lg border border-white/10"
                          />
                        )}
                        <div>
                          <p className="text-white font-bold text-left">페르소나: {test.characterMatch}</p>
                          <p className="text-sm text-white/60 text-left">
                            검사 완료: {formatTime(test.date)}
                          </p>
                        </div>
                      </div>
                      {/* 오른쪽 버튼 */}
                      <button
                        className="bg-gradient-to-r from-cyan-500/20 to-blue-500/20 hover:from-cyan-500/30 hover:to-blue-500/30 text-white px-4 py-2 rounded-full text-sm border border-white/10"
                        onClick={() => navigate(`/result-detail/${test.id}`)}
                      >
                        자세히 보기
                      </button>
                    </div>
                  </div>
                ))}
              </div>
          ))}
        {isLoadingTests && (
          <div className="flex justify-center py-4">
            <Loader className="w-6 h-6 animate-spin text-white" />
          </div>
        )}
        {hasMoreTests && <div ref={testObserverRef} className="h-4" />}
        {!hasMoreTests && displayedTests.length > 0 && (
          <div className="text-white/50 text-center text-sm mt-4">
            모든 검사 결과를 불러왔습니다.
          </div>
        )}
      </>
    )}
  </div>
</div>
</div>



  {/* 회원탈퇴 섹션 */}
  <div className="max-w-5xl mx-auto mt-8">
      <div className="flex justify-start">
        <Button
          onClick={handleDeleteAccountClick}
          className="bg-gradient-to-r from-slate-600/50 to-slate-700/50 hover:from-slate-600/70 hover:to-slate-700/70 text-white px-6 py-3 rounded-full font-medium border border-white/10"
        >
          회원탈퇴
        </Button>
      </div>
    </div>

    {/* DeleteAccountModal */}
    <DeleteAccountModal
      isOpen={showDeleteAccountModal}
      onClose={handleDeleteAccountClose}
      onConfirm={handleDeleteAccountConfirm}
    />
  </div>
  </div>
  );
};

export default MyPage;