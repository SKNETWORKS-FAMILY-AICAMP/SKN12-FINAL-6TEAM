"use client"

import { Button } from "@/components/ui/button"
import Navigation from "./navigation"
import { ChevronLeft } from "lucide-react"

interface CharacterSelectionScreenProps {
  onNavigate: (screen: string) => void
  onSelectCharacter: (character: string) => void
}

export default function CharacterSelectionScreen({ onNavigate, onSelectCharacter }: CharacterSelectionScreenProps) {
  const characters = [
    {
      name: "추진이",
      description: "긍정적 생각 전환, 스트레스 해소, 자존감 향상 등을 통해 심리적인 해결책을 찾아 나갈 거예요.",
      color: "from-orange-500 to-red-600",
      bgColor: "from-orange-400 to-red-500",
      emoji: "🦊",
      buttonText: "추진이와\n대화하기",
      badge: null,
    },
    {
      name: "관계이",
      description: "당신의 솔직을 이해하고 함께 극복해나가는 방법을 찾아드립니다. 저와 함께 나아보아요.",
      color: "from-blue-500 to-purple-600",
      bgColor: "from-gray-600 to-gray-800",
      emoji: "🦝",
      buttonText: "관계이와\n대화하기",
      badge: "매칭된 페르소나",
    },
    {
      name: "내면이",
      description: "본능과 최정감을 간접하게 표현하고 해소하는 방법을 알려드릴게요. 마음의 평화를 찾아봐요.",
      color: "from-gray-500 to-gray-700",
      bgColor: "from-pink-200 to-brown-300",
      emoji: "🐰",
      buttonText: "내면이와\n대화하기",
      badge: "대화 중",
    },
    {
      name: "쾌락이",
      description: "불안과 두려움을 함께 극복해보아요. 누구보다 유쾌하고 재미있게 당신을 응원 해드릴게요.",
      color: "from-pink-500 to-red-600",
      bgColor: "from-yellow-400 to-orange-500",
      emoji: "🐰",
      buttonText: "쾌락이와\n대화하기",
      badge: null,
    },
    {
      name: "안정이",
      description: "저는 항상 당신 편이에요. 따뜻한 위로의 한마디로 당신의 마음이 평화로워지도록 도울게요.",
      color: "from-green-500 to-emerald-600",
      bgColor: "from-gray-100 to-gray-300",
      emoji: "🐼",
      buttonText: "안정이와\n대화하기",
      badge: null,
    },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0F103F] via-[#1a1b4a] via-[#2a2b5a] to-[#3a3b6a] relative overflow-hidden">
      <Navigation currentPage="챗봇" onNavigate={onNavigate} />

      {/* Starfield particles */}
      <div
        className="absolute inset-0 opacity-20"
        style={{
          backgroundImage: `url('/images/starfield-particles.png')`,
          backgroundSize: "cover",
          backgroundPosition: "center",
          backgroundRepeat: "no-repeat",
        }}
      ></div>

      {/* Multiple glowing orbs */}
      <div
        className="absolute top-20 right-20 w-24 h-24 opacity-60 animate-pulse"
        style={{
          backgroundImage: `url('/images/glowing-orb.png')`,
          backgroundSize: "contain",
          backgroundPosition: "center",
          backgroundRepeat: "no-repeat",
          animationDuration: "2s",
        }}
      ></div>

      <div
        className="absolute bottom-40 left-20 w-32 h-32 opacity-40 animate-pulse"
        style={{
          backgroundImage: `url('/images/glowing-orb.png')`,
          backgroundSize: "contain",
          backgroundPosition: "center",
          backgroundRepeat: "no-repeat",
          animationDuration: "3s",
          animationDelay: "1s",
        }}
      ></div>

      {/* Enhanced decorative space elements */}
      <div className="absolute top-32 left-16 w-16 h-20 bg-gradient-to-br from-orange-400 via-red-500 to-pink-500 rounded-full opacity-80 transform rotate-45 shadow-2xl">
        <div className="absolute top-2 left-2 w-12 h-16 bg-gradient-to-br from-gray-600 via-gray-800 to-black rounded-full"></div>
        <div className="absolute -bottom-2 left-6 w-4 h-8 bg-gradient-to-t from-yellow-400 via-orange-500 to-red-500 rounded-full opacity-90"></div>
      </div>

      {/* Enhanced floating orbs */}
      <div className="absolute top-20 right-20 w-8 h-8 bg-gradient-to-br from-cyan-400 via-blue-500 to-purple-600 rounded-full opacity-60 animate-pulse"></div>
      <div
        className="absolute top-40 right-32 w-4 h-4 bg-gradient-to-br from-pink-400 via-purple-500 to-indigo-600 rounded-full opacity-80 animate-pulse"
        style={{ animationDelay: "1s" }}
      ></div>
      <div
        className="absolute bottom-40 left-20 w-6 h-6 bg-gradient-to-br from-purple-400 via-pink-500 to-red-500 rounded-full opacity-70 animate-pulse"
        style={{ animationDelay: "2s" }}
      ></div>

      {/* Enhanced crystal/gem */}
      <div className="absolute bottom-16 right-16 w-32 h-40 opacity-60">
        <div
          className="w-full h-full bg-gradient-to-br from-purple-400 via-pink-500 via-orange-500 to-yellow-400 transform rotate-12 rounded-lg shadow-2xl animate-pulse"
          style={{ animationDelay: "0.5s" }}
        >
          <div className="absolute top-4 left-4 w-6 h-6 bg-white/30 rounded-full"></div>
          <div className="absolute bottom-6 right-6 w-4 h-4 bg-white/20 rounded-full"></div>
          <div className="absolute top-8 right-8 w-3 h-3 bg-cyan-400/40 rounded-full"></div>
        </div>
      </div>

      {/* Enhanced orbital rings */}
      <div
        className="absolute top-1/3 left-1/4 w-64 h-64 border border-purple-400/15 rounded-full animate-spin"
        style={{ animationDuration: "30s" }}
      ></div>
      <div
        className="absolute bottom-1/4 right-1/3 w-48 h-48 border border-cyan-400/15 rounded-full animate-spin"
        style={{ animationDuration: "25s" }}
      ></div>

      {/* Enhanced stars */}
      <div className="absolute top-1/4 left-1/2 w-1 h-1 bg-white rounded-full opacity-80 animate-pulse"></div>
      <div
        className="absolute top-1/2 right-1/4 w-1.5 h-1.5 bg-cyan-400 rounded-full opacity-60 animate-pulse"
        style={{ animationDelay: "1s" }}
      ></div>
      <div
        className="absolute bottom-1/3 left-1/3 w-1 h-1 bg-pink-400 rounded-full opacity-70 animate-pulse"
        style={{ animationDelay: "2s" }}
      ></div>

      {/* Back button */}
      <button
        onClick={() => onNavigate("chatbot")}
        className="absolute top-24 left-8 z-20 bg-white/20 hover:bg-white/30 backdrop-blur-sm rounded-full px-4 py-2 text-white text-sm font-medium transition-colors flex items-center border border-white/10"
      >
        <ChevronLeft size={16} className="mr-1" />
        대화로 돌아가기
      </button>

      <div className="relative z-10 container mx-auto px-8 py-24">
        <div className="text-center mb-12">
          <h1 className="text-3xl md:text-4xl font-bold text-white mb-4 drop-shadow-2xl">다른 캐릭터와 대화해보기</h1>
          <p className="text-white/80 text-lg drop-shadow-lg">각 캐릭터는 다른 접근과 상황에 특화되어 있어요</p>
        </div>

        <div className="max-w-4xl mx-auto space-y-6">
          {characters.map((character, index) => (
            <div
              key={index}
              className="bg-slate-600/40 backdrop-blur-sm rounded-3xl p-6 border border-white/20 hover:bg-slate-600/50 transition-all duration-300 shadow-2xl"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-6">
                  {/* Character Avatar */}
                  <div className="relative">
                    <div
                      className={`w-24 h-24 bg-gradient-to-br ${character.bgColor} rounded-full flex items-center justify-center shadow-2xl border border-white/10`}
                    >
                      <span className="text-4xl">{character.emoji}</span>
                    </div>
                    {/* Character badge */}
                    {character.badge && (
                      <div className="absolute -top-2 -right-2 bg-gradient-to-r from-purple-500/90 to-pink-500/90 backdrop-blur-sm px-2 py-1 rounded-full text-xs text-white font-medium shadow-lg border border-white/20">
                        {character.badge}
                      </div>
                    )}
                  </div>

                  <div className="flex-1">
                    <h3 className="text-2xl font-bold text-white mb-3 drop-shadow-lg">{character.name}</h3>
                    <p className="text-white/90 text-sm leading-relaxed max-w-md">{character.description}</p>
                  </div>
                </div>

                {/* Action Button */}
                <Button
                  onClick={() => {
                    onSelectCharacter(character.name)
                    onNavigate("chatbot")
                  }}
                  className={`bg-gradient-to-r ${character.color} hover:opacity-90 text-white px-6 py-4 rounded-2xl font-medium shadow-2xl hover:shadow-3xl transition-all duration-300 whitespace-pre-line text-center min-w-[120px] border border-white/20`}
                >
                  {character.buttonText}
                </Button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
