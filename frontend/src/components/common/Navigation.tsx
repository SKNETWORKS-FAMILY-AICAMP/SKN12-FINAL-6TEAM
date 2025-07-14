import React from 'react';
import { Link, useLocation } from 'react-router-dom';

interface NavigationProps {
  activeTab?: string;
  onNavigate?: (screen: string) => void;
}

const Navigation: React.FC<NavigationProps> = ({ activeTab, onNavigate }) => {
  const location = useLocation();
  
  // URL 기반으로 활성 탭 결정
  const getActiveTab = () => {
    if (activeTab) return activeTab; // 명시적으로 전달된 activeTab이 있으면 사용
    
    switch (location.pathname) {
      case '/main':
        return 'main';
      case '/test':
        return 'test';
      case '/results':
        return 'results';
      case '/chat':
        return 'chat';
      case '/mypage':
        return 'mypage';
      default:
        return 'main';
    }
  };

  const currentActiveTab = getActiveTab();

  return (
    <nav className="bg-white py-4 shadow-md">
      <div className="flex justify-center gap-10 max-w-6xl mx-auto">
        <Link
          to="/main"
          className={`px-4 py-2 rounded-full font-medium transition-all duration-300 ${
            currentActiveTab === 'main' 
              ? 'bg-blue-500 text-white' 
              : 'text-gray-600 hover:bg-gray-100 hover:text-gray-800'
          }`}
        >
          메인
        </Link>
        <Link
          to="/test"
          className={`px-4 py-2 rounded-full font-medium transition-all duration-300 ${
            currentActiveTab === 'test' || currentActiveTab === 'results'
              ? 'bg-blue-500 text-white' 
              : 'text-gray-600 hover:bg-gray-100 hover:text-gray-800'
          }`}
        >
          그림검사
        </Link>
        <Link
          to="/chat"
          className={`px-4 py-2 rounded-full font-medium transition-all duration-300 ${
            currentActiveTab === 'chat' 
              ? 'bg-blue-500 text-white' 
              : 'text-gray-600 hover:bg-gray-100 hover:text-gray-800'
          }`}
        >
          챗봇
        </Link>
        <Link
          to="/mypage"
          className={`px-4 py-2 rounded-full font-medium transition-all duration-300 ${
            currentActiveTab === 'mypage' 
              ? 'bg-blue-500 text-white' 
              : 'text-gray-600 hover:bg-gray-100 hover:text-gray-800'
          }`}
        >
          마이페이지
        </Link>
        <Link
          to="/"
          className={`px-4 py-2 rounded-full font-medium transition-all duration-300 ${
            currentActiveTab === 'logout' 
              ? 'bg-blue-500 text-white' 
              : 'text-gray-600 hover:bg-gray-100 hover:text-gray-800'
          }`}
        >
          로그아웃
        </Link>
      </div>
    </nav>
  );
};

export default Navigation;