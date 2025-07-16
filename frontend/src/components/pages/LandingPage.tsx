import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService } from '../../services/authService';

interface LandingPageProps {
  onGoogleLogin?: () => void;
}

const LandingPage: React.FC<LandingPageProps> = ({ onGoogleLogin }) => {
  const navigate = useNavigate();

  useEffect(() => {
    // URL에서 토큰 확인 (Google OAuth 콜백에서 전달됨)
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    
    if (token) {
      // 토큰을 로컬스토리지에 저장하고 리다이렉션
      localStorage.setItem('access_token', token);
      
      // URL에서 토큰 제거
      window.history.replaceState({}, document.title, window.location.pathname);
      
      // 사용자 정보 확인 후 적절한 페이지로 이동
      const checkAuthAndRedirect = async () => {
        const user = await authService.getCurrentUser();
        if (user) {
          if (user.is_first_login) {
            navigate('/nickname');
          } else {
            navigate('/main');
          }
        }
      };
      
      checkAuthAndRedirect();
      return;
    }
    
    // 이미 로그인한 경우 메인으로 리디렉션
    const checkAuth = async () => {
      const user = await authService.getCurrentUser();
      if (user) {
        if (user.is_first_login) {
          navigate('/nickname');
        } else {
          navigate('/main');
        }
      }
    };
    
    checkAuth();
  }, [navigate]);

  const handleGoogleLogin = () => {
    try {
      console.log('Starting Google login with redirect...');
      
      const clientId = process.env.REACT_APP_GOOGLE_CLIENT_ID || '689738363605-i65c3ar97vnts2jeh648dj3v9b23njq4.apps.googleusercontent.com';
      const redirectUri = `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/auth/google/callback`;
      const scope = 'email profile';
      
      // Google OAuth2 서버 리다이렉션 방식
      const googleAuthUrl = `https://accounts.google.com/o/oauth2/v2/auth?` +
        `client_id=${clientId}&` +
        `redirect_uri=${encodeURIComponent(redirectUri)}&` +
        `scope=${encodeURIComponent(scope)}&` +
        `response_type=code&` +
        `access_type=offline`;
      
      console.log('Redirecting to:', googleAuthUrl);
      
      // Google OAuth 페이지로 리다이렉션
      window.location.href = googleAuthUrl;
      
    } catch (error) {
      console.error('Login failed:', error);
      navigate('/nickname');
    }
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
        <div className="flex flex-col items-center gap-4">
          <button 
            className="bg-white text-gray-800 border-none py-4 px-8 rounded-full text-lg font-semibold cursor-pointer flex items-center gap-3 mx-auto mt-10 hover:transform hover:-translate-y-1 hover:shadow-lg transition-all duration-300"
            onClick={handleGoogleLogin}
          >
            <span className="text-blue-600 font-bold">G</span>
            구글 로그인으로 시작하기
          </button>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;