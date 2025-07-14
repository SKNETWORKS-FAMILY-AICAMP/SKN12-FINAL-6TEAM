import React, { useState, useRef, useEffect } from 'react';

interface ChatBotMessage {
  id: string;
  type: 'user' | 'bot';
  content: string;
  timestamp: string;
}

interface GeneralChatBotProps {
  isOpen: boolean;
  onClose: () => void;
}

const GeneralChatBot: React.FC<GeneralChatBotProps> = ({ isOpen, onClose }) => {
  const [messages, setMessages] = useState<ChatBotMessage[]>([
    {
      id: '1',
      type: 'bot',
      content: '안녕하세요! 무엇을 도와드릴까요? 궁금한 것이 있으시면 언제든 물어보세요.',
      timestamp: new Date().toLocaleTimeString()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (inputMessage.trim() === '') return;

    const userMessage: ChatBotMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsTyping(true);

    // 봇 응답 시뮬레이션
    setTimeout(() => {
      const botResponse = generateBotResponse(inputMessage);
      const botMessage: ChatBotMessage = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: botResponse,
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, botMessage]);
      setIsTyping(false);
    }, 1000 + Math.random() * 2000);
  };

  const generateBotResponse = (userInput: string): string => {
    const lowerInput = userInput.toLowerCase();
    
    if (lowerInput.includes('안녕') || lowerInput.includes('hello')) {
      return '안녕하세요! 좋은 하루 보내고 계신가요?';
    }
    
    if (lowerInput.includes('도움') || lowerInput.includes('help')) {
      return '무엇을 도와드릴까요? 저는 다음과 같은 것들을 도와드릴 수 있어요:\n• 일반적인 질문 답변\n• 감정적 지원\n• 정보 제공\n• 대화 상대';
    }
    
    if (lowerInput.includes('기분') || lowerInput.includes('감정')) {
      return '지금 기분이 어떠신가요? 힘든 일이 있으시면 언제든 말씀해 주세요. 제가 들어드릴게요.';
    }
    
    if (lowerInput.includes('고마워') || lowerInput.includes('감사')) {
      return '천만에요! 도움이 되어서 기뻐요. 또 다른 궁금한 것이 있으시면 언제든 물어보세요.';
    }
    
    if (lowerInput.includes('이름')) {
      return '저는 일반 도우미 챗봇이에요. 여러분의 궁금증을 해결하고 대화 상대가 되어드리는 것이 제 역할입니다!';
    }
    
    if (lowerInput.includes('시간') || lowerInput.includes('날짜')) {
      const now = new Date();
      return `현재 시간은 ${now.toLocaleString('ko-KR')}입니다.`;
    }
    
    // 기본 응답들
    const defaultResponses = [
      '흥미로운 말씀이네요! 더 자세히 말씀해 주실 수 있나요?',
      '그런 생각을 해보신 적이 있군요. 어떤 계기로 그렇게 생각하게 되셨나요?',
      '좋은 질문이에요! 제가 이해한 것이 맞는지 확인해볼게요.',
      '말씀해 주신 내용을 들어보니, 정말 중요한 문제인 것 같아요.',
      '네, 잘 이해했어요. 이런 상황에서는 여러 가지 방법이 있을 수 있겠네요.',
      '정말 좋은 관점이네요! 다른 방향에서도 생각해볼 수 있을까요?'
    ];
    
    return defaultResponses[Math.floor(Math.random() * defaultResponses.length)];
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-5" onClick={onClose}>
      <div className="bg-white rounded-3xl w-full max-w-md h-[600px] max-h-[80vh] flex flex-col shadow-2xl chatbot-slide-up" onClick={(e) => e.stopPropagation()}>
        <div className="flex justify-between items-center p-5 border-b border-gray-200 rounded-t-3xl bg-gradient-to-r from-indigo-500 to-purple-600 text-white">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white bg-opacity-20 rounded-full flex items-center justify-center text-xl">🤖</div>
            <div>
              <h3 className="font-semibold text-base">일반 도우미 챗봇</h3>
              <p className="text-xs opacity-80">온라인</p>
            </div>
          </div>
          <button 
            className="w-8 h-8 rounded-full flex items-center justify-center hover:bg-white hover:bg-opacity-20 transition-colors duration-300 text-2xl"
            onClick={onClose}
          >
            ×
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-5 flex flex-col gap-4 bg-gray-50 chat-messages">
          {messages.map((message) => (
            <div key={message.id} className={`flex flex-col max-w-[80%] ${message.type === 'user' ? 'self-end' : 'self-start'}`}>
              <div className={`p-3 rounded-2xl text-sm leading-relaxed break-words ${
                message.type === 'user' 
                  ? 'bg-blue-500 text-white rounded-br-sm' 
                  : 'bg-white text-gray-800 border border-gray-200 rounded-bl-sm shadow-sm'
              }`}>
                {message.content.split('\n').map((line, index) => (
                  <React.Fragment key={index}>
                    {line}
                    {index < message.content.split('\n').length - 1 && <br />}
                  </React.Fragment>
                ))}
              </div>
              <div className={`text-xs text-gray-500 mt-1 ${message.type === 'user' ? 'text-right' : 'text-left'}`}>
                {message.timestamp}
              </div>
            </div>
          ))}
          
          {isTyping && (
            <div className="flex flex-col max-w-[80%] self-start">
              <div className="bg-white text-gray-800 border border-gray-200 rounded-2xl rounded-bl-sm shadow-sm p-3 text-sm">
                <div className="flex items-center gap-2 italic text-gray-600">
                  <div className="typing-dots flex gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
                  </div>
                  챗봇이 입력 중...
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="p-5 border-t border-gray-200 bg-white">
          <div className="flex gap-3 items-end">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="메시지를 입력하세요... (Shift+Enter로 줄바꿈)"
              rows={1}
              className="flex-1 border-2 border-gray-200 focus:border-blue-500 rounded-3xl py-3 px-4 text-sm resize-none outline-none transition-colors duration-300 max-h-24 min-h-[40px]"
            />
            <button 
              onClick={handleSendMessage}
              disabled={inputMessage.trim() === '' || isTyping}
              className="bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed text-white rounded-3xl py-3 px-5 text-sm font-semibold cursor-pointer transition-all duration-300 whitespace-nowrap"
            >
              전송
            </button>
          </div>
        </div>

        <div className="p-4 bg-gray-50 text-center rounded-b-3xl border-t border-gray-200">
          <p className="text-xs text-gray-600 italic">💡 팁: 도움말, 기분, 시간 등에 대해 물어보세요!</p>
        </div>
      </div>
    </div>
  );
};

export default GeneralChatBot;