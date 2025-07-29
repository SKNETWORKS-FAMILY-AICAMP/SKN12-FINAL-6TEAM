"use client"

import { Button } from "@/components/ui/button"
import Navigation from "./navigation"

interface ResultsScreenProps {
  onNavigate: (screen: string) => void
}

export default function ResultsScreen({ onNavigate }: ResultsScreenProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0F103F] via-[#1a1b4a] to-[#2a2b5a] relative overflow-hidden">
      <Navigation currentPage="그림검사" onNavigate={onNavigate} />

      {/* Decorative elements */}
      <div className="absolute top-20 left-20 w-24 h-24 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full opacity-60 blur-lg"></div>
      <div className="absolute bottom-20 right-20 w-48 h-48 bg-gradient-to-br from-purple-400 to-pink-500 rounded-full opacity-30 blur-2xl"></div>

      <div className="relative z-10 container mx-auto px-8 py-8">
        {/* Main result card */}
        <div className="max-w-4xl mx-auto mb-8">
          <div className="bg-slate-700/50 backdrop-blur-sm rounded-3xl p-8 border border-white/20">
            <h1 className="text-white text-xl font-bold text-center mb-8">그림 심리 분석 결과</h1>

            <div className="bg-slate-600/50 rounded-2xl p-8">
              <div className="flex items-center justify-between mb-6">
                <div className="flex-1">
                  <h2 className="text-white text-2xl font-bold mb-2">
                    당신의 페르소나는 <span className="text-pink-400">내면이</span> 입니다
                  </h2>

                  <div className="w-full bg-gray-300 rounded-full h-3 mb-4">
                    <div
                      className="bg-gradient-to-r from-pink-500 to-purple-600 h-3 rounded-full"
                      style={{ width: "82%" }}
                    ></div>
                  </div>

                  <div className="text-white/90 text-sm mb-4">나와 82%만큼 가까워진</div>
                </div>

                <div className="w-32 h-32 bg-gradient-to-br from-pink-200 to-brown-300 rounded-full flex items-center justify-center ml-8">
                  <span className="text-4xl">🐰</span>
                </div>
              </div>

              <div className="bg-slate-500/50 rounded-xl p-6 mb-6">
                <p className="text-white/90 text-sm leading-relaxed">
                  무슨거 같긴 같은 분석이 사실 좀 길어, 심리학과 에서만 같은 것 수준의 분석을 할 수 있어서 지식이 좀
                  복잡 부족하긴 수 있습니다. 단, 관련 법령에 따라 보존할 필요가 있는 경우 해당 법령에서 정한 기간 동안
                  보관할 수 있습니다. 무슨거 같긴 같은 분석이 사실 좀 길어, 심리학과 에서만 같은 것 수준의 분석을 할 수
                  있어서 지식이 좀 복잡 부족하긴 수 있습니다. 단, 관련 법령에 따라 보존할 필요가 있는 경우 해당 법령에서
                  정한 기간 동안 보관할 수 있습니다.
                </p>
              </div>

              <Button
                onClick={() => onNavigate("chatbot")}
                className="w-full bg-gradient-to-r from-pink-500 to-purple-600 hover:from-pink-600 hover:to-purple-700 text-white py-3 rounded-full font-medium"
              >
                내면이와 대화하기
              </Button>
            </div>
          </div>
        </div>

        {/* Other character options */}
        <div className="max-w-4xl mx-auto">
          <div className="bg-slate-700/50 backdrop-blur-sm rounded-3xl p-8 border border-white/20">
            <h2 className="text-white text-xl font-bold text-center mb-8">그림 심리 분석 결과</h2>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              {/* Character 1 */}
              <div className="bg-slate-600/50 rounded-2xl p-6 text-center">
                <div className="w-16 h-16 bg-gradient-to-br from-orange-400 to-red-500 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">🦊</span>
                </div>
                <h3 className="text-white font-bold mb-2">추진이</h3>
                <p className="text-white/70 text-sm mb-2">나와 60%만큼</p>
                <p className="text-white/70 text-sm">가까워진!</p>
              </div>

              {/* Character 2 */}
              <div className="bg-slate-600/50 rounded-2xl p-6 text-center">
                <div className="w-16 h-16 bg-gradient-to-br from-gray-600 to-gray-800 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">🦝</span>
                </div>
                <h3 className="text-white font-bold mb-2">관계이</h3>
                <p className="text-white/70 text-sm mb-2">나와 40%만큼</p>
                <p className="text-white/70 text-sm">가까워진!</p>
              </div>

              {/* Character 3 */}
              <div className="bg-slate-600/50 rounded-2xl p-6 text-center">
                <div className="w-16 h-16 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">🐰</span>
                </div>
                <h3 className="text-white font-bold mb-2">쾌락이</h3>
                <p className="text-white/70 text-sm mb-2">나와 20%만큼</p>
                <p className="text-white/70 text-sm">가까워진!</p>
              </div>

              {/* Character 4 */}
              <div className="bg-slate-600/50 rounded-2xl p-6 text-center">
                <div className="w-16 h-16 bg-gradient-to-br from-gray-100 to-gray-300 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">🐼</span>
                </div>
                <h3 className="text-white font-bold mb-2">안정이</h3>
                <p className="text-white/70 text-sm mb-2">나와 10%만큼</p>
                <p className="text-white/70 text-sm">가까워진!</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
