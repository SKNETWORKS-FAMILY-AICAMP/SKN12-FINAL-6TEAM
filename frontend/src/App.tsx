import React from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import MainPage from './components/pages/MainPage';
import TestPage from './components/pages/TestPage';
import TestInstructionPage from './components/pages/TestInstructionPage';
import ResultsPage from './components/pages/ResultsPage';
import ResultDetailPage from './components/pages/ResultDetailPage';
import CharactersPage from './components/pages/CharactersPage';
import ChatPage from './components/pages/ChatPage';
import MyPage from './components/pages/MyPage';
import LandingPage from './components/pages/LandingPage';
// import FloatingChatBot from './components/common/FloatingChatBot';
import { useAppState } from './hooks/useAppState';
import './App.css';
import './components/DreamSearchApp.css';

const AppContent: React.FC = () => {
  const navigate = useNavigate();
  const {
    selectedCharacter,
    chatMessages,
    chatHistory,
    testResults,
    userProfile,
    showRatingModal,
    currentTestResult,
    isSending,
    getAvailableCharacters,
    handleGoogleLogin,
    handleStartDreamSearch,
    handleCharacterSelect,
    handleStartChat,
    handleSendMessage,
    handleShowRating,
    handleCloseRatingModal,
    handleNewChat,
    handleDeleteAccount,
    handleContinueChat
  } = useAppState();

  const handleNavigate = (screen: string) => {
    switch (screen) {
      case 'main':
        navigate('/main');
        break;
      case 'test':
        navigate('/test');
        break;
      case 'test-instruction':
        navigate('/test-instruction');
        break;
      case 'mypage':
        navigate('/mypage');
        break;
      case 'landing':
        navigate('/');
        break;
      case 'results':
        navigate('/results');
        break;
      case 'chat':
        navigate('/chat');
        break;
      default:
        break;
    }
  };

  const handleStartAnalysis = (imageFile: File | null, description: string) => {
    // 여기서 이미지와 설명을 저장하거나 처리할 수 있습니다
    console.log('Analysis started with:', { imageFile, description });
    handleStartDreamSearch();
  };

  return (
    <div className="App font-sans min-h-screen bg-gray-100">
      <Routes>
        <Route path="/" element={<LandingPage onGoogleLogin={handleGoogleLogin} />} />
        <Route 
          path="/main" 
          element={
            <MainPage 
              onStartDreamSearch={handleStartDreamSearch} 
              onNavigate={handleNavigate} 
            />
          } 
        />
        <Route 
          path="/test" 
          element={
            <TestPage 
              onStartAnalysis={handleStartAnalysis} 
              onNavigate={handleNavigate} 
            />
          } 
        />
        <Route 
          path="/test-instruction" 
          element={
            <TestInstructionPage 
              onStartAnalysis={handleStartAnalysis} 
              onNavigate={handleNavigate} 
            />
          } 
        />
        <Route 
          path="/results" 
          element={
            <ResultsPage
              characters={getAvailableCharacters()}
              selectedCharacter={selectedCharacter}
              showModal={false}
              onCharacterSelect={handleCharacterSelect}
              onCloseModal={() => {}}
              onStartChat={handleStartChat}
              onNavigate={handleNavigate}
              currentTestResult={currentTestResult}
            />
          } 
        />
        <Route 
          path="/chat" 
          element={
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
          } 
        />
        <Route 
          path="/mypage" 
          element={
            <MyPage
              chatHistory={chatHistory}
              testResults={testResults}
              userProfile={userProfile}
              onNewChat={handleNewChat}
              onDeleteAccount={handleDeleteAccount}
              onNavigate={handleNavigate}
              onContinueChat={handleContinueChat}
            />
          } 
        />
        <Route 
          path="/result-detail/:id" 
          element={
            <ResultDetailPage
              testResults={testResults}
              onNavigate={handleNavigate}
              onStartChat={handleStartChat}
            />
          } 
        />
        <Route 
          path="/characters" 
          element={
            <CharactersPage
              characters={getAvailableCharacters()}
              selectedCharacter={selectedCharacter}
              onCharacterSelect={handleCharacterSelect}
              onStartChat={handleStartChat}
              onNavigate={handleNavigate}
            />
          } 
        />
      </Routes>
      {/* <FloatingChatBot /> */}
    </div>
  );
};

const App: React.FC = () => {
  return (
    <Router>
      <AppContent />
    </Router>
  );
};

export default App;