"use client"

import { Button } from "@/components/ui/button"
import Navigation from "./navigation"

interface MainScreenProps {
  onNavigate: (screen: string) => void
}

export default function MainScreen({ onNavigate }: MainScreenProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0F103F] via-[#1a1b4a] via-[#2a2b5a] to-[#3a3b6a] relative overflow-hidden">
      <Navigation currentPage="메인" onNavigate={onNavigate} />

      {/* Starfield background */}
      <div
        className="absolute inset-0 opacity-30"
        style={{
          backgroundImage: `url('/images/starfield-particles.png')`,
          backgroundSize: "cover",
          backgroundPosition: "center",
          backgroundRepeat: "no-repeat",
        }}
      ></div>

      {/* Cosmic spheres */}
      <div
        className="absolute top-1/4 right-1/4 w-96 h-64 opacity-40"
        style={{
          backgroundImage: `url('/images/cosmic-spheres.png')`,
          backgroundSize: "contain",
          backgroundPosition: "center",
          backgroundRepeat: "no-repeat",
        }}
      ></div>

      {/* Glowing orb */}
      <div
        className="absolute bottom-20 left-20 w-32 h-32 opacity-60"
        style={{
          backgroundImage: `url('/images/glowing-orb.png')`,
          backgroundSize: "contain",
          backgroundPosition: "center",
          backgroundRepeat: "no-repeat",
        }}
      ></div>

      {/* Enhanced decorative orbs */}
      <div className="absolute top-20 left-20 w-32 h-32 bg-gradient-to-br from-pink-400 via-purple-500 to-indigo-600 rounded-full opacity-40 blur-xl animate-pulse"></div>
      <div
        className="absolute top-40 right-32 w-24 h-24 bg-gradient-to-br from-cyan-400 via-blue-500 to-purple-600 rounded-full opacity-50 blur-lg animate-pulse"
        style={{ animationDelay: "1s" }}
      ></div>
      <div
        className="absolute bottom-32 left-1/4 w-20 h-20 bg-gradient-to-br from-purple-400 via-pink-500 to-red-500 rounded-full opacity-60 blur-sm animate-pulse"
        style={{ animationDelay: "2s" }}
      ></div>
      <div
        className="absolute bottom-20 right-20 w-48 h-48 bg-gradient-to-br from-cyan-400 via-purple-500 to-pink-500 rounded-full opacity-20 blur-2xl animate-pulse"
        style={{ animationDelay: "0.5s" }}
      ></div>

      {/* Mystical orbital rings */}
      <div className="absolute top-1/3 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
        <div
          className="w-96 h-96 border border-cyan-400/20 rounded-full animate-spin"
          style={{ animationDuration: "20s" }}
        ></div>
        <div
          className="absolute inset-0 w-[500px] h-[500px] border border-purple-400/15 rounded-full -translate-x-12 -translate-y-12 animate-spin"
          style={{ animationDuration: "30s" }}
        ></div>
        <div
          className="absolute inset-0 w-[600px] h-[600px] border border-pink-400/10 rounded-full -translate-x-24 -translate-y-24 animate-spin"
          style={{ animationDuration: "40s" }}
        ></div>
      </div>

      <div className="relative z-10 container mx-auto px-8 py-16">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <div className="flex items-center justify-center mb-8">
            <div className="w-16 h-16 bg-gradient-to-br from-cyan-400 via-purple-500 to-pink-500 rounded-full mr-4 opacity-80 animate-pulse"></div>
            <div
              className="w-12 h-12 bg-gradient-to-br from-pink-400 via-purple-500 to-indigo-500 rounded-full opacity-60 animate-pulse"
              style={{ animationDelay: "1s" }}
            ></div>
          </div>

          <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 drop-shadow-2xl">MY MOODY</h1>

          <div className="text-white/90 text-lg md:text-xl mb-4 max-w-2xl mx-auto drop-shadow-lg">
            당신의 감정이 위로받을 수 있도록 -
          </div>
          <div className="text-white/90 text-lg md:text-xl mb-8 max-w-2xl mx-auto drop-shadow-lg">
            마이무디는 HTP* 그림 심리 분석과 맞춤형 챗봇 기능을 제공합니다
          </div>

          <div className="text-white/70 text-sm mb-8 max-w-2xl mx-auto">
            HTP란? House(집) - Tree(나무) - Person(사람)으로 구성된 그림심리검사로,
            <br />
            당신의 심리 상태를 확인할 수 있습니다
          </div>

          <Button
            onClick={() => onNavigate("drawing-test-intro")}
            className="bg-gradient-to-r from-pink-500 via-purple-600 to-indigo-600 hover:from-pink-600 hover:via-purple-700 hover:to-indigo-700 text-white px-8 py-3 rounded-full text-lg font-medium shadow-2xl hover:shadow-3xl transition-all duration-300 border border-white/20"
          >
            그림검사 시작하기
          </Button>
        </div>

        {/* About Service Section */}
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-12 drop-shadow-xl">About Service</h2>

          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            {/* Service Card 1 */}
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 border border-white/20 hover:bg-white/15 transition-all duration-300 shadow-xl">
              <div className="w-48 h-48 mx-auto mb-6 flex items-center justify-center">
                <img src="/images/frame1.png" alt="심리 상태 분석" className="w-full h-full object-contain" />
              </div>
              <h3 className="text-xl font-bold text-white mb-4">심리 상태 분석</h3>
              <p className="text-white/70 text-sm">
                그림을 통한
                <br />
                심리 상태 파악
              </p>
            </div>

            {/* Service Card 2 */}
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 border border-white/20 hover:bg-white/15 transition-all duration-300 shadow-xl">
              <div className="w-48 h-48 mx-auto mb-6 flex items-center justify-center">
                <img src="/images/frame2.png" alt="전문적 분석" className="w-full h-full object-contain" />
              </div>
              <h3 className="text-xl font-bold text-white mb-4">전문적 분석</h3>
              <p className="text-white/70 text-sm">
                AI 기반
                <br />
                심리 분석 제공
              </p>
            </div>

            {/* Service Card 3 */}
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 border border-white/20 hover:bg-white/15 transition-all duration-300 shadow-xl">
              <div className="w-48 h-48 mx-auto mb-6 flex items-center justify-center">
                <img src="/images/frame3.png" alt="맞춤형 상담" className="w-full h-full object-contain" />
              </div>
              <h3 className="text-xl font-bold text-white mb-4">맞춤형 상담</h3>
              <p className="text-white/70 text-sm">
                개인별
                <br />
                맞춤 상담 서비스
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
