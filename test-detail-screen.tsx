"use client"

import Navigation from "./navigation"
import { ChevronLeft } from "lucide-react"

interface TestDetailScreenProps {
  onNavigate: (screen: string) => void
}

export default function TestDetailScreen({ onNavigate }: TestDetailScreenProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0F103F] via-[#1a1b4a] to-[#2a2b5a] relative overflow-hidden">
      <Navigation currentPage="마이페이지" onNavigate={onNavigate} />

      {/* Decorative elements */}
      <div className="absolute bottom-20 right-20 w-48 h-48 bg-gradient-to-br from-cyan-400 to-purple-500 rounded-full opacity-20 blur-2xl"></div>

      {/* Back button */}
      <button
        onClick={() => onNavigate("mypage")}
        className="absolute top-24 left-8 z-20 bg-white/20 hover:bg-white/30 backdrop-blur-sm rounded-full px-4 py-2 text-white text-sm font-medium transition-colors flex items-center"
      >
        <ChevronLeft size={16} className="mr-1" />
        마이페이지로 돌아가기
      </button>

      <div className="relative z-10 container mx-auto px-8 py-24">
        <div className="text-center mb-8">
          <h1 className="text-3xl md:text-4xl font-bold text-white mb-4">검사 결과 상세</h1>
          <p className="text-white/80">검사 일시: 2025년 7월 22일</p>
        </div>

        <div className="max-w-4xl mx-auto">
          <div className="bg-slate-700/50 backdrop-blur-sm rounded-3xl p-8 border border-white/20">
            <h2 className="text-2xl font-bold text-white text-center mb-8">검사 결과</h2>

            <div className="bg-slate-600/50 rounded-2xl p-8 mb-8">
              <p className="text-white/90 text-sm leading-relaxed mb-6">
                현재 심리 상태는 안정적이고 긍정적인 것으로 보입니다. 그림을 받고 진단한 요소들을 구성하여 있어 긍정적인
                감정을 나타냅니다. 나무는 상대적으로 높은 안정을 보이며, 이는 자연과의 연결과 안정감을 중요시하는 경향을
                나타냅니다. 행복이 함께 비치고 있는 점은 희망적이고 긍정적인 에너지를 표현한다. 이러한 점들은 현재 상태
                만족하고 있으며, 환경과의 조화로운 관계를 유지하고 있 음을 시사합니다. 주변은 안전하고 안정적인
                상황이며, 안전한 환경 감각하는 능력이 대단 긍정적이고 안스러운 상태임을 보여주니 다. 외부 환경과
                조화롭게 지내며, 긍정적인 마태를 기대하는 모습을 보입니다.
              </p>

              <div className="flex justify-center">
                <div className="w-32 h-32 bg-white/90 rounded-2xl flex items-center justify-center">
                  <div className="w-24 h-24 bg-gradient-to-br from-green-400 to-blue-500 rounded-lg flex items-center justify-center">
                    <span className="text-white text-xs">그림 이미지</span>
                  </div>
                </div>
              </div>

              <p className="text-white/70 text-center text-sm mt-4">그림을 클릭하여 더 자세히 볼 수 있습니다</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
