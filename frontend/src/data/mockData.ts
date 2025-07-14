import { ChatHistory, TestResult, UserProfile } from '../types';

export const mockChatHistory: ChatHistory[] = [
  {
    id: '1',
    characterId: '1',
    characterName: '기쁨이',
    characterAvatar: '😊',
    messages: [
      {
        id: '1',
        type: 'assistant',
        content: '안녕하세요! 오늘 기분이 어떠세요?',
        timestamp: '2024-01-15 10:30:00'
      },
      {
        id: '2',
        type: 'user',
        content: '좀 우울해요',
        timestamp: '2024-01-15 10:31:00'
      },
      {
        id: '3',
        type: 'assistant',
        content: '그렇군요. 어떤 일이 있었나요? 차근차근 이야기해보세요.',
        timestamp: '2024-01-15 10:32:00'
      }
    ],
    date: '2024-01-15',
    lastMessage: '그렇군요. 어떤 일이 있었나요? 차근차근 이야기해보세요.'
  },
  {
    id: '2',
    characterId: '3',
    characterName: '슬픔이',
    characterAvatar: '😢',
    messages: [
      {
        id: '1',
        type: 'assistant',
        content: '안녕... 무엇이 너를 가장 슬프게 하니..?',
        timestamp: '2024-01-14 14:20:00'
      },
      {
        id: '2',
        type: 'user',
        content: '요즘 일이 잘 안풀려서 힘들어요',
        timestamp: '2024-01-14 14:21:00'
      },
      {
        id: '3',
        type: 'assistant',
        content: '그런 마음... 나도 잘 알아. 혼자가 아니야.',
        timestamp: '2024-01-14 14:22:00'
      }
    ],
    date: '2024-01-14',
    lastMessage: '그런 마음... 나도 잘 알아. 혼자가 아니야.'
  },
  {
    id: '3',
    characterId: '2',
    characterName: '버럭이',
    characterAvatar: '😤',
    messages: [
      {
        id: '1',
        type: 'assistant',
        content: '뭔가 화나는 일이 있었나?',
        timestamp: '2024-01-13 16:45:00'
      },
      {
        id: '2',
        type: 'user',
        content: '네, 직장에서 불합리한 일이 있었어요',
        timestamp: '2024-01-13 16:46:00'
      }
    ],
    date: '2024-01-13',
    lastMessage: '뭔가 화나는 일이 있었나?'
  }
];

export const mockTestResults: TestResult[] = [
  {
    id: '1',
    testType: 'HTP',
    result: '슬픔이',
    characterMatch: '슬픔이',
    date: '2024-01-15',
    description: '집, 나무, 사람 그림을 통한 심리 분석 결과, 현재 내면의 슬픔과 고독감이 강하게 드러났습니다. 하지만 이는 일시적인 감정으로, 적절한 상담과 관리를 통해 극복할 수 있습니다.',
    images: ['house.jpg', 'tree.jpg', 'person.jpg']
  },
  {
    id: '2',
    testType: 'Drawing',
    result: '기쁨이',
    characterMatch: '기쁨이',
    date: '2024-01-10',
    description: '자유 그림 검사 결과, 밝고 긍정적인 에너지가 느껴집니다. 색채 사용과 구도에서 안정감과 희망이 표현되었습니다.',
    images: ['drawing1.jpg']
  },
  {
    id: '3',
    testType: 'HTP',
    result: '기쁨이',
    characterMatch: '기쁨이',
    date: '2024-01-05',
    description: '이전 검사 대비 심리적 안정감이 크게 향상되었습니다. 특히 집 그림에서 따뜻함과 안정감이 잘 표현되었습니다.',
    images: ['house2.jpg', 'tree2.jpg', 'person2.jpg']
  }
];

export const mockUserProfile: UserProfile = {
  id: '1',
  name: '김철수',
  email: 'kimcs@example.com',
  joinDate: '2024-01-01',
  totalTests: 3,
  totalChats: 15
};