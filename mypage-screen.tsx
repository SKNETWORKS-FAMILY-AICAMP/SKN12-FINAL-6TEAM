"use client"

import { Button } from "@/components/ui/button"
import Navigation from "./navigation"
import { User } from "lucide-react"

interface MyPageScreenProps {
  onNavigate: (screen: string) => void
}

export default function MyPageScreen({ onNavigate }: MyPageScreenProps) {
  const chatHistory = [
    {
      character: "관계이",
      emoji: "🦝",
      date: "2025년 7월 23일 오후 03:52",
      screen: "chatbot",
    },
    {
      character: "안정이",
      emoji: "🐼",
      date: "2025년 7월 21일 오후 10:30",
      screen: "chatbot",
    },
    {
      character: "쾌락이",
      emoji: "🐰",
      date: "2025년 7월 20일 오후 07:10",
      screen: "chatbot",
    },
  ]

  const testHistory = [
    {
      title: "매칭 페르소나: 관계이",
      date: "2025년 7월 23일 오후 03:52",
      screen: "personality-analysis",
    },
    {
      title: "매칭 페르소나: 쾌락이",
      date: "2025년 7월 20일 오후 7:10",
      screen: "test-detail",
    },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0F103F] via-[#1a1b4a] via-[#2a2b5a] to-[#3a3b6a] relative overflow-hidden">
      <Navigation currentPage="마이페이지" onNavigate={onNavigate} />

      {/* Minimal particles background */}
      <div
        className="absolute inset-0 opacity-25"
        style={{
          backgroundImage: `url('/images/minimal-particles.png')`,
          backgroundSize: "cover",
          backgroundPosition: "center",
          backgroundRepeat: "no-repeat",
        }}
      ></div>

      {/* Cosmic spheres */}
      <div
        className="absolute top-1/3 left-1/4 w-80 h-52 opacity-30 animate-pulse"
        style={{
          backgroundImage: `url('/images/cosmic-spheres.png')`,
          backgroundSize: "contain",
          backgroundPosition: "center",
          backgroundRepeat: "no-repeat",
          animationDuration: "4s",
        }}
      ></div>

      {/* Enhanced decorative elements */}
      <div className="absolute bottom-20 right-20 w-48 h-48 bg-gradient-to-br from-cyan-400 via-purple-500 to-pink-500 rounded-full opacity-20 blur-2xl animate-pulse"></div>
      <div
        className="absolute top-20 left-20 w-32 h-32 bg-gradient-to-br from-purple-400 via-indigo-500 to-blue-500 rounded-full opacity-30 blur-xl animate-pulse"
        style={{ animationDelay: "2s" }}
      ></div>

      <div className="relative z-10 container mx-auto px-8 py-24">
        <h1 className="text-3xl md:text-4xl font-bold text-white text-center mb-12 drop-shadow-2xl">마이페이지</h1>

        {/* User Profile */}
        <div className="max-w-4xl mx-auto mb-8">
          <div className="bg-slate-700/50 backdrop-blur-sm rounded-3xl p-8 border border-white/20 shadow-2xl">
            <div className="flex items-center space-x-4">
              <div className="w-16 h-16 bg-gradient-to-br from-purple-400/30 via-pink-400/20 to-cyan-400/30 rounded-full flex items-center justify-center border border-white/20">
                <User size={32} className="text-white" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white mb-1 drop-shadow-lg">하지오래 ✏️</h2>
                <p className="text-white/70 text-sm">가입일: 2025년 7월 23일 | 총 검사 2회 | 총 채팅 3회</p>
              </div>
            </div>
          </div>
        </div>

        <div className="max-w-4xl mx-auto grid md:grid-cols-2 gap-8">
          {/* Chat History */}
          <div className="bg-slate-700/50 backdrop-blur-sm rounded-3xl p-8 border border-white/20 shadow-2xl">
            <h3 className="text-xl font-bold text-white text-center mb-8 drop-shadow-lg">채팅 히스토리</h3>

            <div className="space-y-4 mb-6">
              {chatHistory.map((chat, index) => (
                <div
                  key={index}
                  className="bg-slate-600/50 rounded-2xl p-4 border border-white/10 hover:bg-slate-600/60 transition-all duration-300"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-12 h-12 bg-gradient-to-br from-gray-600 to-gray-800 rounded-full flex items-center justify-center shadow-lg">
                        <span className="text-xl">{chat.emoji}</span>
                      </div>
                      <div>
                        <h4 className="text-white font-bold">{chat.character}와의 대화</h4>
                        <p className="text-white/70 text-xs">{chat.date}</p>
                      </div>
                    </div>
                    <Button
                      onClick={() => onNavigate(chat.screen)}
                      className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 hover:from-purple-500/30 hover:to-pink-500/30 text-white px-4 py-2 rounded-full text-sm border border-white/10"
                    >
                      이어서 대화하기
                    </Button>
                  </div>
                </div>
              ))}
            </div>

            <p className="text-white/50 text-center text-sm">모든 채팅 기록을 불러왔습니다</p>
          </div>

          {/* Test Results History */}
          <div className="bg-slate-700/50 backdrop-blur-sm rounded-3xl p-8 border border-white/20 shadow-2xl">
            <h3 className="text-xl font-bold text-white text-center mb-8 drop-shadow-lg">그림 검사 결과</h3>

            <div className="space-y-4 mb-6">
              {testHistory.map((test, index) => (
                <div
                  key={index}
                  className="bg-slate-600/50 rounded-2xl p-4 border border-white/10 hover:bg-slate-600/60 transition-all duration-300"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-12 h-12 bg-gradient-to-br from-purple-400/30 to-pink-400/30 rounded-lg flex items-center justify-center border border-white/10">
                        <span className="text-xl">🎨</span>
                      </div>
                      <div>
                        <h4 className="text-white font-bold">{test.title}</h4>
                        <p className="text-white/70 text-xs">{test.date}</p>
                      </div>
                    </div>
                    <Button
                      onClick={() => onNavigate(test.screen)}
                      className="bg-gradient-to-r from-cyan-500/20 to-blue-500/20 hover:from-cyan-500/30 hover:to-blue-500/30 text-white px-4 py-2 rounded-full text-sm border border-white/10"
                    >
                      자세히 보기
                    </Button>
                  </div>
                </div>
              ))}
            </div>

            <p className="text-white/50 text-center text-sm">모든 검사 결과를 불러왔습니다</p>
          </div>
        </div>

        {/* Logout Button */}
        <div className="max-w-4xl mx-auto mt-8">
          <Button
            onClick={() => onNavigate("welcome")}
            className="bg-gradient-to-r from-slate-600/50 to-slate-700/50 hover:from-slate-600/70 hover:to-slate-700/70 text-white px-6 py-3 rounded-full font-medium border border-white/10"
          >
            회원탈퇴
          </Button>
        </div>
      </div>
    </div>
  )
}
