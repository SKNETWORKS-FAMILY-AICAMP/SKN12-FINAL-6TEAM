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
import NicknamePage from './components/pages/NicknamePage';
// import FloatingChatBot from './components/common/FloatingChatBot';
import { useAppState } from './hooks/useAppState';
import './App.css';
import './components/DreamSearchApp.css';

const AppContent: React.FC = () => {
  const navigate = useNavigate();
  const {
    selectedCharacter,
    chatHistory,
    testResults,
    userProfile,
    showRatingModal,
    currentTestResult,
    getAvailableCharacters,
    handleGoogleLogin,
    handleStartDreamSearch,
    handleCharacterSelect,
    handleStartChat,
    handleShowRating,
    handleCloseRatingModal,
    handleNewChat,
    handleDeleteAccount,
    handleContinueChat,
    handleUpdateProfile,
    handleInitializeChat
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
      case 'characters':
        navigate('/characters');
        break;
      case 'nickname':
        navigate('/nickname');
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
              showRatingModal={showRatingModal}
              onShowRating={handleShowRating}
              onCloseRatingModal={handleCloseRatingModal}
              onNavigate={handleNavigate}
              onInitializeChat={handleInitializeChat}
              userId={1} // 실제로는 로그인한 사용자 ID
              friendsId={selectedCharacter ? parseInt(selectedCharacter.id) : 1}
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
              onUpdateProfile={handleUpdateProfile}
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
        <Route 
          path="/nickname" 
          element={
            <NicknamePage
              onComplete={(nickname) => {
                console.log('Nickname set:', nickname);
                // 여기서 닉네임을 저장하거나 처리할 수 있습니다
              }}
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