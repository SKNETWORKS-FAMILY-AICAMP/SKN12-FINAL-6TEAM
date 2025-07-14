import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
// import Navigation from '../common/Navigation';
import Modal from '../common/Modal';
import StarRating from '../common/StarRating';
import { ChatMessage, SearchResult } from '../../types';

interface ChatPageProps {
  selectedCharacter: SearchResult | null;
  chatMessages: ChatMessage[];
  onSendMessage: (message: string) => void;
  showRatingModal: boolean;
  onShowRating: () => void;
  onCloseRatingModal: () => void;
  onNavigate?: (screen: string) => void;
  isSending?: boolean;
}

const ChatPage: React.FC<ChatPageProps> = ({
  selectedCharacter,
  chatMessages,
  onSendMessage,
  showRatingModal,
  onShowRating,
  onCloseRatingModal,
  onNavigate,
  isSending = false
}) => {
  const [inputMessage, setInputMessage] = useState('');
  const [currentRating, setCurrentRating] = useState(3);
  const [sidebarVisible, setSidebarVisible] = useState(false);
  const [isChatEnded, setIsChatEnded] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const sidebarMessagesEndRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  const handleSendMessage = () => {
    if (inputMessage.trim() === '' || isSending || isChatEnded) return;
    const messageToSend = inputMessage.trim();
    
    // 즉시 입력창 비우기
    setInputMessage('');
    
    // 강제로 입력창 비우기
    if (inputRef.current) {
      inputRef.current.value = '';
    }
    
    // 약간의 딜레이를 두고 다시 한 번 비우기
    setTimeout(() => {
      setInputMessage('');
      if (inputRef.current) {
        inputRef.current.value = '';
      }
    }, 0);
    
    onSendMessage(messageToSend);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleRatingChange = (rating: number) => {
    setCurrentRating(rating);
  };

  const toggleSidebar = () => {
    setSidebarVisible(!sidebarVisible);
  };

  const handleEndChat = () => {
    setIsChatEnded(true);
  };

  useEffect(() => {
    // 컴포넌트가 마운트되면 입력창에 포커스
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  useEffect(() => {
    // 메시지가 업데이트될 때마다 스크롤을 맨 아래로
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
    // 사이드바 채팅도 맨 아래로 스크롤
    if (sidebarMessagesEndRef.current) {
      sidebarMessagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [chatMessages]);

  useEffect(() => {
    // 전송 완료 후 입력창에 포커스
    if (!isSending && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isSending]);

  const getLastBotMessage = () => {
    const botMessages = chatMessages.filter(msg => msg.type !== 'user');
    return botMessages.length > 0 ? botMessages[botMessages.length - 1] : null;
  };

  // 초기 메시지를 한 번만 생성하고 저장
  const [initialMessage] = useState(() => {
    const characterMessages: { [key: string]: string[] } = {
      '기쁨이': [
        "안녕! 오늘 뭔가 좋은 일이 있을 것 같은데?",
        "하이~ 기분 좋은 하루 보내고 있어?",
        "웃어봐! 세상이 더 밝아 보일 거야!",
        "오늘은 특별한 날이야. 뭔가 신나는 일을 해볼까?"
      ],
      '버럭이': [
        "뭐가 그렇게 짜증나는 거야? 말해봐!",
        "화났어? 속시원하게 털어놔!",
        "답답한 게 있으면 다 말해! 내가 들어줄게!",
        "억울한 일이라도 있었나? 화내도 괜찮아!"
      ],
      '슬픔이': [
        "안녕... 무엇이 너를 가장 슬프게 하니...?",
        "힘든 하루였나? 천천히 말해줘...",
        "슬픈 일이 있었구나... 함께 이야기해보자",
        "괜찮아... 여기서는 마음껏 울어도 돼"
      ],
      '무서미': [
        "걱정되는 일이 있어? 천천히 말해봐",
        "무서운 게 있다면 함께 해결해보자",
        "불안하지? 괜찮아, 내가 옆에 있어",
        "두려운 마음, 충분히 이해해... 어떤 기분이야?"
      ],
      '까칠이': [
        "뭔 일이야? 솔직히 말해봐",
        "또 무슨 일로 고민이야? 현실적으로 생각해보자",
        "쓸데없는 걱정 말고, 정확히 뭐가 문제인지 말해",
        "그만 우울해하고, 뭐가 진짜 문제인지 파악해보자"
      ]
    };

    const characterName = selectedCharacter?.name || '슬픔이';
    const messages = characterMessages[characterName] || characterMessages['슬픔이'];
    return messages[Math.floor(Math.random() * messages.length)];
  });


  const lastBotMessage = getLastBotMessage();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex justify-center space-x-8">
            <button 
              onClick={() => onNavigate && onNavigate('main')}
              className="py-4 px-6 text-sm font-medium border-b-2 border-transparent text-gray-500 hover:text-gray-700"
            >
              메인
            </button>
            <button 
              onClick={() => onNavigate && onNavigate('test')}
              className="py-4 px-6 text-sm font-medium border-b-2 border-transparent text-gray-500 hover:text-gray-700"
            >
              그림검사
            </button>
            <button className="py-4 px-6 text-sm font-medium border-b-2 border-blue-500 text-blue-600">
              챗봇
            </button>
            <button 
              onClick={() => onNavigate && onNavigate('mypage')}
              className="py-4 px-6 text-sm font-medium border-b-2 border-transparent text-gray-500 hover:text-gray-700"
            >
              마이페이지
            </button>
            <button 
              onClick={() => onNavigate && onNavigate('logout')}
              className="py-4 px-6 text-sm font-medium border-b-2 border-transparent text-gray-500 hover:text-gray-700"
            >
              로그아웃
            </button>
          </div>
        </div>
      </nav>

      <div className="flex max-w-7xl mx-auto relative">
        {/* Toggle Button - Bookmark Style */}
        <button
          onClick={toggleSidebar}
          className={`fixed top-24 z-50 bg-blue-500 text-white shadow-lg hover:shadow-xl transition-all duration-300 hover:bg-blue-600 ${
            sidebarVisible ? 'right-80' : 'right-0'
          }`}
          style={{
            width: '60px',
            height: '80px',
            borderRadius: sidebarVisible ? '8px 0 0 8px' : '0 8px 8px 0',
            clipPath: sidebarVisible ? 'none' : 'polygon(15% 0, 100% 0, 100% 100%, 15% 100%, 0% 50%)'
          }}
        >
          <div className="flex flex-col items-center justify-center h-full">
            {sidebarVisible ? (
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            ) : (
              <>
                <svg className="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                <span className="text-xs font-medium">채팅</span>
              </>
            )}
          </div>
        </button>

        {/* Main Content */}
        <div className={`flex-1 p-8 transition-all duration-300 ${sidebarVisible ? 'mr-80' : ''}`}>
          <div className="max-w-2xl mx-auto">
            {/* Character */}
            <div className="flex justify-center mb-8">
              <div className="w-64 h-64 bg-white rounded-full flex items-center justify-center shadow-lg overflow-hidden">
                <img 
                  src="/assets/character.png" 
                  alt={selectedCharacter?.name || '슬픔이'}
                  className="w-full h-full object-cover"
                />
              </div>
            </div>

            {/* Last Bot Message Display */}
            {(lastBotMessage || chatMessages.length === 0) && (
              <div className="bg-gray-300 rounded-2xl p-6 mb-8 text-center">
                <p className="text-gray-800 text-lg font-medium">
                  {lastBotMessage?.content || initialMessage}
                </p>
              </div>
            )}

            {/* Input Area */}
            <div className="flex gap-3">
              <input
                ref={inputRef}
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder={isChatEnded ? '대화가 종료되었습니다' : `${selectedCharacter?.name || '슬픔이'}에게 공감한 질문 물어보세요`}
                className="flex-1 rounded-full border-gray-300 px-6 py-3 text-base border focus:outline-none focus:ring-2 focus:ring-blue-500"
                onKeyDown={handleKeyPress}
                autoFocus
                disabled={isSending || isChatEnded}
              />
              <button
                onClick={handleSendMessage}
                disabled={isSending || inputMessage.trim() === '' || isChatEnded}
                className="rounded-full px-8 py-3 bg-blue-500 hover:bg-blue-600 text-white disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isChatEnded ? '종료됨' : isSending ? '전송 중...' : '전송'}
              </button>
            </div>
          </div>
        </div>

        {/* Chat History Sidebar */}
        {sidebarVisible && (
          <div className="fixed right-0 top-0 h-full w-80 bg-white shadow-2xl z-40 transition-transform duration-300 transform translate-x-0 border-l border-gray-200">
            <div className="p-6 pt-20 h-full flex flex-col">
              {/* Header */}
              <div className="mb-6 pb-4 border-b border-gray-200">
                <h2 className="text-xl font-semibold text-gray-800 flex items-center">
                  <svg className="w-5 h-5 mr-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                  채팅 내역
                </h2>
                <p className="text-sm text-gray-500 mt-1">{selectedCharacter?.name || '슬픔이'}와의 대화</p>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto space-y-3 mb-6">
                {chatMessages.length === 0 ? (
                  <div className="text-center text-gray-400 py-8">
                    <svg className="w-12 h-12 mx-auto mb-3 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                    </svg>
                    <p className="text-sm">아직 대화가 없습니다</p>
                    <p className="text-xs text-gray-400 mt-1">메시지를 보내서 대화를 시작해보세요</p>
                  </div>
                ) : (
                  chatMessages.map((message) => (
                    <div key={message.id} className={`flex ${message.type === 'user' ? "justify-end" : "justify-start"}`}>
                      <div className={`max-w-[85%] ${message.type === 'user' ? 'order-2' : 'order-1'}`}>
                        <div
                          className={`rounded-2xl px-4 py-2 shadow-sm ${
                            message.type === 'user' 
                              ? "bg-blue-500 text-white" 
                              : "bg-gray-100 text-gray-800 border border-gray-200"
                          }`}
                        >
                          <p className="text-sm leading-relaxed">{message.content}</p>
                        </div>
                        <p className={`text-xs mt-1 px-2 ${
                          message.type === 'user' ? "text-right text-blue-200" : "text-left text-gray-400"
                        }`}>
                          {message.timestamp ? 
                            new Date(message.timestamp).toLocaleTimeString("ko-KR", {
                              hour: "2-digit",
                              minute: "2-digit",
                              hour12: false,
                            }) : 
                            new Date().toLocaleTimeString("ko-KR", {
                              hour: "2-digit",
                              minute: "2-digit",
                              hour12: false,
                            })
                          }
                        </p>
                      </div>
                    </div>
                  ))
                )}
                <div ref={sidebarMessagesEndRef} />
              </div>
              
              {/* Actions */}
              <div className="border-t border-gray-200 pt-4 space-y-3">
                <button 
                  onClick={onShowRating}
                  className="w-full bg-blue-50 hover:bg-blue-100 text-blue-700 py-3 px-4 rounded-xl transition-colors flex items-center justify-center font-medium"
                >
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                  </svg>
                  다른 캐릭터와 대화하기
                </button>
                <button 
                  onClick={handleEndChat}
                  className="w-full bg-red-50 hover:bg-red-100 text-red-600 py-2 px-4 rounded-lg transition-colors text-sm"
                  disabled={isChatEnded}
                >
                  {isChatEnded ? '대화가 종료됨' : '대화 종료'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      <Modal isOpen={showRatingModal} onClose={onCloseRatingModal} className="rating-modal">
        <h3>만족도 조사</h3>
        <div className="rating-section">
          <StarRating 
            initialRating={3}
            onRatingChange={handleRatingChange}
            centered={true}
          />
          <p className="rating-text">
            {currentRating > 0 && `${currentRating}점을 선택하셨습니다.`}
          </p>
        </div>
        <div className="rating-feedback">
          <h4>기타 의견(선택)</h4>
          <textarea placeholder="이 캐릭터는 제 취향 돋구었어요, 저에게 딱 맞는 해결책을 제시해줬어요 등 챗봇에 대한 의견을 자유롭게 적어주세요"></textarea>
          <button 
            className="submit-btn"
            onClick={() => navigate('/characters')}
          >
            다른 캐릭터랑도 대화해보기
          </button>
        </div>
      </Modal>
    </div>
  );
};

export default ChatPage;