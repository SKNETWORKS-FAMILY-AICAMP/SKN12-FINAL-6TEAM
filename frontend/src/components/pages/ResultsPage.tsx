import React from 'react';
import { useNavigate } from 'react-router-dom';
import Navigation from '../common/Navigation';
import CharacterCard from '../common/CharacterCard';
import { SearchResult } from '../../types';

interface ResultsPageProps {
  characters: SearchResult[];
  selectedCharacter: SearchResult | null;
  showModal: boolean;
  onCharacterSelect: (character: SearchResult) => void;
  onCloseModal: () => void;
  onStartChat: () => void;
  onNavigate?: (screen: string) => void;
  currentTestResult: string;
}

const ResultsPage: React.FC<ResultsPageProps> = ({
  characters,
  onCharacterSelect,
  onStartChat,
  onNavigate,
  currentTestResult
}) => {
  const navigate = useNavigate();

  const handleCharacterClick = (character: SearchResult) => {
    onCharacterSelect(character);
    onStartChat();
    navigate('/chat');
  };
  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation onNavigate={onNavigate} />

      <div className="container mx-auto px-5 py-8 max-w-4xl">
        <div className="text-center mb-8">
          <div className="flex justify-center items-center gap-4 mb-6">
            <div className="text-6xl">😢</div>
            <div className="bg-white rounded-2xl p-4 shadow-lg relative">
              <div className="absolute left-0 top-1/2 transform -translate-y-1/2 -translate-x-2">
                <div className="w-4 h-4 bg-white rotate-45 shadow-lg"></div>
              </div>
              <p className="text-gray-700 font-medium">
                나를<br />
                놀리나.
              </p>
            </div>
          </div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">
            당신의 페르소나는 <span className="text-blue-600">{currentTestResult}</span> 입니다
          </h2>
        </div>

        <div className="bg-white rounded-2xl shadow-lg p-6 mb-8">
          <div className="flex items-start space-x-4">
            <div className="bg-blue-500 text-white w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm flex-shrink-0">
              01
            </div>
            <div>
              <h4 className="text-lg font-semibold text-gray-800 mb-2">검사 결과 요약</h4>
              <p className="text-gray-600 text-sm leading-relaxed mb-4">
                당신의 그림에서 나타난 심리적 특성을 분석한 결과, 현재 내면의 슬픔과 고민이 깊어 보입니다. 이러한 감정을 이해하고 함께 극복해나가는 것이 중요합니다.
              </p>
              <div className="flex flex-wrap gap-2">
                <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">감정적 깊이</span>
                <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">내성적 성향</span>
                <span className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm font-medium">공감 능력</span>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-lg p-6">
          <h3 className="text-xl font-bold text-gray-800 mb-4 text-center">
            {currentTestResult === '슬픔이' ? '대화 가능한 캐릭터' : '모든 결과 유형 보기'}
          </h3>
          {currentTestResult === '슬픔이' && (
            <p className="text-center text-gray-600 text-sm mb-6">
              현재 검사 결과에 따라 슬픔이와만 대화할 수 있습니다.
            </p>
          )}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {characters.map(character => (
              <div key={character.id} className="text-center">
                <div className="mb-4">
                  <CharacterCard
                    character={character}
                    onClick={handleCharacterClick}
                  />
                </div>
                <button 
                  className="w-full bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded-lg text-sm font-medium transition-colors duration-200"
                  onClick={() => handleCharacterClick(character)}
                >
                  {character.name}와 대화하기
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResultsPage;