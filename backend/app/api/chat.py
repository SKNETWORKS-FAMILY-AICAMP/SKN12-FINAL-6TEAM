from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..database import get_db
from ..schemas.chat import (
    ChatSessionCreate,
    ChatSessionResponse,
    ChatSessionDetailResponse,
    SendMessageRequest,
    SendMessageResponse,
    ChatSessionStats,
    ErrorResponse
)
from ..services.chat_service import ChatService
from ..services.ai_service import AIService

router = APIRouter()

@router.post("/sessions", response_model=ChatSessionResponse)
async def create_chat_session(
    session_data: ChatSessionCreate,
    db: Session = Depends(get_db)
):
    """새 채팅 세션 생성"""
    try:
        print(f"세션 생성 요청 받음: user_id={session_data.user_id}, friends_id={session_data.friends_id}, session_name={session_data.session_name}")
        chat_service = ChatService(db)
        session = chat_service.create_session(session_data)
        print(f"세션 생성 성공: {session.chat_sessions_id}")
        return session
    except Exception as e:
        print(f"세션 생성 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"세션 생성 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/sessions", response_model=List[ChatSessionResponse])
async def get_user_sessions(
    user_id: int,
    db: Session = Depends(get_db)
):
    """사용자의 모든 채팅 세션 목록 조회"""
    try:
        chat_service = ChatService(db)
        sessions = chat_service.get_user_sessions(user_id)
        return sessions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"세션 목록 조회 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/sessions/{session_id}", response_model=ChatSessionDetailResponse)
async def get_session_detail(
    session_id: UUID,
    db: Session = Depends(get_db)
):
    """특정 채팅 세션 상세 조회 (메시지 포함)"""
    try:
        chat_service = ChatService(db)
        session = chat_service.get_session(session_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="세션을 찾을 수 없습니다."
            )
        
        messages = chat_service.get_session_messages(session_id)
        
        # 세션 정보에 메시지 추가
        session_detail = ChatSessionDetailResponse(
            chat_sessions_id=session.chat_sessions_id,
            user_id=session.user_id,
            friends_id=session.friends_id,
            session_name=session.session_name,
            is_active=session.is_active,
            created_at=session.created_at,
            updated_at=session.updated_at,
            user_type=session.user_type,
            conversation_stage=session.conversation_stage,
            emotional_state=session.emotional_state,
            messages=messages
        )
        
        return session_detail
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"세션 상세 조회 중 오류가 발생했습니다: {str(e)}"
        )

@router.post("/sessions/{session_id}/messages", response_model=SendMessageResponse)
async def send_message(
    session_id: UUID,
    message_request: SendMessageRequest,
    db: Session = Depends(get_db)
):
    """메시지 전송 및 AI 응답 생성"""
    try:
        chat_service = ChatService(db)
        ai_service = AIService(db)
        
        # 세션 존재 확인
        session = chat_service.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="세션을 찾을 수 없습니다."
            )
        
        if not session.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="비활성화된 세션입니다."
            )
        
        # 사용자 메시지 저장
        user_message = chat_service.add_message(
            session_id=session_id,
            sender_type="user",
            content=message_request.content
        )
        
        # AI 응답 생성
        ai_response = ai_service.process_message(session_id, message_request.content)
        
        # AI 응답 메시지 저장
        assistant_message = chat_service.add_message(
            session_id=session_id,
            sender_type="assistant",
            content=ai_response
        )
        
        return SendMessageResponse(
            user_message=user_message,
            assistant_message=assistant_message,
            session_updated=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"메시지 전송 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/sessions/{session_id}/stats", response_model=ChatSessionStats)
async def get_session_stats(
    session_id: UUID,
    db: Session = Depends(get_db)
):
    """세션 통계 조회"""
    try:
        chat_service = ChatService(db)
        stats = chat_service.get_session_stats(session_id)
        
        if not stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="세션을 찾을 수 없습니다."
            )
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"세션 통계 조회 중 오류가 발생했습니다: {str(e)}"
        )

@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: UUID,
    db: Session = Depends(get_db)
):
    """세션 삭제 (비활성화)"""
    try:
        chat_service = ChatService(db)
        success = chat_service.delete_session(session_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="세션을 찾을 수 없습니다."
            )
        
        return {"message": "세션이 성공적으로 삭제되었습니다."}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"세션 삭제 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/sessions/{session_id}/messages")
async def get_session_messages(
    session_id: UUID,
    db: Session = Depends(get_db)
):
    """세션의 모든 메시지 조회"""
    try:
        chat_service = ChatService(db)
        
        # 세션 존재 확인
        session = chat_service.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="세션을 찾을 수 없습니다."
            )
        
        messages = chat_service.get_session_messages(session_id)
        return messages
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"메시지 조회 중 오류가 발생했습니다: {str(e)}"
        )