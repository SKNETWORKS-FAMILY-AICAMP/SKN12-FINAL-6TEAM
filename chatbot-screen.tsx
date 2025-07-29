"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import Navigation from "./navigation"
import { ChevronLeft, ChevronRight, MessageCircle } from "lucide-react"

interface ChatbotScreenProps {
  onNavigate: (screen: string) => void
  onShowSatisfaction?: () => void
}

export default function ChatbotScreen({ onNavigate, onShowSatisfaction }: ChatbotScreenProps) {
  const [message, setMessage] = useState("")
  const [showChatPanel, setShowChatPanel] = useState(false)

  return (
    <div className="min-h-screen relative overflow-hidden">
      <style jsx>{`
  @keyframes natural-movement {
    0% {
      transform: translateX(0px) translateY(0px);
    }
    25% {
      transform: translateX(-8px) translateY(-12px);
    }
    50% {
      transform: translateX(5px) translateY(-8px);
    }
    75% {
      transform: translateX(-3px) translateY(-15px);
    }
    100% {
      transform: translateX(0px) translateY(0px);
    }
  }
  
  .natural-movement {
    animation: natural-movement 3s ease-in-out infinite;
  }
`}</style>
      {/* Modern flowing background */}
      <div className="absolute inset-0 bg-gradient-to-br from-purple-600 via-purple-700 to-purple-900">
        {/* Flowing wave patterns */}
        <div className="absolute inset-0">
          {/* Top flowing lines */}
          <div className="absolute top-0 left-0 w-full h-32 bg-gradient-to-r from-transparent via-purple-400/20 to-transparent transform -skew-y-12"></div>
          <div className="absolute top-8 left-0 w-full h-24 bg-gradient-to-r from-transparent via-pink-400/15 to-transparent transform -skew-y-12"></div>
          <div className="absolute top-16 left-0 w-full h-16 bg-gradient-to-r from-transparent via-cyan-400/10 to-transparent transform -skew-y-12"></div>

          {/* Bottom flowing lines */}
          <div className="absolute bottom-0 left-0 w-full h-40 bg-gradient-to-r from-transparent via-blue-400/20 to-transparent transform skew-y-12"></div>
          <div className="absolute bottom-8 left-0 w-full h-32 bg-gradient-to-r from-transparent via-cyan-400/15 to-transparent transform skew-y-12"></div>
          <div className="absolute bottom-16 left-0 w-full h-24 bg-gradient-to-r from-transparent via-purple-400/10 to-transparent transform skew-y-12"></div>
        </div>

        {/* Floating orbs */}
        <div className="absolute top-20 right-1/4 w-24 h-24 bg-gradient-to-br from-purple-400/40 to-pink-500/40 rounded-full blur-sm"></div>
        <div className="absolute top-32 left-1/3 w-16 h-16 bg-gradient-to-br from-cyan-400/50 to-blue-500/50 rounded-full blur-sm"></div>
        <div className="absolute bottom-1/3 right-1/6 w-32 h-32 bg-gradient-to-br from-pink-400/30 to-purple-500/30 rounded-full blur-md"></div>
        <div className="absolute bottom-1/4 left-1/4 w-20 h-20 bg-gradient-to-br from-blue-400/40 to-cyan-500/40 rounded-full blur-sm"></div>
        <div className="absolute top-1/2 right-1/3 w-28 h-28 bg-gradient-to-br from-purple-500/35 to-pink-400/35 rounded-full blur-md"></div>

        {/* Large background orbs */}
        <div className="absolute top-1/4 left-1/6 w-48 h-48 bg-gradient-to-br from-cyan-400/20 to-blue-500/20 rounded-full blur-2xl"></div>
        <div className="absolute bottom-1/4 right-1/6 w-56 h-56 bg-gradient-to-br from-pink-400/15 to-purple-500/15 rounded-full blur-3xl"></div>

        {/* Mystical planet-like orb (bottom right) */}
        <div className="absolute bottom-20 right-20 w-40 h-40 bg-gradient-to-br from-orange-400/60 via-purple-500/60 to-blue-500/60 rounded-full blur-sm opacity-80">
          <div className="absolute inset-2 bg-gradient-to-br from-yellow-400/40 via-pink-500/40 to-cyan-500/40 rounded-full"></div>
          <div className="absolute inset-4 bg-gradient-to-br from-orange-300/30 via-purple-400/30 to-blue-400/30 rounded-full"></div>
        </div>
      </div>

      <Navigation currentPage="챗봇" onNavigate={onNavigate} />

      {/* Back button */}
      <button
        onClick={() => onNavigate("main")}
        className="absolute top-8 left-8 z-20 w-12 h-12 bg-pink-500 hover:bg-pink-600 rounded-full flex items-center justify-center text-white transition-colors shadow-lg"
      >
        <ChevronLeft size={24} />
      </button>

      {/* Bookmark-shaped chat toggle button */}
      <button
        onClick={() => setShowChatPanel(!showChatPanel)}
        className={`absolute top-1/2 transform -translate-y-1/2 z-20 transition-all duration-300 ${
          showChatPanel ? "right-80" : "right-0"
        }`}
      >
        <div className="relative">
          {/* Bookmark shape with rounded corners and custom gradient */}
          <div className="w-16 h-20 bg-gradient-to-br from-[#FF6948]/50 to-[#FF0051]/50 hover:from-[#FF6948]/60 hover:to-[#FF0051]/60 transition-colors shadow-lg relative rounded-l-2xl backdrop-blur-sm border border-white/10">
            {/* Bookmark notch */}
            <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-8 border-r-8 border-t-8 border-transparent border-t-[#FF0051]/50"></div>
          </div>

          {/* Arrow icon */}
          <div className="absolute inset-0 flex items-center justify-center text-white">
            {showChatPanel ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
          </div>
        </div>
      </button>

      {/* Main content */}
      <div
        className={`relative z-10 flex flex-col items-center justify-center min-h-screen px-8 transition-all duration-300 ${
          showChatPanel ? "mr-80" : ""
        }`}
      >
        {/* Rabbit character with natural movement animation */}
        <div className="mb-8">
          <div className="w-24 h-24 flex items-center justify-center natural-movement">
            <span className="text-6xl">🐰</span>
          </div>
        </div>

        {/* Speech bubble */}
        <div className="mb-16 max-w-lg">
          <div className="bg-black/80 backdrop-blur-sm rounded-3xl px-8 py-6 text-center shadow-2xl relative">
            <h2 className="text-white font-bold text-xl mb-3">안녕! 반가워, 어떻게 지내?</h2>
            <p className="text-white/90 text-base leading-relaxed">
              무슨 일이 있는지, 어떤 생각들이 있는지 나너에게도 좋아. 듣고 싶어!
              <span className="ml-1">😊</span>
            </p>
            {/* Speech bubble tail */}
            <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-full">
              <div className="w-0 h-0 border-l-6 border-r-6 border-t-12 border-transparent border-t-black/80"></div>
            </div>
          </div>
        </div>

        {/* Input area */}
        <div className="w-full max-w-2xl">
          <div className="flex space-x-4">
            <Input
              type="text"
              placeholder="내면이에게 고민을 이야기해보세요"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              className="flex-1 px-6 py-4 rounded-full bg-white border-0 text-gray-800 placeholder-gray-500 text-base shadow-lg focus:ring-2 focus:ring-purple-400 focus:outline-none"
            />
            <Button className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white px-8 py-4 rounded-full font-medium text-base shadow-lg">
              전송
            </Button>
          </div>
        </div>
      </div>

      {/* Chat panel */}
      <div
        className={`absolute top-0 right-0 w-80 h-full bg-gradient-to-b from-teal-400/30 via-cyan-400/25 to-blue-400/30 backdrop-blur-xl border-l border-white/10 z-30 transition-transform duration-300 ${
          showChatPanel ? "translate-x-0" : "translate-x-full"
        }`}
      >
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-white font-bold flex items-center text-lg">
              <MessageCircle className="mr-2" size={20} />
              채팅 내역
            </h3>
          </div>

          <div className="text-white/80 text-sm mb-6">내면이와의 대화</div>

          <div className="space-y-4 mb-6">
            <div className="flex justify-end">
              <div className="bg-gradient-to-r from-blue-500 to-blue-600 text-white p-3 rounded-2xl text-sm max-w-[80%] shadow-lg">
                안녕
              </div>
            </div>

            <div className="flex justify-start">
              <div className="bg-white/95 text-gray-800 p-3 rounded-2xl text-sm max-w-[80%] shadow-lg leading-relaxed">
                안녕! 반가워, 어떻게 지내?
                <br />
                무슨 일이 있는지,
                <br />
                어떤 생각들이 있는지
                <br />
                나너에게도 좋아. 듣고 싶어!😊
              </div>
            </div>
          </div>

          <Button
            onClick={() => {
              setShowChatPanel(false)
              onShowSatisfaction?.()
            }}
            className="w-full bg-gradient-to-r from-pink-500 to-purple-600 hover:from-pink-600 hover:to-purple-700 text-white py-3 rounded-full font-medium shadow-lg"
          >
            다른 캐릭터와 대화하기
          </Button>
        </div>
      </div>
    </div>
  )
}
