"use client"

import { useState } from "react"
import WelcomeScreen from "../welcome-screen"
import SignupScreen from "../signup-screen"
import MainScreen from "../main-screen"
import DrawingTestIntro from "../drawing-test-intro"
import TermsModal from "../terms-modal"
import DrawingUpload from "../drawing-upload"
import LoadingScreen from "../loading-screen"
import ResultsScreen from "../results-screen"
import ChatbotScreen from "../chatbot-screen"
import CharacterSelectionScreen from "../character-selection-screen"
import MyPageScreen from "../mypage-screen"
import TestDetailScreen from "../test-detail-screen"
import PersonalityAnalysisScreen from "../personality-analysis-screen"
import SatisfactionModal from "../satisfaction-modal"

export default function App() {
  const [currentScreen, setCurrentScreen] = useState("welcome")
  const [showTermsModal, setShowTermsModal] = useState(false)
  const [showSatisfactionModal, setShowSatisfactionModal] = useState(false)
  const [selectedCharacter, setSelectedCharacter] = useState("내면이")

  const renderScreen = () => {
    switch (currentScreen) {
      case "welcome":
        return <WelcomeScreen onNext={() => setCurrentScreen("signup")} />
      case "signup":
        return <SignupScreen onNext={() => setCurrentScreen("main")} />
      case "main":
        return <MainScreen onNavigate={setCurrentScreen} />
      case "drawing-test-intro":
        return <DrawingTestIntro onNext={() => setShowTermsModal(true)} onNavigate={setCurrentScreen} />
      case "drawing-upload":
        return <DrawingUpload onNext={() => setCurrentScreen("loading")} onNavigate={setCurrentScreen} />
      case "loading":
        return <LoadingScreen onNext={() => setCurrentScreen("results")} />
      case "results":
        return <ResultsScreen onNavigate={setCurrentScreen} />
      case "chatbot":
        return <ChatbotScreen onNavigate={setCurrentScreen} onShowSatisfaction={() => setShowSatisfactionModal(true)} />
      case "character-selection":
        return <CharacterSelectionScreen onNavigate={setCurrentScreen} onSelectCharacter={setSelectedCharacter} />
      case "mypage":
        return <MyPageScreen onNavigate={setCurrentScreen} />
      case "test-detail":
        return <TestDetailScreen onNavigate={setCurrentScreen} />
      case "personality-analysis":
        return <PersonalityAnalysisScreen onNavigate={setCurrentScreen} />
      default:
        return <WelcomeScreen onNext={() => setCurrentScreen("signup")} />
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-800">
      {renderScreen()}
      {showTermsModal && (
        <TermsModal
          onClose={() => setShowTermsModal(false)}
          onAccept={() => {
            setShowTermsModal(false)
            setCurrentScreen("drawing-upload")
          }}
        />
      )}
      {showSatisfactionModal && (
        <SatisfactionModal
          onClose={() => setShowSatisfactionModal(false)}
          onSubmit={() => {
            setShowSatisfactionModal(false)
            setCurrentScreen("character-selection")
          }}
        />
      )}
    </div>
  )
}
