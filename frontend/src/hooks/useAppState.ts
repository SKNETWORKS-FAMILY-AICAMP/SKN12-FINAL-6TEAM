import { useState, useCallback } from 'react';
import { ScreenType, SearchResult, ChatMessage, ChatHistory, TestResult, UserProfile } from '../types';
import { mockChatHistory, mockTestResults, mockUserProfile } from '../data/mockData';

export const useAppState = () => {
  const [currentScreen, setCurrentScreen] = useState<ScreenType>('landing');
  const [selectedCharacter, setSelectedCharacter] = useState<SearchResult | null>(null);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatHistory, setChatHistory] = useState<ChatHistory[]>(mockChatHistory);
  const [testResults, setTestResults] = useState<TestResult[]>(mockTestResults);
  const [userProfile, setUserProfile] = useState<UserProfile | null>(mockUserProfile);
  const [showModal, setShowModal] = useState(false);
  const [showRatingModal, setShowRatingModal] = useState(false);
  const [currentTestResult, setCurrentTestResult] = useState<string>('슬픔이'); // 현재 검사 결과
  const [isSending, setIsSending] = useState(false); // 메시지 전송 상태

  const handleGoogleLogin = useCallback(() => {
    setCurrentScreen('main');
  }, []);

  const handleStartDreamSearch = useCallback(() => {
    setCurrentScreen('results');
  }, []);

  const handleCharacterSelect = useCallback((character: SearchResult) => {
    setSelectedCharacter(character);
    setShowModal(true);
  }, []);

  const handleStartChat = useCallback(() => {
    setShowModal(false);
    setCurrentScreen('chat');
  }, []);

  // 캐릭터별 응답 메시지 생성 함수
  const generateBotResponse = useCallback((_userMessage: string) => {
    const characterName = selectedCharacter?.name || '슬픔이';
    
    const responses: { [key: string]: string[] } = {
      '기쁨이': [
        "와! 정말 좋은 이야기네요! 더 들어보고 싶어요!",
        "그런 일이 있었군요! 기분이 어떠셨나요?",
        "정말 흥미로워요! 그래서 어떻게 되었나요?",
        "오~ 그런 경험을 하셨군요! 저도 함께 기뻐해요!",
        "멋진 일이네요! 그때 기분을 더 자세히 말해주세요!",
        "우와! 듣기만 해도 기분이 좋아져요!",
        "정말 좋은 경험이었겠어요! 다른 이야기도 있나요?"
      ],
      '버럭이': [
        "진짜 화나는 일이었겠네! 나도 같이 화나!",
        "그런 건 당연히 짜증날 만해! 더 말해봐!",
        "아, 정말 답답했겠다! 그래서 어떻게 했어?",
        "말도 안 되는 일이네! 정말 화가 치밀어 올라!",
        "그런 상황이면 누구라도 화날 거야! 속 터져!",
        "정말 이해 안 가는 상황이다! 더 털어놔!",
        "그런 일로 스트레스받지 마! 다 말해봐!"
      ],
      '슬픔이': [
        "정말 힘들었겠어요... 괜찮으시나요?",
        "그런 일이 있었군요... 많이 슬프셨을 것 같아요",
        "마음이 아프네요... 혼자 견디기 힘들었죠?",
        "이해해요... 그럴 때는 정말 외롭죠",
        "정말 안타까워요... 지금은 어떤 기분이세요?",
        "힘든 시간을 보내셨군요... 함께 이야기해요",
        "그런 마음 충분히 이해해요... 더 말해주세요"
      ],
      '무서미': [
        "걱정이 많으시겠어요... 불안하셨죠?",
        "그런 상황이면 무섭기도 하고 걱정되기도 했을 거예요",
        "혼자 감당하기 어려웠을 것 같아요... 괜찮으세요?",
        "두려운 마음 충분히 이해해요... 어떤 기분이었나요?",
        "그럴 때는 정말 불안하죠... 지금은 어떠세요?",
        "마음이 편하지 않으셨을 거예요... 함께 이야기해요",
        "걱정이 클 때는 정말 힘들죠... 더 말해주세요"
      ],
      '까칠이': [
        "그래서 결론이 뭐야? 정확히 말해봐",
        "솔직히 말하면, 그건 당연한 결과 아니야?",
        "뭘 기대했던 거야? 현실적으로 생각해봐",
        "그런 식으로 하면 당연히 그렇게 되지",
        "정신 차리고 제대로 접근해야지",
        "감정적으로 생각하지 말고 논리적으로 판단해",
        "그래서 이제 어떻게 할 계획이야?"
      ]
    };

    const characterResponses = responses[characterName] || responses['슬픔이'];
    return characterResponses[Math.floor(Math.random() * characterResponses.length)];
  }, [selectedCharacter]);

  const handleSendMessage = useCallback((message: string) => {
    if (!message.trim() || isSending) return;
    
    setIsSending(true);
    
    const newMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: message,
      timestamp: new Date().toLocaleTimeString()
    };

    setChatMessages(prev => [...prev, newMessage]);

    // 캐릭터별 AI 응답
    setTimeout(() => {
      const aiResponse: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: generateBotResponse(message),
        timestamp: new Date().toLocaleTimeString()
      };
      setChatMessages(prev => [...prev, aiResponse]);
      setIsSending(false);
    }, 1000);
  }, [isSending, generateBotResponse]);

  const handleCloseModal = useCallback(() => {
    setShowModal(false);
  }, []);

  const handleShowRating = useCallback(() => {
    setShowRatingModal(true);
  }, []);

  const handleCloseRatingModal = useCallback(() => {
    setShowRatingModal(false);
  }, []);

  const handleGoToMyPage = useCallback(() => {
    setCurrentScreen('mypage');
  }, []);

  const handleNewChat = useCallback(() => {
    setCurrentScreen('main');
  }, []);

  const handleDeleteAccount = useCallback(() => {
    if (window.confirm('정말로 회원 탈퇴를 하시겠습니까?')) {
      // 실제로는 서버에 탈퇴 요청을 보내야 함
      alert('회원 탈퇴가 완료되었습니다.');
      setCurrentScreen('landing');
      setUserProfile(null);
    }
  }, []);

  // 현재 검사 결과에 따라 이용 가능한 캐릭터 필터링
  const getAvailableCharacters = useCallback(() => {
    // 슬픔이 결과가 나온 경우 슬픔이만 대화 가능
    if (currentTestResult === '슬픔이') {
      return [{ id: '3', name: '슬픔이', description: '당신의 슬픔을 이해하고 함께 극복해나가는 방법을 찾아드립니다.', avatar: '😢' }];
    }
    // 다른 결과의 경우 모든 캐릭터 이용 가능
    return [
      { id: '1', name: '기쁨이', description: '긍정적 생각 전환, 스트레스 해소, 자존감 향상 등을 통해 당신의 마음속 행복을 찾아줄 거예요.', avatar: '😊' },
      { id: '2', name: '버럭이', description: '분노 조절과 감정 관리에 대한 조언을 제공합니다.', avatar: '😤' },
      { id: '3', name: '슬픔이', description: '당신의 슬픔을 이해하고 함께 극복해나가는 방법을 찾아드립니다.', avatar: '😢' },
      { id: '4', name: '두려움이', description: '불안과 두려움을 다스리는 방법을 알려드립니다.', avatar: '😱' }
    ];
  }, [currentTestResult]);

  const handleContinueChat = useCallback((chatId: string, characterName: string) => {
    // 해당 채팅 기록을 찾아서 메시지를 복원
    const targetChat = chatHistory.find(chat => chat.id === chatId);
    if (targetChat) {
      // 캐릭터 설정
      const character = getAvailableCharacters().find(char => char.name === characterName);
      if (character) {
        setSelectedCharacter(character);
      }
      // 메시지 기록 복원
      setChatMessages(targetChat.messages);
    }
  }, [chatHistory, getAvailableCharacters]);

  return {
    currentScreen,
    selectedCharacter,
    chatMessages,
    chatHistory,
    testResults,
    userProfile,
    showModal,
    showRatingModal,
    currentTestResult,
    isSending,
    getAvailableCharacters,
    handleGoogleLogin,
    handleStartDreamSearch,
    handleCharacterSelect,
    handleStartChat,
    handleSendMessage,
    handleCloseModal,
    handleShowRating,
    handleCloseRatingModal,
    handleGoToMyPage,
    handleNewChat,
    handleDeleteAccount,
    handleContinueChat
  };
};