import React from 'react';
import LandingPage from './pages/LandingPage';
import MainPage from './pages/MainPage';
import ResultsPage from './pages/ResultsPage';
import ChatPage from './pages/ChatPage';
import MyPage from './pages/MyPage';
import FloatingChatBot from './common/FloatingChatBot';
import { useAppState } from '../hooks/useAppState';
import { characters } from '../data/characters';
import './DreamSearchApp.css';

const DreamSearchApp: React.FC = () => {
  const {
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
    handleDeleteAccount
  } = useAppState();

  const handleNavigate = (screen: string) => {
    switch (screen) {
      case 'main':
        handleStartDreamSearch();
        break;
      case 'mypage':
        handleGoToMyPage();
        break;
      case 'landing':
        handleGoogleLogin();
        break;
      default:
        break;
    }
  };

  const renderScreen = () => {
    switch (currentScreen) {
      case 'landing':
        return <LandingPage onGoogleLogin={handleGoogleLogin} />;
      case 'main':
        return <MainPage onStartDreamSearch={handleStartDreamSearch} onNavigate={handleNavigate} />;
      case 'results':
        return (
          <ResultsPage
            characters={getAvailableCharacters()}
            selectedCharacter={selectedCharacter}
            showModal={showModal}
            onCharacterSelect={handleCharacterSelect}
            onCloseModal={handleCloseModal}
            onStartChat={handleStartChat}
            onNavigate={handleNavigate}
            currentTestResult={currentTestResult}
          />
        );
      case 'chat':
        return (
          <ChatPage
            selectedCharacter={selectedCharacter}
            chatMessages={chatMessages}
            onSendMessage={handleSendMessage}
            showRatingModal={showRatingModal}
            onShowRating={handleShowRating}
            onCloseRatingModal={handleCloseRatingModal}
            onNavigate={handleNavigate}
            isSending={isSending}
          />
        );
      case 'mypage':
        return (
          <MyPage
            chatHistory={chatHistory}
            testResults={testResults}
            userProfile={userProfile}
            onNewChat={handleNewChat}
            onDeleteAccount={handleDeleteAccount}
            onNavigate={handleNavigate}
          />
        );
      default:
        return <LandingPage onGoogleLogin={handleGoogleLogin} />;
    }
  };

  return (
    <div className="font-sans min-h-screen bg-gray-100">
      {renderScreen()}
      <FloatingChatBot />
    </div>
  );
};

export default DreamSearchApp;