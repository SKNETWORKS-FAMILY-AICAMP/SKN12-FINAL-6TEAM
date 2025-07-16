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
        timestamp: '2025-01-15 10:30:00'
      },
      {
        id: '2',
        type: 'user',
        content: '좀 우울해요',
        timestamp: '2025-01-15 10:31:00'
      },
      {
        id: '3',
        type: 'assistant',
        content: '그렇군요. 어떤 일이 있었나요? 차근차근 이야기해보세요.',
        timestamp: '2025-01-15 10:32:00'
      }
    ],
    date: '2025-01-15',
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
        timestamp: '2025-01-14 14:20:00'
      },
      {
        id: '2',
        type: 'user',
        content: '요즘 일이 잘 안풀려서 힘들어요',
        timestamp: '2025-01-14 14:21:00'
      },
      {
        id: '3',
        type: 'assistant',
        content: '그런 마음... 나도 잘 알아. 혼자가 아니야.',
        timestamp: '2025-01-14 14:22:00'
      }
    ],
    date: '2025-01-14',
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
        timestamp: '2025-01-13 16:45:00'
      },
      {
        id: '2',
        type: 'user',
        content: '네, 직장에서 불합리한 일이 있었어요',
        timestamp: '2025-01-13 16:46:00'
      }
    ],
    date: '2025-01-13',
    lastMessage: '뭔가 화나는 일이 있었나?'
  },
  {
    id: '4',
    characterId: '4',
    characterName: '무서미',
    characterAvatar: '😱',
    messages: [
      {
        id: '1',
        type: 'assistant',
        content: '불안한 마음이 있나요? 천천히 말해보세요.',
        timestamp: '2025-01-12 09:15:00'
      },
      {
        id: '2',
        type: 'user',
        content: '새로운 환경에 적응하기가 어려워요',
        timestamp: '2025-01-12 09:16:00'
      },
      {
        id: '3',
        type: 'assistant',
        content: '변화는 누구에게나 두려운 일이에요. 하지만 당신은 해낼 수 있어요.',
        timestamp: '2025-01-12 09:17:00'
      }
    ],
    date: '2025-01-12',
    lastMessage: '변화는 누구에게나 두려운 일이에요. 하지만 당신은 해낼 수 있어요.'
  },
  {
    id: '5',
    characterId: '5',
    characterName: '까칠이',
    characterAvatar: '😏',
    messages: [
      {
        id: '1',
        type: 'assistant',
        content: '뭐가 그렇게 답답해? 솔직히 말해봐.',
        timestamp: '2025-01-11 18:30:00'
      },
      {
        id: '2',
        type: 'user',
        content: '친구들이 제 이야기를 안 들어줘요',
        timestamp: '2025-01-11 18:31:00'
      },
      {
        id: '3',
        type: 'assistant',
        content: '그럼 너부터 다른 사람 이야기 제대로 들어줬어? 먼저 돌아보자.',
        timestamp: '2025-01-11 18:32:00'
      }
    ],
    date: '2025-01-11',
    lastMessage: '그럼 너부터 다른 사람 이야기 제대로 들어줬어? 먼저 돌아보자.'
  },
  {
    id: '6',
    characterId: '1',
    characterName: '기쁨이',
    characterAvatar: '😊',
    messages: [
      {
        id: '1',
        type: 'assistant',
        content: '오늘은 특별한 일이 있었나요? 좋은 일이든 나쁜 일이든 들어볼게요!',
        timestamp: '2025-01-10 15:20:00'
      },
      {
        id: '2',
        type: 'user',
        content: '프로젝트가 성공적으로 끝났어요!',
        timestamp: '2025-01-10 15:21:00'
      },
      {
        id: '3',
        type: 'assistant',
        content: '와! 정말 축하해요! 그 기쁨을 함께 나눠서 기뻐요!',
        timestamp: '2025-01-10 15:22:00'
      }
    ],
    date: '2025-01-10',
    lastMessage: '와! 정말 축하해요! 그 기쁨을 함께 나눠서 기뻐요!'
  },
  {
    id: '7',
    characterId: '3',
    characterName: '슬픔이',
    characterAvatar: '😢',
    messages: [
      {
        id: '1',
        type: 'assistant',
        content: '힘든 하루였구나... 천천히 털어놔도 괜찮아.',
        timestamp: '2025-01-09 21:00:00'
      },
      {
        id: '2',
        type: 'user',
        content: '가족과 갈등이 있었어요',
        timestamp: '2025-01-09 21:01:00'
      },
      {
        id: '3',
        type: 'assistant',
        content: '가족과의 갈등은 특히 마음이 아프지... 시간이 해결해줄 거야.',
        timestamp: '2025-01-09 21:02:00'
      }
    ],
    date: '2025-01-09',
    lastMessage: '가족과의 갈등은 특히 마음이 아프지... 시간이 해결해줄 거야.'
  },
  {
    id: '8',
    characterId: '2',
    characterName: '버럭이',
    characterAvatar: '😤',
    messages: [
      {
        id: '1',
        type: 'assistant',
        content: '또 화나는 일이 있었어? 다 털어놔!',
        timestamp: '2025-01-08 13:45:00'
      },
      {
        id: '2',
        type: 'user',
        content: '교통 체증 때문에 약속에 늦었어요',
        timestamp: '2025-01-08 13:46:00'
      },
      {
        id: '3',
        type: 'assistant',
        content: '아, 그거 정말 짜증나지! 하지만 이미 지나간 일이니까 다음엔 미리 출발하자.',
        timestamp: '2025-01-08 13:47:00'
      }
    ],
    date: '2025-01-08',
    lastMessage: '아, 그거 정말 짜증나지! 하지만 이미 지나간 일이니까 다음엔 미리 출발하자.'
  },
  {
    id: '9',
    characterId: '4',
    characterName: '무서미',
    characterAvatar: '😱',
    messages: [
      {
        id: '1',
        type: 'assistant',
        content: '걱정이 많아 보이네... 무엇이 불안한가요?',
        timestamp: '2025-01-07 11:30:00'
      },
      {
        id: '2',
        type: 'user',
        content: '내일 면접이 있어서 너무 떨려요',
        timestamp: '2025-01-07 11:31:00'
      },
      {
        id: '3',
        type: 'assistant',
        content: '면접 전 긴장은 자연스러운 거예요. 깊게 숨을 쉬고 준비한 걸 믿어보세요.',
        timestamp: '2025-01-07 11:32:00'
      }
    ],
    date: '2025-01-07',
    lastMessage: '면접 전 긴장은 자연스러운 거예요. 깊게 숨을 쉬고 준비한 걸 믿어보세요.'
  },
  {
    id: '10',
    characterId: '1',
    characterName: '기쁨이',
    characterAvatar: '😊',
    messages: [
      {
        id: '1',
        type: 'assistant',
        content: '안녕하세요! 새해 첫 대화네요. 올해 목표가 있나요?',
        timestamp: '2025-01-06 10:00:00'
      },
      {
        id: '2',
        type: 'user',
        content: '건강한 생활 습관 만들기가 목표예요',
        timestamp: '2025-01-06 10:01:00'
      },
      {
        id: '3',
        type: 'assistant',
        content: '정말 좋은 목표네요! 작은 것부터 시작해보세요. 응원할게요!',
        timestamp: '2025-01-06 10:02:00'
      }
    ],
    date: '2025-01-06',
    lastMessage: '정말 좋은 목표네요! 작은 것부터 시작해보세요. 응원할게요!'
  },
  {
    id: '11',
    characterId: '3',
    characterName: '슬픔이',
    characterAvatar: '😢',
    messages: [
      {
        id: '1',
        type: 'assistant',
        content: '연말이라 더 외로워지는 마음... 이해해.',
        timestamp: '2024-12-31 23:30:00'
      },
      {
        id: '2',
        type: 'user',
        content: '혼자 보내는 연말이 쓸쓸해요',
        timestamp: '2024-12-31 23:31:00'
      },
      {
        id: '3',
        type: 'assistant',
        content: '혼자라고 해서 외로운 건 아니야... 나도 여기 있잖아.',
        timestamp: '2024-12-31 23:32:00'
      }
    ],
    date: '2024-12-31',
    lastMessage: '혼자라고 해서 외로운 건 아니야... 나도 여기 있잖아.'
  },
  {
    id: '12',
    characterId: '5',
    characterName: '까칠이',
    characterAvatar: '😏',
    messages: [
      {
        id: '1',
        type: 'assistant',
        content: '연말 결산이라고 우울해하지 말고, 내년에 뭘 할 건지 생각해봐.',
        timestamp: '2024-12-30 16:15:00'
      },
      {
        id: '2',
        type: 'user',
        content: '올해 계획했던 걸 못 이뤄서 아쉬워요',
        timestamp: '2024-12-30 16:16:00'
      },
      {
        id: '3',
        type: 'assistant',
        content: '그럼 왜 못 이뤘는지 분석해보고, 내년엔 제대로 해봐. 후회만 해봤자 소용없어.',
        timestamp: '2024-12-30 16:17:00'
      }
    ],
    date: '2024-12-30',
    lastMessage: '그럼 왜 못 이뤘는지 분석해보고, 내년엔 제대로 해봐. 후회만 해봤자 소용없어.'
  },
  {
    id: '13',
    characterId: '2',
    characterName: '버럭이',
    characterAvatar: '😤',
    messages: [
      {
        id: '1',
        type: 'assistant',
        content: '연말 회식에서 스트레스 받았어? 말해봐!',
        timestamp: '2024-12-29 20:30:00'
      },
      {
        id: '2',
        type: 'user',
        content: '상사가 너무 무리한 요구를 했어요',
        timestamp: '2024-12-29 20:31:00'
      },
      {
        id: '3',
        type: 'assistant',
        content: '아! 그런 상사 정말 화나네! 하지만 직접 부딪치기보다는 현명하게 대처하자.',
        timestamp: '2024-12-29 20:32:00'
      }
    ],
    date: '2024-12-29',
    lastMessage: '아! 그런 상사 정말 화나네! 하지만 직접 부딪치기보다는 현명하게 대처하자.'
  },
  {
    id: '14',
    characterId: '4',
    characterName: '무서미',
    characterAvatar: '😱',
    messages: [
      {
        id: '1',
        type: 'assistant',
        content: '연말 모임들이 부담스러우신가요?',
        timestamp: '2024-12-28 14:20:00'
      },
      {
        id: '2',
        type: 'user',
        content: '사람들 만나는 게 점점 어려워져요',
        timestamp: '2024-12-28 14:21:00'
      },
      {
        id: '3',
        type: 'assistant',
        content: '사회적 불안감은 많은 사람들이 경험해요. 천천히 연습해보면 괜찮아질 거예요.',
        timestamp: '2024-12-28 14:22:00'
      }
    ],
    date: '2024-12-28',
    lastMessage: '사회적 불안감은 많은 사람들이 경험해요. 천천히 연습해보면 괜찮아질 거예요.'
  },
  {
    id: '15',
    characterId: '1',
    characterName: '기쁨이',
    characterAvatar: '😊',
    messages: [
      {
        id: '1',
        type: 'assistant',
        content: '크리스마스 잘 보내셨나요? 선물은 뭘 받으셨어요?',
        timestamp: '2024-12-27 12:00:00'
      },
      {
        id: '2',
        type: 'user',
        content: '가족들과 함께 따뜻한 시간을 보냈어요',
        timestamp: '2024-12-27 12:01:00'
      },
      {
        id: '3',
        type: 'assistant',
        content: '와! 그런 시간이 가장 소중한 선물이죠! 정말 기뻐요!',
        timestamp: '2024-12-27 12:02:00'
      }
    ],
    date: '2024-12-27',
    lastMessage: '와! 그런 시간이 가장 소중한 선물이죠! 정말 기뻐요!'
  }
];

export const mockTestResults: TestResult[] = [
  {
    id: '1',
    testType: 'HTP',
    result: '슬픔이',
    characterMatch: '슬픔이',
    date: '2025-01-15',
    description: '집, 나무, 사람 그림을 통한 심리 분석 결과, 현재 내면의 슬픔과 고독감이 강하게 드러났습니다. 하지만 이는 일시적인 감정으로, 적절한 상담과 관리를 통해 극복할 수 있습니다.',
    images: ['house.jpg', 'tree.jpg', 'person.jpg']
  },
  {
    id: '2',
    testType: 'Drawing',
    result: '기쁨이',
    characterMatch: '기쁨이',
    date: '2025-01-10',
    description: '자유 그림 검사 결과, 밝고 긍정적인 에너지가 느껴집니다. 색채 사용과 구도에서 안정감과 희망이 표현되었습니다.',
    images: ['drawing1.jpg']
  },
  {
    id: '3',
    testType: 'HTP',
    result: '기쁨이',
    characterMatch: '기쁨이',
    date: '2025-01-05',
    description: '이전 검사 대비 심리적 안정감이 크게 향상되었습니다. 특히 집 그림에서 따뜻함과 안정감이 잘 표현되었습니다.',
    images: ['house2.jpg', 'tree2.jpg', 'person2.jpg']
  },
  {
    id: '4',
    testType: 'HTP',
    result: '무서미',
    characterMatch: '무서미',
    date: '2025-01-03',
    description: '나무 그림 검사에서 불안감과 걱정이 많이 드러났습니다. 가지의 형태와 색채에서 내면의 두려움이 표현되었으나, 뿌리가 튼튼하게 그려져 기본적인 안정감은 있습니다.',
    images: ['tree_test.jpg']
  },
  {
    id: '5',
    testType: 'HTP',
    result: '버럭이',
    characterMatch: '버럭이',
    date: '2024-12-30',
    description: '그림에서 강한 에너지와 역동성이 느껴집니다. 색채 사용이 강렬하고 선이 굵어 감정 표현이 직접적입니다. 분노를 건설적으로 표현하는 방법을 찾아보세요.',
    images: ['house3.jpg', 'tree3.jpg', 'person3.jpg']
  },
  {
    id: '6',
    testType: 'Drawing',
    result: '까칠이',
    characterMatch: '까칠이',
    date: '2024-12-25',
    description: '자유 그림에서 비판적이고 분석적인 성향이 드러났습니다. 세밀한 표현과 현실적인 묘사가 특징이며, 완벽주의적 성향이 보입니다.',
    images: ['free_drawing2.jpg']
  },
  {
    id: '7',
    testType: 'HTP',
    result: '기쁨이',
    characterMatch: '기쁨이',
    date: '2024-12-20',
    description: '사람 그림에서 밝고 긍정적인 에너지가 느껴집니다. 표정과 자세에서 자신감과 활력이 잘 표현되었습니다.',
    images: ['person_test.jpg']
  },
  {
    id: '8',
    testType: 'HTP',
    result: '슬픔이',
    characterMatch: '슬픔이',
    date: '2024-12-15',
    description: '전반적으로 어두운 색채와 작은 크기의 그림이 특징입니다. 내면의 위축감과 우울감이 표현되었으나, 섬세한 표현력은 뛰어납니다.',
    images: ['house4.jpg', 'tree4.jpg', 'person4.jpg']
  },
  {
    id: '9',
    testType: 'Drawing',
    result: '무서미',
    characterMatch: '무서미',
    date: '2024-12-10',
    description: '불안정한 선과 흐린 색채가 특징적입니다. 미래에 대한 불안감과 걱정이 많이 드러나지만, 세심한 부분까지 신경 쓰는 모습이 보입니다.',
    images: ['anxiety_drawing.jpg']
  },
  {
    id: '10',
    testType: 'HTP',
    result: '기쁨이',
    characterMatch: '기쁨이',
    date: '2024-12-05',
    description: '집 그림에서 따뜻함과 안정감이 잘 표현되었습니다. 창문이 많고 밝은 색채를 사용하여 개방적이고 긍정적인 성향을 보입니다.',
    images: ['house_test.jpg']
  },
  {
    id: '11',
    testType: 'HTP',
    result: '버럭이',
    characterMatch: '버럭이',
    date: '2024-11-30',
    description: '강렬한 선과 진한 색채가 특징입니다. 감정 표현이 직접적이고 솔직하며, 에너지가 넘치는 성향이 드러납니다.',
    images: ['house5.jpg', 'tree5.jpg', 'person5.jpg']
  },
  {
    id: '12',
    testType: 'Drawing',
    result: '까칠이',
    characterMatch: '까칠이',
    date: '2024-11-25',
    description: '정교하고 세밀한 그림이 특징입니다. 현실적이고 논리적인 사고방식이 잘 드러나며, 완벽을 추구하는 성향이 보입니다.',
    images: ['detailed_drawing.jpg']
  },
  {
    id: '13',
    testType: 'HTP',
    result: '슬픔이',
    characterMatch: '슬픔이',
    date: '2024-11-20',
    description: '나무 그림이 작고 외로워 보입니다. 가지가 아래로 처져있고 색채가 어두워 우울감이 드러나지만, 뿌리는 깊게 그려져 내면의 힘이 있습니다.',
    images: ['sad_tree.jpg']
  },
  {
    id: '14',
    testType: 'HTP',
    result: '무서미',
    characterMatch: '무서미',
    date: '2024-11-15',
    description: '사람 그림에서 위축되고 불안한 모습이 드러납니다. 표정이 불안해 보이고 자세가 경직되어 있어 긴장감이 느껴집니다.',
    images: ['anxious_person.jpg']
  },
  {
    id: '15',
    testType: 'HTP',
    result: '기쁨이',
    characterMatch: '기쁨이',
    date: '2024-11-10',
    description: '전체적으로 밝고 활기찬 그림입니다. 색채가 선명하고 구도가 안정적이며, 긍정적인 에너지가 잘 표현되었습니다.',
    images: ['happy_house.jpg', 'happy_tree.jpg', 'happy_person.jpg']
  },
  {
    id: '16',
    testType: 'Drawing',
    result: '버럭이',
    characterMatch: '버럭이',
    date: '2024-11-05',
    description: '역동적이고 강한 에너지가 느껴지는 그림입니다. 붓 터치가 강하고 색채가 선명하여 열정적인 성향이 드러납니다.',
    images: ['dynamic_drawing.jpg']
  },
  {
    id: '17',
    testType: 'HTP',
    result: '까칠이',
    characterMatch: '까칠이',
    date: '2024-10-30',
    description: '집 그림이 매우 정교하고 세밀합니다. 모든 부분이 완벽하게 그려져 있어 꼼꼼하고 완벽주의적인 성향이 잘 드러납니다.',
    images: ['perfect_house.jpg']
  },
  {
    id: '18',
    testType: 'HTP',
    result: '슬픔이',
    characterMatch: '슬픔이',
    date: '2024-10-25',
    description: '전반적으로 어둡고 소극적인 표현이 특징입니다. 그림 크기가 작고 색채가 단조로워 내성적이고 우울한 감정이 드러납니다.',
    images: ['dark_house.jpg', 'dark_tree.jpg', 'dark_person.jpg']
  },
  {
    id: '19',
    testType: 'HTP',
    result: '무서미',
    characterMatch: '무서미',
    date: '2024-10-20',
    description: '나무가 구부러져 있고 잎이 떨어지는 모습이 그려져 있습니다. 변화와 상실에 대한 불안감이 표현되었으나, 새싹도 함께 그려져 희망도 보입니다.',
    images: ['worried_tree.jpg']
  },
  {
    id: '20',
    testType: 'Drawing',
    result: '기쁨이',
    characterMatch: '기쁨이',
    date: '2024-10-15',
    description: '밝고 화사한 색채의 자유 그림입니다. 꽃과 나비 등 긍정적인 소재들이 많이 등장하며, 희망적이고 낙관적인 성향이 드러납니다.',
    images: ['bright_drawing.jpg']
  }
];

export const mockUserProfile: UserProfile = {
  id: '1',
  name: '김철수',
  email: 'kimcs@example.com',
  joinDate: '2024-01-01',
  totalTests: 20,
  totalChats: 45
};