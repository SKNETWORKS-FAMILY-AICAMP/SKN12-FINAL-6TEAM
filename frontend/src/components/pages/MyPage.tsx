import React from 'react';
import { useNavigate } from 'react-router-dom';
import Navigation from '../common/Navigation';
import { ChatHistory, TestResult, UserProfile } from '../../types';
import { MessageCircle, FileText, Trash2, User, Calendar, MessageSquare } from 'lucide-react';

interface MyPageProps {
  chatHistory: ChatHistory[];
  testResults: TestResult[];
  userProfile: UserProfile | null;
  onNewChat: () => void;
  onDeleteAccount: () => void;
  onNavigate?: (screen: string) => void;
  onContinueChat?: (chatId: string, characterName: string) => void;
}

const MyPage: React.FC<MyPageProps> = ({
  chatHistory,
  testResults,
  userProfile,
  onNewChat,
  onDeleteAccount,
  onNavigate,
  onContinueChat
}) => {
  const navigate = useNavigate();

  const handleNewChat = () => {
    onNewChat();
    navigate('/main');
  };

  const handleContinueChat = (chat: ChatHistory) => {
    if (onContinueChat) {
      onContinueChat(chat.id, chat.characterName);
    }
    navigate('/chat');
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
      const date = item.date;
      if (!groups[date]) {
        groups[date] = [];
      }
      groups[date].push(item);
      return groups;
    }, {});
  };

  const chatsByDate = groupByDate(chatHistory);
  const testsByDate = groupByDate(testResults);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      <Navigation onNavigate={onNavigate} />
      
      <main className="container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto space-y-8">
          <div className="text-center space-y-4">
            <h1 className="text-3xl font-bold text-gray-800">마이페이지</h1>
            <p className="text-gray-600">당신의 검사 기록과 대화 내역을 확인하세요</p>
          </div>

          {/* User Profile Card */}
          <div className="bg-white/70 backdrop-blur-sm border-0 shadow-xl rounded-xl p-6">
            <div className="flex items-center space-x-4">
              <div className="w-16 h-16 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center">
                <User className="w-8 h-8 text-white" />
              </div>
              <div className="flex-1">
                <h2 className="text-xl font-bold text-gray-800">{userProfile?.name || '사용자'}</h2>
                <p className="text-gray-600">{userProfile?.email}</p>
                <div className="flex items-center space-x-6 mt-2 text-sm text-gray-500">
                  <span className="flex items-center space-x-1">
                    <Calendar className="w-4 h-4" />
                    <span>가입일: {userProfile?.joinDate && formatDate(userProfile.joinDate)}</span>
                  </span>
                  <span>총 검사: {userProfile?.totalTests}회</span>
                  <span>총 채팅: {userProfile?.totalChats}회</span>
                </div>
              </div>
            </div>
          </div>

          <div className="grid lg:grid-cols-2 gap-8">
            {/* Chat History */}
            <div className="bg-white/70 backdrop-blur-sm border-0 shadow-xl rounded-xl">
              <div className="p-6 border-b border-gray-100">
                <h3 className="flex items-center space-x-2 text-xl font-bold text-gray-800">
                  <MessageCircle className="w-5 h-5" />
                  <span>채팅 히스토리</span>
                </h3>
              </div>
              <div className="p-6 space-y-4">
                {Object.entries(chatsByDate)
                  .sort(([a], [b]) => new Date(b).getTime() - new Date(a).getTime())
                  .map(([date, chats]) => (
                    <div key={date} className="space-y-2">
                      <h4 className="text-sm font-medium text-gray-500">{formatDate(date)}</h4>
                      {chats.map((chat: ChatHistory) => (
                        <div key={chat.id} className="flex items-center justify-between p-3 hover:bg-gray-50/50 rounded-lg transition-colors">
                          <div className="flex items-center space-x-3">
                            <div className="text-2xl">{chat.characterAvatar}</div>
                            <div>
                              <p className="font-medium text-gray-800">{chat.characterName}와의 대화</p>
                              <p className="text-sm text-gray-500">
                                {formatTime(chat.messages[chat.messages.length - 1].timestamp)} · 메시지 {chat.messages.length}개
                              </p>
                            </div>
                          </div>
                          <button 
                            className="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
                            onClick={() => handleContinueChat(chat)}
                          >
                            이어서 대화하기
                          </button>
                        </div>
                      ))}
                      {date !== Object.keys(chatsByDate).sort((a, b) => new Date(b).getTime() - new Date(a).getTime())[Object.keys(chatsByDate).length - 1] && (
                        <div className="border-t border-gray-100 my-2"></div>
                      )}
                    </div>
                  ))}
              </div>
            </div>

            {/* Test Results */}
            <div className="bg-white/70 backdrop-blur-sm border-0 shadow-xl rounded-xl">
              <div className="p-6 border-b border-gray-100">
                <h3 className="flex items-center space-x-2 text-xl font-bold text-gray-800">
                  <FileText className="w-5 h-5" />
                  <span>그림 검사 결과</span>
                </h3>
              </div>
              <div className="p-6 space-y-4">
                {Object.entries(testsByDate)
                  .sort(([a], [b]) => new Date(b).getTime() - new Date(a).getTime())
                  .map(([date, tests]) => (
                    <div key={date} className="space-y-2">
                      <h4 className="text-sm font-medium text-gray-500">{formatDate(date)}</h4>
                      {tests.map((test: TestResult) => (
                        <div key={test.id} className="flex items-center justify-between p-3 hover:bg-gray-50/50 rounded-lg transition-colors">
                          <div>
                            <p className="font-medium text-gray-800">{formatDate(test.date)} 결과</p>
                            <p className="text-sm text-indigo-600">페르소나: {test.characterMatch}</p>
                            {test.images && (
                              <p className="text-xs text-gray-400">첨부된 이미지: {test.images.length}개</p>
                            )}
                          </div>
                          <button 
                            className="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
                            onClick={() => navigate(`/result-detail/${test.id}`)}
                          >
                            자세히 보기
                          </button>
                        </div>
                      ))}
                      {date !== Object.keys(testsByDate).sort((a, b) => new Date(b).getTime() - new Date(a).getTime())[Object.keys(testsByDate).length - 1] && (
                        <div className="border-t border-gray-100 my-2"></div>
                      )}
                    </div>
                  ))}
              </div>
            </div>
          </div>


          {/* Account Management */}
          <div className="bg-white/70 backdrop-blur-sm border-0 shadow-xl rounded-xl">
            <div className="p-6 border-b border-gray-100">
              <h3 className="text-xl font-bold text-gray-800">계정 관리</h3>
            </div>
            <div className="p-6">
              <div className="flex justify-between items-center">
                <button 
                  className="bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white px-6 py-3 rounded-full shadow-lg hover:shadow-xl transition-all duration-300 flex items-center space-x-2"
                  onClick={handleNewChat}
                >
                  <MessageSquare className="w-4 h-4" />
                  <span>새로운 대화 시작</span>
                </button>
                <button 
                  className="flex items-center space-x-2 px-4 py-2 text-red-600 border border-red-200 rounded-lg hover:bg-red-50 transition-colors"
                  onClick={onDeleteAccount}
                >
                  <Trash2 className="w-4 h-4" />
                  <span>회원 탈퇴</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default MyPage;