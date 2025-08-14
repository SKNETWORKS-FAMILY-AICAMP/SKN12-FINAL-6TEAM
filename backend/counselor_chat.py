#!/usr/bin/env python3
"""
원본 프롬프트 기반 상담 챗봇
- prompts/type_1.md 파일 내용을 그대로 활용
- 4번/5번 유형 구분 유지
- 메모리 관리 20개 한도
- 히스토리 및 컨텍스트 추적
- 자연스러운 대화 흐름 개선
"""

import os
import re
import json
from typing import List, Dict, Any
from datetime import datetime
import pytz
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# 환경 변수 로드
load_dotenv()

class ConversationMemory:
    """대화 메모리 관리 클래스"""
    
    def __init__(self, max_messages: int = 20):
        self.max_messages = max_messages
        self.messages: List[Dict[str, Any]] = []
        self.session_info = {
            "started_at": datetime.now(pytz.timezone('Asia/Seoul')).isoformat(),
            "user_traits": [],
            "key_topics": [],
            "emotional_state": "neutral",
            "user_type": "미정"
        }
    
    def add_message(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """메시지 추가 (최대 개수 관리)"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now(pytz.timezone('Asia/Seoul')).isoformat(),
            "metadata": metadata or {}
        }
        
        self.messages.append(message)
        
        # 최대 개수 초과 시 오래된 메시지 제거 (시작 메시지는 보존)
        if len(self.messages) > self.max_messages:
            # 첫 번째 메시지(시작 인사)는 항상 유지
            preserved_first = self.messages[0]
            recent_messages = self.messages[-(self.max_messages-1):]
            self.messages = [preserved_first] + recent_messages
    
    def get_recent_context(self, count: int = 6) -> str:
        """최근 대화 컨텍스트 반환"""
        recent = self.messages[-count:] if len(self.messages) >= count else self.messages
        context_lines = []
        
        for msg in recent:
            role_name = "사용자" if msg["role"] == "user" else "마음탐구자"
            content = msg["content"][:200]  # 내용 길이 제한
            context_lines.append(f"{role_name}: {content}")
        
        return "\n".join(context_lines)
    
    def get_conversation_summary(self) -> str:
        """대화 요약 생성"""
        if len(self.messages) < 4:
            return "대화 초기 단계"
        
        user_messages = [msg for msg in self.messages if msg["role"] == "user"]
        
        summary_parts = []
        
        # 사용자 유형
        if self.session_info["user_type"] != "미정":
            summary_parts.append(f"유형: {self.session_info['user_type']}")
        
        # 주요 주제 추출
        if self.session_info["key_topics"]:
            summary_parts.append(f"주요 주제: {', '.join(self.session_info['key_topics'])}")
        
        # 메시지 수
        summary_parts.append(f"대화 메시지: {len(user_messages)}개")
        
        return " | ".join(summary_parts)
    
    def update_session_info(self, key: str, value: Any):
        """세션 정보 업데이트"""
        if key in self.session_info:
            if isinstance(self.session_info[key], list):
                if value not in self.session_info[key]:
                    self.session_info[key].append(value)
            else:
                self.session_info[key] = value
    
    def get_message_count_by_role(self, role: str) -> int:
        """역할별 메시지 수 반환"""
        return len([msg for msg in self.messages if msg["role"] == role])

class PromptCounselor:
    """원본 프롬프트 기반 상담 챗봇"""
    
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
        self.memory = ConversationMemory(max_messages=20)
        self.prompts = self._load_original_prompts()
        self.conversation_stage = "START"
        
        # 대화 단계 정의
        self.stages = {
            "START": "시작",
            "CLASSIFY": "유형분류",
            "EXPLORE": "탐색", 
            "SOLUTION": "솔루션",
            "WRAP_UP": "마무리",
            "FREE_CHAT": "자유대화"
        }
        
        print(f"✅ 원본 프롬프트 기반 상담 챗봇 초기화 완료 (메모리: {self.memory.max_messages}개)")
    
    def _load_original_prompts(self) -> Dict[str, str]:
        """원본 MD 파일에서 프롬프트를 그대로 로드"""
        try:
            with open("./prompts/type_1.md", 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 정확한 섹션 매칭을 위한 정규식
            sections = {
                'persona': r"### \*\*챗봇 페르소나 .*?\*\*(.*?)---",
                'start_message': r"\*\*\(1단계: 시작 및 유형 확인\)\*\*(.*?)\*\*\(2단계:",
                'type_4_stress_prompt': r"\*\*\[만약 사용자가 공허함.*?\]\*\*(.*?)\*\*\[만약 사용자가 정신적 피로",
                'type_5_stress_prompt': r"\*\*\[만약 사용자가 정신적 피로.*?\]\*\*(.*?)\*\*\(3단계:",
                'type_4_solution_prompt': r"\*\*\[4번 유형의 감정적 소용돌이에 대한 솔루션\]\*\*(.*?)\*\*\[5번 유형",
                'type_5_solution_prompt': r"\*\*\[5번 유형의 고립/탐욕에 대한 솔루션\]\*\*(.*?)\*\*\(4-1단계:",
                'wrap_up_prompt': r"\*\*\(4-1단계: 마무리 및 격려\)\*\*(.*)"
            }
            
            prompts = {}
            for key, pattern in sections.items():
                match = re.search(pattern, content, re.DOTALL)
                if match:
                    prompts[key] = match.group(1).strip().strip('"')
                    print(f"✅ {key} 프롬프트 로드 완료")
                else:
                    print(f"⚠️ {key} 프롬프트 로드 실패")
            
            return prompts
            
        except Exception as e:
            print(f"❌ 프롬프트 로드 오류: {e}")
            return self._get_default_prompts()
    
    def _get_default_prompts(self) -> Dict[str, str]:
        """기본 프롬프트 반환"""
        return {
            'persona': "차분하고 사려 깊은 마음탐구자로서 사용자의 복잡한 감정과 생각을 존중하며 대화합니다.",
            'start_message': "안녕하세요. 저는 당신의 특별한 내면세계를 함께 탐험할 '마음탐구자'예요. 오늘은 어떤 마음에 대해 더 깊이 들여다보고 싶으신가요?",
            'type_4_stress_prompt': "감정적 깊이와 특별함에 대한 갈망에 대해 더 이야기해볼까요?",
            'type_5_stress_prompt': "지적 탐구와 에너지 관리에 대해 더 깊이 들어가볼까요?",
            'type_4_solution_prompt': "감정적 창조성을 통한 해결 방법을 제안드릴게요.",
            'type_5_solution_prompt': "지혜롭고 체계적인 접근 방법을 함께 찾아보겠습니다.",
            'wrap_up_prompt': "오늘 나눈 이야기가 당신에게 도움이 되길 바라요. 언제든 다시 찾아주세요."
        }
    
    def start_session(self) -> str:
        """세션 시작"""
        start_message = self.prompts.get('start_message', '상담을 시작합니다.')
        
        # 메모리에 시작 메시지 추가
        self.memory.add_message("assistant", start_message, {
            "stage": "START",
            "message_type": "greeting"
        })
        
        self.conversation_stage = "CLASSIFY"
        return start_message
    
    def classify_user_type(self, user_message: str) -> str:
        """사용자 유형 분류 (원본 로직)"""
        try:
            # AI를 통한 유형 분류
            classification_prompt = ChatPromptTemplate.from_messages([
                ("system", f"""
{self.prompts.get('persona')}

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
            
            chain = classification_prompt | self.llm
            response = chain.invoke({})
            
            # 분류 결과에 따른 다음 프롬프트 결정
            if "4번 유형" in response.content:
                user_type = "4번 유형"
                next_prompt = self.prompts['type_4_stress_prompt']
                self.memory.update_session_info("user_type", "4번 유형")
            else:
                user_type = "5번 유형"
                next_prompt = self.prompts['type_5_stress_prompt']
                self.memory.update_session_info("user_type", "5번 유형")
            
            self.conversation_stage = "EXPLORE"
            
            return next_prompt
            
        except Exception as e:
            print(f"유형 분류 오류: {e}")
            # 기본값으로 4번 유형 설정
            self.memory.update_session_info("user_type", "4번 유형")
            self.conversation_stage = "EXPLORE"
            return self.prompts['type_4_stress_prompt']
    
    def provide_solution(self) -> str:
        """유형별 솔루션 제공 (원본 로직)"""
        user_type = self.memory.session_info.get("user_type", "4번 유형")
        
        if user_type == "4번 유형":
            solution = self.prompts.get('type_4_solution_prompt')
        else:
            solution = self.prompts.get('type_5_solution_prompt')
        
        self.conversation_stage = "WRAP_UP"
        return solution
    
    def _should_continue_conversation(self, user_message: str) -> bool:
        """대화 계속 여부 판단 (개선된 로직)"""
        # 1. 명시적인 계속 요청 키워드
        continue_keywords = ['대화', '더', '계속', '이야기', '말하고', '말해도', '말했으면', '얘기', '물어봐도']
        
        # 2. 질문 패턴 (물음표나 의문문)
        question_patterns = ['?', '까', '해결', '어떻게', '방법', '가능', '될까', '어떨까', '그림', '창의']
        
        # 3. 관심 표현 키워드
        interest_keywords = ['흥미', '궁금', '알고싶', '더 자세히', '구체적으로']
        
        # 4. 구체적인 해결책 질문
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
    
    def wrap_up_conversation(self, user_message: str) -> str:
        """대화 마무리 또는 계속 결정"""
        # 사용자가 대화를 계속하고 싶어하는지 판단
        if self._should_continue_conversation(user_message):
            # 자유 대화로 전환하여 구체적인 응답 제공
            self.conversation_stage = "FREE_CHAT"
            return self.free_conversation(user_message)
        else:
            # 마무리 메시지 제공
            self.conversation_stage = "FREE_CHAT"
            return self.prompts.get('wrap_up_prompt')
    
    def free_conversation(self, user_message: str) -> str:
        """자유 대화 - 컨텍스트 고려"""
        try:
            # 대화 계속 의사 감지 (일반적인 경우)
            if self._should_continue_conversation(user_message) and len(user_message) < 15 and not any(word in user_message for word in ['그림', '해결', '방법']):
                return self._generate_continue_response()
            
            # 구체적인 해결책 질문에 대한 특별 처리
            if any(keyword in user_message for keyword in ['그림그리기', '그림', '창의', '표현', '해결']):
                return self._handle_specific_solution_question(user_message)
            
            # 일반 자유 대화
            recent_context = self.memory.get_recent_context(8)
            conversation_summary = self.memory.get_conversation_summary()
            user_type = self.memory.session_info.get("user_type", "미정")
            
            # 이전 대화 참조 확인
            previous_references = self._extract_previous_references(user_message)
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", f"""
{self.prompts.get('persona')}

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
            
            chain = prompt | self.llm
            response = chain.invoke({})
            return response.content
            
        except Exception as e:
            print(f"자유 대화 오류: {e}")
            return "그 마음을 충분히 이해해요. 더 자세히 말씀해 주시겠어요?"
    
    def _handle_specific_solution_question(self, user_message: str) -> str:
        """구체적인 해결책 질문에 대한 응답"""
        user_type = self.memory.session_info.get("user_type", "미정")
        
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
    
    def _generate_continue_response(self) -> str:
        """대화 계속 요청에 대한 응답"""
        user_type = self.memory.session_info.get("user_type", "미정")
        key_topics = self.memory.session_info.get('key_topics', [])
        
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
    
    def _update_emotional_state(self, message: str):
        """메시지에서 감정 상태 추출 및 업데이트"""
        emotional_keywords = {
            "positive": ["행복", "좋아", "기뻐", "만족", "편안", "안정"],
            "negative": ["힘들어", "우울", "슬퍼", "화나", "답답", "불안"],
            "complex": ["복잡", "혼란", "애매", "모호", "갈등"]
        }
        
        for state, keywords in emotional_keywords.items():
            if any(keyword in message for keyword in keywords):
                self.memory.update_session_info("emotional_state", state)
                break
    
    def _extract_key_topics(self, message: str):
        """주요 주제 추출"""
        topic_keywords = {
            "relationship": ["관계", "사람", "친구", "가족", "연인"],
            "work": ["일", "직장", "업무", "공부", "학교"],
            "emotion": ["감정", "마음", "기분", "느낌"],
            "thinking": ["생각", "사고", "고민", "분석", "판단"],
            "creativity": ["창의", "예술", "창작", "표현", "그림"],
            "energy": ["에너지", "피로", "지침", "활력"]
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in message for keyword in keywords):
                self.memory.update_session_info("key_topics", topic)
    
    def process_message(self, user_message: str) -> str:
        """메시지 처리 - 개선된 단계 플로우"""
        try:
            # 사용자 메시지를 메모리에 추가
            self.memory.add_message("user", user_message, {
                "stage": self.conversation_stage,
                "timestamp": datetime.now(pytz.timezone('Asia/Seoul')).isoformat()
            })
            
            # 감정 상태 및 주요 주제 업데이트
            self._update_emotional_state(user_message)
            self._extract_key_topics(user_message)
            
            # 현재 단계에 따른 응답 생성
            user_message_count = self.memory.get_message_count_by_role("user")
            
            if self.conversation_stage == "CLASSIFY":
                response = self.classify_user_type(user_message)
            elif self.conversation_stage == "EXPLORE":
                response = self.provide_solution()
            elif self.conversation_stage == "WRAP_UP":
                response = self.wrap_up_conversation(user_message)
            elif self.conversation_stage == "FREE_CHAT":
                response = self.free_conversation(user_message)
            else:
                response = self.classify_user_type(user_message)
            
            # 응답을 메모리에 추가
            self.memory.add_message("assistant", response, {
                "stage": self.conversation_stage,
                "user_type": self.memory.session_info.get("user_type"),
                "response_type": "original_prompt"
            })
            
            return response
            
        except Exception as e:
            print(f"메시지 처리 오류: {e}")
            error_response = "죄송합니다. 잠시 문제가 발생했어요. 다시 말씀해 주시겠어요?"
            self.memory.add_message("assistant", error_response, {"error": True})
            return error_response
    
    def get_conversation_stats(self) -> Dict[str, Any]:
        """대화 통계 반환"""
        return {
            "total_messages": len(self.memory.messages),
            "user_messages": self.memory.get_message_count_by_role("user"),
            "assistant_messages": self.memory.get_message_count_by_role("assistant"),
            "current_stage": self.conversation_stage,
            "stage_name": self.stages.get(self.conversation_stage, "알 수 없음"),
            "session_info": self.memory.session_info,
            "memory_capacity": f"{len(self.memory.messages)}/{self.memory.max_messages}"
        }
    
    def export_conversation(self) -> str:
        """대화 내용 내보내기"""
        export_data = {
            "session_info": self.memory.session_info,
            "conversation_stats": self.get_conversation_stats(),
            "messages": self.memory.messages
        }
        return json.dumps(export_data, ensure_ascii=False, indent=2)

def run_original_prompt_counselor():
    """원본 프롬프트 기반 상담 챗봇 실행"""
    print("🤖 원본 프롬프트 기반 상담 챗봇을 시작합니다...")
    print("📝 prompts/type_1.md 파일 내용을 그대로 활용")
    print("💾 메모리 관리: 최대 20개 메시지 유지")
    print("🔀 4번/5번 유형 구분 및 맞춤 상담\n")
    
    try:
        if not os.getenv("OPENAI_API_KEY"):
            print("❌ OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
            return
        
        # 챗봇 초기화
        counselor = PromptCounselor()
        
        # 세션 시작
        start_message = counselor.start_session()
        print(f"마음탐구자: {start_message}\n")
        
        # 대화 루프
        while True:
            try:
                user_input = input("나: ").strip()
                
                # 특수 명령어 처리
                if user_input.lower() in ["exit", "quit", "종료", "그만", "끝"]:
                    print("\n마음탐구자: 당신의 내면 여행이 계속되길 바라요. 🌟")
                    break
                elif user_input.lower() in ["stats", "통계"]:
                    stats = counselor.get_conversation_stats()
                    print(f"\n📊 대화 통계:")
                    print(f"   현재 단계: {stats['stage_name']}")
                    print(f"   사용자 유형: {stats['session_info']['user_type']}")
                    print(f"   메모리 사용량: {stats['memory_capacity']}")
                    print(f"   주요 주제: {', '.join(stats['session_info']['key_topics'])}")
                    print(f"   감정 상태: {stats['session_info']['emotional_state']}\n")
                    continue
                elif user_input.lower() in ["export", "내보내기"]:
                    export_data = counselor.export_conversation()
                    print(f"\n📄 대화 내용이 준비되었습니다. (총 {len(export_data)} 문자)\n")
                    continue
                
                if not user_input:
                    print("마음탐구자: 편하게 마음을 나누어 주세요.")
                    continue
                
                # 응답 생성
                response = counselor.process_message(user_input)
                print(f"\n마음탐구자: {response}\n")
                
                # 간단한 상태 표시
                stats = counselor.get_conversation_stats()
                print(f"--- {stats['stage_name']} 단계 | {stats['session_info']['user_type']} | 메모리: {stats['memory_capacity']} ---\n")
                
            except EOFError:
                print("\n\n마음탐구자: 대화가 종료되었습니다. 🙏")
                break
            except KeyboardInterrupt:
                print("\n\n마음탐구자: 안녕히 가세요. 🌟")
                break
                
    except Exception as e:
        print(f"❌ 실행 오류: {e}")

if __name__ == "__main__":
    run_original_prompt_counselor()