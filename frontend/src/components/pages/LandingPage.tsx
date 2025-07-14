import React from 'react';
import { useNavigate } from 'react-router-dom';

interface LandingPageProps {
  onGoogleLogin: () => void;
}

const LandingPage: React.FC<LandingPageProps> = ({ onGoogleLogin }) => {
  const navigate = useNavigate();

  const handleGoogleLogin = () => {
    onGoogleLogin();
    navigate('/main');
  };
  return (
    <div className="bg-gradient-to-br from-black to-gray-800 min-h-screen flex items-center justify-center text-white text-center">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-5xl font-bold mb-10 leading-tight">
          그림을 그리고<br />
          당신의 심리를 확인해보세요
        </h1>
        <div className="flex justify-center gap-5 my-10 flex-wrap">
          <div className="text-6xl mx-2 bounce-animation">🧸</div>
          <div className="text-6xl mx-2 bounce-animation">😊</div>
          <div className="text-6xl mx-2 bounce-animation">😤</div>
          <div className="text-6xl mx-2 bounce-animation">😢</div>
          <div className="text-6xl mx-2 bounce-animation">😱</div>
          <div className="text-6xl mx-2 bounce-animation">🤢</div>
          <div className="text-6xl mx-2 bounce-animation">💚</div>
        </div>
        <button 
          className="bg-white text-gray-800 border-none py-4 px-8 rounded-full text-lg font-semibold cursor-pointer flex items-center gap-3 mx-auto mt-10 hover:transform hover:-translate-y-1 hover:shadow-lg transition-all duration-300"
          onClick={handleGoogleLogin}
        >
          <span className="text-blue-600 font-bold">G</span>
          구글 로그인으로 시작하기
        </button>
      </div>
    </div>
  );
};

export default LandingPage;