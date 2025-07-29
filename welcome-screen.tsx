"use client"

import { Button } from "@/components/ui/button"

interface WelcomeScreenProps {
  onNext: () => void
}

export default function WelcomeScreen({ onNext }: WelcomeScreenProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-800 relative overflow-hidden">
      {/* Decorative elements */}
      <div className="absolute top-20 left-20 w-32 h-32 bg-gradient-to-br from-cyan-400 to-purple-500 rounded-full opacity-20 blur-xl"></div>
      <div className="absolute bottom-20 right-20 w-48 h-48 bg-gradient-to-br from-pink-400 to-orange-500 rounded-full opacity-20 blur-xl"></div>
      <div className="absolute top-1/2 left-10 w-24 h-24 bg-gradient-to-br from-blue-400 to-cyan-500 rounded-full opacity-30 blur-lg"></div>

      {/* Orbital rings */}
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="w-96 h-96 border border-cyan-400/20 rounded-full"></div>
        <div className="absolute w-[500px] h-[500px] border border-purple-400/10 rounded-full"></div>
        <div className="absolute w-[600px] h-[600px] border border-pink-400/10 rounded-full"></div>
      </div>

      <div className="relative z-10 flex flex-col items-center justify-center min-h-screen px-8">
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-6xl font-bold text-white mb-6">그림을 그리고</h1>
          <h2 className="text-3xl md:text-5xl font-bold text-white mb-8">당신의 심리를 확인해보세요</h2>
        </div>

        {/* Animal characters */}
        <div className="flex items-center justify-center mb-12 space-x-4">
          <div className="w-20 h-20 bg-gradient-to-br from-orange-400 to-red-500 rounded-full flex items-center justify-center">
            <span className="text-2xl">🦊</span>
          </div>
          <div className="w-20 h-20 bg-gradient-to-br from-gray-600 to-gray-800 rounded-full flex items-center justify-center">
            <span className="text-2xl">🦝</span>
          </div>
          <div className="w-20 h-20 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center">
            <span className="text-2xl">🐰</span>
          </div>
          <div className="w-20 h-20 bg-gradient-to-br from-gray-100 to-gray-300 rounded-full flex items-center justify-center">
            <span className="text-2xl">🐼</span>
          </div>
          <div className="w-20 h-20 bg-gradient-to-br from-pink-200 to-gray-300 rounded-full flex items-center justify-center">
            <span className="text-2xl">🐰</span>
          </div>
        </div>

        {/* Google login button */}
        <Button
          onClick={onNext}
          className="bg-gradient-to-r from-pink-500 to-purple-600 hover:from-pink-600 hover:to-purple-700 text-white px-12 py-4 rounded-full text-lg font-medium shadow-lg hover:shadow-xl transition-all duration-300"
        >
          <span className="mr-3 text-xl">G</span>
          구글 로그인으로 시작하기
        </Button>
      </div>
    </div>
  )
}
