"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import Navigation from "./navigation"

interface DrawingUploadProps {
  onNext: () => void
  onNavigate: (screen: string) => void
}

export default function DrawingUpload({ onNext, onNavigate }: DrawingUploadProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setSelectedFile(file)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0F103F] via-[#1a1b4a] to-[#2a2b5a] relative overflow-hidden">
      <Navigation currentPage="그림검사" onNavigate={onNavigate} />

      {/* Decorative elements */}
      <div className="absolute top-1/4 left-1/4 w-24 h-24 bg-gradient-to-br from-cyan-400 to-blue-500 rounded-full opacity-40 blur-lg"></div>
      <div className="absolute bottom-1/3 right-1/4 w-32 h-32 bg-gradient-to-br from-pink-400 to-purple-500 rounded-full opacity-30 blur-xl"></div>

      {/* Orbital rings */}
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="w-[500px] h-[500px] border border-cyan-400/10 rounded-full"></div>
        <div className="absolute w-[600px] h-[600px] border border-purple-400/10 rounded-full"></div>
      </div>

      <div className="relative z-10 flex items-center justify-center min-h-screen px-8">
        <div className="max-w-md mx-auto">
          {/* Main container */}
          <div className="bg-slate-600/40 backdrop-blur-sm rounded-3xl p-8 border border-white/20">
            <h1 className="text-white text-xl font-bold text-center mb-8">그림 업로드</h1>

            {/* Instructions */}
            <div className="bg-slate-500/50 rounded-2xl p-6 mb-8">
              <h2 className="text-white font-bold mb-4">필독사항</h2>
              <div className="text-white/90 text-sm space-y-2">
                <p>• 메모장, 흰드문 노트 등을 활용해 집, 나무, 사람 각 요소를 분리하게 그려주세요</p>
                <p>• 3가지 요소를 모두 그려야 정상적인 검사가 가능합니다</p>
                <p>• 파일 업로드는 JPG 및 PNG로만 가능합니다</p>
              </div>
            </div>

            {/* Upload area */}
            <div className="border-2 border-dashed border-white/30 rounded-2xl p-8 mb-6 text-center">
              <p className="text-white/70 mb-4">파일을 드래그해서 놓거나, 클릭하여 불러오세요</p>

              <input
                type="file"
                accept="image/jpeg,image/png,image/jpg"
                onChange={handleFileSelect}
                className="hidden"
                id="file-upload"
              />

              <label htmlFor="file-upload">
                <Button
                  type="button"
                  className="bg-gradient-to-r from-pink-500 to-purple-600 hover:from-pink-600 hover:to-purple-700 text-white px-8 py-3 rounded-full cursor-pointer"
                >
                  파일 선택하기
                </Button>
              </label>

              {selectedFile && <p className="text-white/90 mt-4 text-sm">선택된 파일: {selectedFile.name}</p>}
            </div>

            {/* Example images */}
            <div className="bg-slate-500/50 rounded-2xl p-6">
              <h3 className="text-white font-bold mb-4 text-center">예시</h3>
              <div className="grid grid-cols-4 gap-3">
                <div className="bg-white rounded-lg p-2 aspect-square flex items-center justify-center">
                  <span className="text-xs text-gray-600">집 그림</span>
                </div>
                <div className="bg-white rounded-lg p-2 aspect-square flex items-center justify-center">
                  <span className="text-xs text-gray-600">나무 그림</span>
                </div>
                <div className="bg-white rounded-lg p-2 aspect-square flex items-center justify-center">
                  <span className="text-xs text-gray-600">사람 그림</span>
                </div>
                <div className="bg-white rounded-lg p-2 aspect-square flex items-center justify-center">
                  <span className="text-xs text-gray-600">전체 그림</span>
                </div>
              </div>
            </div>

            {selectedFile && (
              <Button
                onClick={onNext}
                className="w-full mt-6 bg-gradient-to-r from-pink-500 to-purple-600 hover:from-pink-600 hover:to-purple-700 text-white py-3 rounded-full font-medium"
              >
                분석 시작하기
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
