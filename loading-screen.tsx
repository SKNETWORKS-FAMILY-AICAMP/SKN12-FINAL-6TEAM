"use client"

import { useEffect } from "react"
import Navigation from "./navigation"

interface LoadingScreenProps {
  onNext: () => void
}

export default function LoadingScreen({ onNext }: LoadingScreenProps) {
  useEffect(() => {
    const timer = setTimeout(() => {
      onNext()
    }, 3000)

    return () => clearTimeout(timer)
  }, [onNext])

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0F103F] via-[#1a1b4a] to-[#2a2b5a] relative overflow-hidden">
      <Navigation currentPage="그림검사" onNavigate={() => {}} />

      {/* Decorative elements */}
      <div className="absolute top-1/4 left-1/4 w-32 h-32 bg-gradient-to-br from-cyan-400 to-blue-500 rounded-full opacity-30 blur-xl animate-pulse"></div>
      <div className="absolute bottom-1/3 right-1/4 w-24 h-24 bg-gradient-to-br from-pink-400 to-purple-500 rounded-full opacity-40 blur-lg animate-pulse"></div>

      {/* Orbital rings */}
      <div className="absolute inset-0 flex items-center justify-center">
        <div
          className="w-[500px] h-[500px] border border-cyan-400/20 rounded-full animate-spin"
          style={{ animationDuration: "20s" }}
        ></div>
        <div
          className="absolute w-[600px] h-[600px] border border-purple-400/10 rounded-full animate-spin"
          style={{ animationDuration: "30s" }}
        ></div>
      </div>

      <div className="relative z-10 flex items-center justify-center min-h-screen px-8">
        <div className="max-w-md mx-auto">
          {/* Phone mockup */}
          <div className="bg-slate-600/40 backdrop-blur-sm rounded-3xl p-8 border border-white/20">
            <h1 className="text-white text-lg font-bold text-center mb-8">그림 업로드</h1>

            {/* Loading content */}
            <div className="bg-white rounded-2xl p-8 text-center">
              {/* Loading dots */}
              <div className="flex justify-center mb-4">
                <div className="flex space-x-1">
                  <div className="w-3 h-3 bg-purple-500 rounded-full animate-bounce"></div>
                  <div
                    className="w-3 h-3 bg-purple-500 rounded-full animate-bounce"
                    style={{ animationDelay: "0.1s" }}
                  ></div>
                  <div
                    className="w-3 h-3 bg-purple-500 rounded-full animate-bounce"
                    style={{ animationDelay: "0.2s" }}
                  ></div>
                </div>
              </div>

              <h2 className="text-gray-800 font-bold text-lg mb-4">그림을 분석하고 있습니다</h2>

              <div className="text-gray-600 text-sm mb-6">
                AI가 당신의 그림을 분석해서
                <br />
                심리 상태를 파악하고 있습니다
              </div>

              {/* Progress indicators */}
              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm text-gray-600">
                  <span>🟣 이미지 처리</span>
                </div>

                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-pink-500 to-purple-600 h-2 rounded-full animate-pulse"
                    style={{ width: "82%" }}
                  ></div>
                </div>

                <div className="text-xs text-gray-500">나머지 82%만을 기다려주세요</div>

                <div className="bg-gray-100 rounded-lg p-4 mt-6">
                  <div className="text-xs text-gray-600 leading-relaxed">
                    무슨거 같긴 같은 분석이 사실 좀 길어, 심리학과 에서만 같은 것 수준의 분석을 할 수 있어서 지식이 좀
                    복잡 부족하긴 수 있습니다. 단, 관련 법령에 따라 보존할 필요가 있는 경우 해당 법령에서 정한 기간 동안
                    보관할 수 있습니다. 무슨거 같긴 같은 분석이 사실 좀 길어, 심리학과 에서만 같은 것 수준의 분석을 할
                    수 있어서 관련 서비스를 제공받으실 수 없습니다.
                  </div>
                </div>

                <div className="text-xs text-gray-500 mt-4">이미지를 처리하고 있습니다...</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
