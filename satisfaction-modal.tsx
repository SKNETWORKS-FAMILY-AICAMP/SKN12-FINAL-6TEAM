"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Star } from "lucide-react"

interface SatisfactionModalProps {
  onClose: () => void
  onSubmit: () => void
}

export default function SatisfactionModal({ onClose, onSubmit }: SatisfactionModalProps) {
  const [rating, setRating] = useState(0)
  const [feedback, setFeedback] = useState("")

  const handleSubmit = () => {
    // Handle satisfaction survey submission
    onSubmit()
  }

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-md w-full p-6">
        <h2 className="text-xl font-bold text-gray-800 text-center mb-6">만족도 조사</h2>

        {/* Star rating */}
        <div className="flex justify-center mb-4">
          {[1, 2, 3, 4, 5].map((star) => (
            <button key={star} onClick={() => setRating(star)} className="p-1">
              <Star
                size={32}
                className={`${
                  star <= rating ? "fill-yellow-400 text-yellow-400" : "fill-gray-300 text-gray-300"
                } transition-colors`}
              />
            </button>
          ))}
        </div>

        <div className="text-center mb-6">
          <h3 className="font-bold text-gray-800 mb-2">기타 의견(선택)</h3>
        </div>

        <Textarea
          placeholder="이 캐릭터는 제 취향과 맞지않아요. 지에게 더 맞는 해결책을 제시해주어요 등 챗봇에 대한 의견을 자유롭게 작성하세요"
          value={feedback}
          onChange={(e) => setFeedback(e.target.value)}
          className="w-full h-24 mb-6 resize-none"
        />

        <Button
          onClick={handleSubmit}
          className="w-full bg-gradient-to-r from-pink-500 to-blue-600 hover:from-pink-600 hover:to-blue-700 text-white py-3 rounded-full font-medium"
        >
          다른 캐릭터와 대화하기
        </Button>
      </div>
    </div>
  )
}
