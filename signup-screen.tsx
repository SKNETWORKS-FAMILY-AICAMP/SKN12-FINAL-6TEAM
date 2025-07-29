"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

interface SignupScreenProps {
  onNext: () => void
}

export default function SignupScreen({ onNext }: SignupScreenProps) {
  const [nickname, setNickname] = useState("")
  const [isVerified, setIsVerified] = useState(false)

  const handleVerifyNickname = () => {
    if (nickname.trim()) {
      setIsVerified(true)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-800 relative overflow-hidden">
      {/* Floating orbs */}
      <div className="absolute top-20 left-20 w-24 h-24 bg-gradient-to-br from-purple-400 to-pink-500 rounded-full opacity-60 blur-sm"></div>
      <div className="absolute top-40 left-40 w-16 h-16 bg-gradient-to-br from-cyan-400 to-blue-500 rounded-full opacity-40 blur-sm"></div>
      <div className="absolute bottom-32 left-32 w-20 h-20 bg-gradient-to-br from-pink-400 to-purple-500 rounded-full opacity-50 blur-sm"></div>
      <div className="absolute bottom-20 right-20 w-32 h-32 bg-gradient-to-br from-cyan-400 to-purple-500 rounded-full opacity-30 blur-lg"></div>
      <div className="absolute top-1/3 right-1/4 w-12 h-12 bg-gradient-to-br from-blue-400 to-cyan-500 rounded-full opacity-60"></div>

      {/* Stars */}
      <div className="absolute top-1/4 left-1/3 w-2 h-2 bg-cyan-400 rounded-full opacity-80"></div>
      <div className="absolute top-1/2 right-1/3 w-1 h-1 bg-pink-400 rounded-full opacity-60"></div>
      <div className="absolute bottom-1/3 left-1/4 w-1.5 h-1.5 bg-purple-400 rounded-full opacity-70"></div>

      <div className="relative z-10 flex flex-col items-center justify-center min-h-screen px-8">
        <div className="text-center mb-6">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-8">닉네임을 알려주세요</h1>
        </div>

        <div className="w-full max-w-md mb-6">
          <Input
            type="text"
            placeholder="AI 캐릭터가 당신을 부르는 이름을 설정해주세요"
            value={nickname}
            onChange={(e) => setNickname(e.target.value)}
            className="w-full px-6 py-4 rounded-full bg-white/90 backdrop-blur-sm border-0 text-gray-800 placeholder-gray-500 text-center text-lg focus:ring-2 focus:ring-purple-400"
          />
        </div>

        <Button
          onClick={handleVerifyNickname}
          disabled={!nickname.trim() || isVerified}
          className="bg-gradient-to-r from-pink-500 to-blue-600 hover:from-pink-600 hover:to-blue-700 disabled:from-gray-400 disabled:to-gray-500 text-white px-12 py-4 rounded-full text-lg font-medium shadow-lg hover:shadow-xl transition-all duration-300 mb-8"
        >
          {isVerified ? "중복 확인 완료" : "닉네임 중복 확인"}
        </Button>

        <p className="text-white/70 text-center text-sm mb-16">
          마이페이지 - 프로필 수정에서 언제든 다시 바꿀 수 있어요
        </p>
      </div>

      {/* Bottom gradient backgrounds */}
      <div className="absolute bottom-0 left-0 right-0 h-20 bg-gradient-to-t from-purple-600/50 to-transparent pointer-events-none"></div>
      <div className="absolute bottom-0 left-0 right-0 h-12 bg-gradient-to-r from-pink-500/30 via-purple-500/30 to-blue-500/30 pointer-events-none"></div>

      {/* 전체 하단 영역의 완료 버튼 - 항상 표시되지만 중복 확인 후에만 클릭 가능 */}
      <div
        onClick={isVerified ? onNext : undefined}
        className={`absolute bottom-0 left-0 right-0 h-32 z-20 transition-all duration-300 flex items-end justify-center pb-6 ${
          isVerified ? "cursor-pointer hover:opacity-90" : "cursor-not-allowed opacity-50"
        }`}
      >
        <div
          className={`font-bold text-xl transition-colors duration-300 ${isVerified ? "text-white" : "text-white/50"}`}
        >
          완료
        </div>
      </div>
    </div>
  )
}
