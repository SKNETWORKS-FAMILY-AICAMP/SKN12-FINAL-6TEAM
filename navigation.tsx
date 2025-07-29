"use client"

interface NavigationProps {
  currentPage: string
  onNavigate: (screen: string) => void
}

export default function Navigation({ currentPage, onNavigate }: NavigationProps) {
  const navItems = [
    { name: "메인", screen: "main" },
    { name: "그림검사", screen: "drawing-test-intro" },
    { name: "챗봇", screen: "chatbot" },
    { name: "마이페이지", screen: "mypage" },
    { name: "로그아웃", screen: "welcome" },
  ]

  return (
    <nav className="relative z-20 flex justify-center items-center py-6">
      <div className="flex space-x-8">
        {navItems.map((item) => (
          <button
            key={item.name}
            onClick={() => onNavigate(item.screen)}
            className={`px-6 py-2 rounded-full text-sm font-medium transition-all duration-300 ${
              currentPage === item.name
                ? "bg-white text-gray-800 shadow-lg"
                : "text-white/70 hover:text-white hover:bg-white/10"
            }`}
          >
            {item.name}
          </button>
        ))}
      </div>
    </nav>
  )
}
