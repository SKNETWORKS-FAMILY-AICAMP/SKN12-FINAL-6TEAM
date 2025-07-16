import os
from typing import Dict, Any, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from .chat_service import ChatService, ConversationMemory
from ..models.chat import ChatSession, ChatMessage
from pydantic import SecretStr
from dotenv import load_dotenv
load_dotenv()
# AI 서비스 이부분 전폭 수정해야함 지금은 프로토 타입이라서 ai에 맡긴거
# OPENAPIKEY 생성 
api_key_str = os.getenv("OPENAI_API_KEY")
OPENAI_API_KEY = SecretStr(api_key_str) if api_key_str is not None else None

class AIService:
    """OpenAI API 연동 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
        self.chat_service = ChatService(db)
        
        # OpenAI API 키가 있으면 실제 LLM 사용, 없으면 Mock 사용
        if OPENAI_API_KEY and str(OPENAI_API_KEY) != "None":
            self.llm = ChatOpenAI(model="gpt-4o", api_key=OPENAI_API_KEY, 
                                    temperature=0.7)
            self.use_mock = False
        else:
            self.llm = None
            self.use_mock = True
            print("OpenAI API 키가 없어 Mock AI 서비스를 사용합니다.")
    
    def classify_user_type(self, session_id: UUID, user_message: str) -> Tuple[str, str]:
        """사용자 유형 분류"""
        try:
            # AI를 통한 유형 분류
            classification_prompt = ChatPromptTemplate.from_messages([
                ("system", f"""
        {self.chat_service.prompts.get('persona')}

        사용자의 응답을 분석하여 에니어그램 4번 유형과 5번 유형 중 어디에 더 가까운지 판단하세요.

        **4번 유형 특징:**
        - 공허함, 우울감, 타인과의 비교로 인한 고통
        - 외로움, 결핍감, 슬픔, 수치심
        - 감정의 파도, 특별함에 대한 갈망

        **5번 유형 특징:**
        - 정신적 피로, 고갈감, 단절감
        - 압박감, 지식 탐닉, 행동 주저
        - 생각 과잉, 에너지 보존 욕구

        사용자의 메시지를 분석하고 "4번 유형" 또는 "5번 유형" 중 하나로만 답변하세요.
        """),
                ("human", f"사용자 메시지: {user_message}")
            ])
            
            if self.use_mock:
                # Mock 분류 로직
                emotional_keywords = ["슬퍼", "우울", "외로", "특별", "감정", "마음"]
                if any(keyword in user_message for keyword in emotional_keywords):
                    response_content = "4번 유형"
                else:
                    response_content = "5번 유형"
            else:
                chain = classification_prompt | self.llm
                response = chain.invoke({})
                response_content = response.content
            
            # 분류 결과에 따른 다음 프롬프트 결정
            if "4번 유형" in response_content:
                user_type = "4번 유형"
                next_prompt = self.chat_service.prompts['type_4_stress_prompt']
            else:
                user_type = "5번 유형"
                next_prompt = self.chat_service.prompts['type_5_stress_prompt']
            
            # 세션 업데이트 (conversation_stage 제거됨)
            
            return user_type, next_prompt
            
        except Exception as e:
            print(f"유형 분류 오류: {e}")
            # 기본값으로 4번 유형 설정
            return "4번 유형", self.chat_service.prompts['type_4_stress_prompt']
    
    def provide_solution(self, session_id: UUID) -> str:
        """유형별 솔루션 제공"""
        session = self.chat_service.get_session(session_id)
        if not session:
            return "세션을 찾을 수 없습니다."
        
        # 기본 솔루션 제공
        solution = self.chat_service.prompts.get('type_4_solution_prompt', '감정적 창조성을 통한 해결 방법을 제안드릴게요.')
        return solution
    
    def _should_continue_conversation(self, user_message: str) -> bool:
        """대화 계속 여부 판단"""
        # 명시적인 계속 요청 키워드
        continue_keywords = ['대화', '더', '계속', '이야기', '말하고', '말해도', '말했으면', '얘기', '물어봐도']
        
        # 질문 패턴 (물음표나 의문문)
        question_patterns = ['?', '까', '해결', '어떻게', '방법', '가능', '될까', '어떨까', '그림', '창의']
        
        # 관심 표현 키워드
        interest_keywords = ['흥미', '궁금', '알고싶', '더 자세히', '구체적으로']
        
        # 구체적인 해결책 질문
        solution_keywords = ['그림그리기', '음악', '운동', '명상', '산책', '글쓰기']
        
        # 키워드 체크
        has_continue_keyword = any(keyword in user_message for keyword in continue_keywords)
        has_question_pattern = any(pattern in user_message for pattern in question_patterns)
        has_interest_keyword = any(keyword in user_message for keyword in interest_keywords)
        has_solution_question = any(keyword in user_message for keyword in solution_keywords)
        
        # 짧은 메시지도 질문으로 간주
        is_short_question = len(user_message) < 20 and ('?' in user_message or has_question_pattern)
        
        # 감정 표현이나 간단한 긍정은 마무리로 간주하지 않음
        simple_responses = ['감사', '고마워', '도움이', '좋네', '그래', '네', '맞아']
        is_simple_response = any(keyword in user_message for keyword in simple_responses) and len(user_message) < 30
        
        return (has_continue_keyword or has_question_pattern or has_interest_keyword or 
                has_solution_question or is_short_question) and not is_simple_response
    
    def wrap_up_conversation(self, session_id: UUID, user_message: str) -> str:
        """대화 마무리 또는 계속 결정"""
        if self._should_continue_conversation(user_message):
            # 자유 대화로 전환
            return self.free_conversation(session_id, user_message)
        else:
            # 마무리 메시지 제공
            return self.chat_service.prompts.get('wrap_up_prompt', '오늘 나눈 이야기가 도움이 되길 바라요.')
    
    def free_conversation(self, session_id: UUID, user_message: str) -> str:
        """자유 대화 - 컨텍스트 고려"""
        try:
            session = self.chat_service.get_session(session_id)
            if not session:
                return "세션을 찾을 수 없습니다."
            
            # 대화 계속 의사 감지
            if (self._should_continue_conversation(user_message) and 
                len(user_message) < 15 and 
                not any(word in user_message for word in ['그림', '해결', '방법'])):
                return self._generate_continue_response(session_id)
            
            # 구체적인 해결책 질문에 대한 특별 처리
            if any(keyword in user_message for keyword in ['그림그리기', '그림', '창의', '표현', '해결']):
                return self._handle_specific_solution_question(session_id, user_message)
            
            # 일반 자유 대화
            memory = ConversationMemory(session_id, self.db)
            recent_context = memory.get_recent_context(8)
            conversation_summary = memory.get_conversation_summary()
            user_type = "미정"  # 기본값
            
            # 이전 대화 참조 확인
            previous_references = self._extract_previous_references(user_message)
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", f"""
            {self.chat_service.prompts.get('persona')}

            이전 대화 내용을 바탕으로 자연스럽고 연결성 있는 대화를 이어가세요.

            사용자 유형: {user_type}
            대화 요약: {conversation_summary}
            이전 대화 참조: {previous_references}

            최근 대화 내용:
            {recent_context}

            중요한 지침:
            1. 사용자가 이전에 언급한 내용을 기억하고 연결하세요
            2. "아까 말씀하신", "처음에 언급하신", "계속 언급하신" 등의 표현에 주의
            3. 유형별 특성을 고려한 구체적이고 도움이 되는 답변 제공
            4. 4줄 이내로 간결하게
            5. 공감적이고 지지적인 태도 유지
            6. 사용자의 질문에 직접적으로 답변하기
            """),
                ("human", f"사용자: {user_message}")
            ])
            
            if self.use_mock:
                # Mock 응답 생성 - 대화 맥락을 고려한 응답
                return self._generate_mock_contextual_response(recent_context, user_message)
            else:
                chain = prompt | self.llm
                response = chain.invoke({})
                return response.content
            
        except Exception as e:
            import traceback
            print(f"자유 대화 오류: {e}")
            print(f"스택 트레이스: {traceback.format_exc()}")
            return "그 마음을 충분히 이해해요. 더 자세히 말씀해 주시겠어요?"
    
    def _handle_specific_solution_question(self, session_id: UUID, user_message: str) -> str:
        """구체적인 해결책 질문에 대한 응답"""
        user_type = "미정"  # 기본값
        
        if "그림그리기" in user_message or "그림" in user_message:
            if user_type == "4번 유형":
                return "네, 그림그리기는 4번 유형에게 정말 효과적인 방법이에요! 감정을 색과 형태로 표현하면서 내면의 깊은 감정들을 해소하고, 동시에 특별함과 창의성을 발휘할 수 있어요. 특히 힘든 감정이 밀려올 때 그 감정을 그림으로 그려보시는 건 어떨까요?"
            elif user_type == "5번 유형":
                return "그림그리기는 5번 유형에게도 좋은 방법이에요! 머릿속의 복잡한 생각들을 시각적으로 정리하고, 몸을 움직여 에너지를 충전하는 동시에 창의적인 표현을 할 수 있거든요. 생각만 하지 말고 손으로 직접 그려보시면 어떨까요?"
            else:
                return "그림그리기는 정말 좋은 해결책이에요! 감정 표현과 스트레스 해소에 효과적이며, 창의성도 기를 수 있어요."
        
        if "해결" in user_message:
            return "네, 앞서 말씀드린 방법들이 도움이 될 수 있어요. 특히 어떤 부분에 대해 더 구체적으로 알고 싶으신가요?"
        
        return "구체적인 해결 방법에 대해 더 자세히 이야기해볼까요? 어떤 부분이 가장 궁금하신가요?"
    
    def _generate_continue_response(self, session_id: UUID) -> str:
        """대화 계속 요청에 대한 응답"""
        user_type = "미정"  # 기본값
        
        if user_type == "4번 유형":
            return "물론이죠! 감정이나 창의성에 대해 더 깊이 대화해볼까요? 어떤 이야기를 나누고 싶으신가요?"
        elif user_type == "5번 유형":
            return "네, 더 이야기해요! 지적 탐구나 에너지 관리에 대해 더 대화해볼까요?"
        else:
            return "좋아요! 언제든 대화하고 싶어요. 어떤 이야기를 더 나누고 싶으신가요?"
    
    def _extract_previous_references(self, user_message: str) -> str:
        """사용자 메시지에서 이전 대화 참조 추출"""
        reference_keywords = [
            "아까", "처음에", "예전에", "전에", "계속", "방금", "말씀하신", "언급하신"
        ]
        
        references = []
        for keyword in reference_keywords:
            if keyword in user_message:
                references.append(keyword)
        
        if references:
            return f"사용자가 이전 대화를 참조: {', '.join(references)}"
        return "이전 대화 참조 없음"
    
    def _generate_mock_contextual_response(self, recent_context: str, user_message: str) -> str:
        """Mock AI - 대화 맥락을 고려한 응답 생성"""
        
        print(f"Mock AI 호출됨")
        print(f"  최근 맥락: {recent_context}")
        print(f"  사용자 메시지: {user_message}")
        
        # 이전 대화에서 언급된 키워드 추출
        context_keywords = []
        if "우울" in recent_context:
            context_keywords.append("우울감")
        if "아침" in recent_context:
            context_keywords.append("아침에 일어나기")
        if "집중" in recent_context:
            context_keywords.append("집중력")
        if "일" in recent_context:
            context_keywords.append("업무")
        
        print(f"  추출된 맥락 키워드: {context_keywords}")
        
        # 사용자가 이전 대화를 참조하는지 확인
        reference_indicators = ["아까", "전에", "앞서", "말한", "언급"]
        has_reference = any(ind in user_message for ind in reference_indicators)
        
        if has_reference and context_keywords:
            # 이전 대화를 참조하는 응답
            if "우울감" in context_keywords and "집중력" in context_keywords:
                return f"아까 말씀하신 우울감이 일에도 집중하기 어렵게 만드는군요. 이런 연결고리를 인식하신 것 자체가 중요한 통찰이에요. 우울할 때 집중력이 떨어지는 것은 자연스러운 현상이랍니다."
            elif "우울감" in context_keywords:
                return f"처음에 말씀하신 우울감이 계속 마음에 남아있으시는군요. 그 감정을 더 깊이 들여다보고 싶어요."
            elif "아침에 일어나기" in context_keywords:
                return f"앞서 언급하신 아침에 일어나기 힘든 상황과 연결해서 생각해보면, 전반적인 에너지 부족을 느끼고 계신 것 같아요."
        
        # 일반적인 공감 응답
        if "힘들" in user_message or "어려워" in user_message:
            return "힘든 상황을 겪고 계시는군요. 그런 마음을 표현해주셔서 고마워요. 어떤 부분이 가장 어려우신가요?"
        elif "집중" in user_message:
            return "집중하기 어려운 상황이군요. 마음이 여러 곳에 흩어져 있는 느낌일 수 있어요. 어떤 생각들이 가장 방해가 되시나요?"
        else:
            return "그 마음을 충분히 이해해요. 더 자세히 말씀해 주시겠어요?"
    
    def process_message(self, session_id: UUID, user_message: str) -> str:
        """메시지 처리 - 대화 맥락을 고려한 자연스러운 응답"""
        try:
            session = self.chat_service.get_session(session_id)
            if not session:
                return "세션을 찾을 수 없습니다."
            
            # ConversationMemory를 통해 대화 기록 확인
            memory = ConversationMemory(session_id, self.db)
            user_message_count = memory.get_message_count_by_role("user")
            
            # 첫 번째 메시지인 경우 유형 분류 수행
            if user_message_count <= 1:
                classified_type, response = self.classify_user_type(session_id, user_message)
                print(f"사용자 유형 분류: {classified_type}")
                return response
            else:
                # 대화가 진행 중인 경우 컨텍스트를 고려한 자유 대화
                return self.free_conversation(session_id, user_message)
            
        except Exception as e:
            print(f"메시지 처리 오류: {e}")
            return "죄송합니다. 잠시 문제가 발생했어요. 다시 말씀해 주시겠어요?"