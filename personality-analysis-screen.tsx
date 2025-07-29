"use client"

import { Button } from "@/components/ui/button"
import Navigation from "./navigation"
import { ChevronLeft } from "lucide-react"

interface PersonalityAnalysisScreenProps {
  onNavigate: (screen: string) => void
}

export default function PersonalityAnalysisScreen({ onNavigate }: PersonalityAnalysisScreenProps) {
  const personalityData = [
    { name: "추진이", percentage: 68.1, color: "from-orange-500 to-red-600" },
    { name: "내면이", percentage: 40, color: "from-gray-500 to-gray-700" },
    { name: "안정이", percentage: 23.5, color: "from-blue-500 to-purple-600" },
    { name: "관계이", percentage: 10.7, color: "from-purple-500 to-pink-600" },
    { name: "쾌락이", percentage: 9.1, color: "from-yellow-500 to-orange-600" },
  ]

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
        <div className="max-w-4xl mx-auto">
          <div className="bg-slate-700/50 backdrop-blur-sm rounded-3xl p-8 border border-white/20">
            <h1 className="text-2xl font-bold text-white text-center mb-8">당신의 성격 유형</h1>

            <div className="grid md:grid-cols-2 gap-8 items-center">
              {/* Character Display */}
              <div className="text-center">
                <div className="w-48 h-48 bg-slate-600/50 rounded-3xl flex flex-col items-center justify-center mx-auto mb-6">
                  <div className="w-24 h-24 bg-gradient-to-br from-orange-400 to-red-500 rounded-full flex items-center justify-center mb-4">
                    <span className="text-4xl">🦊</span>
                  </div>
                  <h2 className="text-2xl font-bold text-white">추진이</h2>
                </div>
              </div>

              {/* Personality Bars */}
              <div className="space-y-4">
                {personalityData.map((item, index) => (
                  <div key={index} className="flex items-center space-x-4">
                    <div className="w-16 text-white text-sm font-medium">{item.name}</div>
                    <div className="flex-1 bg-slate-600/50 rounded-full h-3 overflow-hidden">
                      <div
                        className={`h-full bg-gradient-to-r ${item.color} transition-all duration-1000`}
                        style={{ width: `${item.percentage}%` }}
                      ></div>
                    </div>
                    <div className="w-12 text-white text-sm font-medium text-right">{item.percentage}%</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="mt-8 text-center">
              <p className="text-white/90 text-lg mb-4 italic">"목표 실현부터 실행까지, 단호하게 밀어붙인다"</p>
              <p className="text-white/80 text-sm mb-6">
                '추진이'는 사용자의 머릿거림과 나태함을 용납하지 않는 성과 중심 챗봇입니다.
                <br />
                감정적인 위로나 공감 대신, 즉시 실행 가능한 목표와 행동 계획을 제시하고
                <br />
                압박감 있는 피드백으로 당신을 밀어붙입니다.
              </p>

              <div className="bg-slate-600/50 rounded-2xl p-6 mb-8">
                <h3 className="text-white font-bold mb-4">추진이의 특징</h3>
                <ul className="text-white/90 text-sm space-y-2 text-left max-w-md mx-auto">
                  <li>• 집중 이면의 진짜 문제를 즉시 파악</li>
                  <li>• 불필요한 말 없이, 행동 중심의 실행 솔루션 제공</li>
                  <li>• 지금 하지 않으면 어떤 결과가 따라올지 경고</li>
                  <li>• 최고 수준의 기준을 설정하고, 성과로 검증</li>
                </ul>
              </div>

              <Button
                onClick={() => onNavigate("chatbot")}
                className="bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-600 hover:to-red-700 text-white px-8 py-3 rounded-full font-medium shadow-lg hover:shadow-xl transition-all duration-300"
              >
                추진이와 대화하기
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
