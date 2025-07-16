from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

# 채팅 세션 스키마
class ChatSessionBase(BaseModel):
    session_name: Optional[str] = Field(None, max_length=255)
    user_id: int
    friends_id: int

class ChatSessionCreate(ChatSessionBase):
    pass

class ChatSessionUpdate(BaseModel):
    session_name: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None
    user_type: Optional[str] = Field(None, max_length=20)
    conversation_stage: Optional[str] = Field(None, max_length=20)
    emotional_state: Optional[str] = Field(None, max_length=20)

class ChatSessionResponse(ChatSessionBase):
    chat_sessions_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# 채팅 메시지 스키마
class ChatMessageBase(BaseModel):
    content: str = Field(..., min_length=1)

class ChatMessageCreate(ChatMessageBase):
    sender_type: str = Field(..., pattern="^(user|assistant)$")
    message_type: Optional[str] = Field(None, max_length=50)
    user_type_detected: Optional[str] = Field(None, max_length=20)

class ChatMessageResponse(ChatMessageBase):
    chat_messages_id: UUID
    session_id: UUID
    sender_type: str
    created_at: datetime
    message_type: Optional[str] = None
    user_type_detected: Optional[str] = None
    
    class Config:
        from_attributes = True

# 채팅 세션 상세 정보 (메시지 포함)
class ChatSessionDetailResponse(ChatSessionResponse):
    messages: List[ChatMessageResponse] = []

# 메시지 전송 요청
class SendMessageRequest(BaseModel):
    content: str = Field(..., min_length=1)
    enable_tts: Optional[bool] = False
    voice_type: Optional[str] = None

# 메시지 전송 응답
class SendMessageResponse(BaseModel):
    user_message: ChatMessageResponse
    assistant_message: ChatMessageResponse
    session_updated: bool = False

# 채팅 세션 통계
class ChatSessionStats(BaseModel):
    total_messages: int
    user_messages: int
    assistant_messages: int
    current_stage: str
    stage_name: str
    session_info: Dict[str, Any]
    memory_capacity: str

# 에러 응답
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    code: Optional[int] = None