"""
사용자 관리 API 라우터
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.schemas.user import (
    UserCreate, UserUpdate, UserResponse, UserLogin, UserListResponse,
    PasswordChange, SocialLoginResponse
)
from app.models.user import User, UserInformation, SocialUser
from app.database import get_db

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """일반 사용자 회원가입"""
    # 닉네임 중복 확인
    existing_user = db.query(UserInformation).filter(
        UserInformation.nickname == user_data.nickname
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 사용 중인 닉네임입니다."
        )
    
    # 일반 사용자 생성
    new_user = User(user_password=user_data.user_password)  # 실제로는 해시화 필요
    db.add(new_user)
    db.flush()
    
    # 사용자 정보 생성
    user_info = UserInformation(
        nickname=user_data.nickname,
        regular_user_id=new_user.user_id,
        status="ACTIVE"
    )
    db.add(user_info)
    db.commit()
    
    return UserResponse(
        user_id=user_info.user_id,
        nickname=user_info.nickname,
        user_type="REGULAR",
        status=user_info.status
    )

@router.post("/social-login", response_model=SocialLoginResponse)
async def social_login(social_id: str, nickname: str, db: Session = Depends(get_db)):
    """소셜 로그인"""
    # 기존 소셜 사용자 확인
    social_user = db.query(SocialUser).filter(
        SocialUser.social_id == social_id
    ).first()
    
    if not social_user:
        # 새 소셜 사용자 생성
        social_user = SocialUser(social_id=social_id)
        db.add(social_user)
        db.flush()
        
        # 사용자 정보 생성
        user_info = UserInformation(
            nickname=nickname,
            social_user_id=social_user.social_user_id,
            status="ACTIVE"
        )
        db.add(user_info)
        db.commit()
        
        return SocialLoginResponse(
            user_id=user_info.user_id,
            nickname=user_info.nickname,
            is_new_user=True
        )
    else:
        # 기존 사용자 정보 조회
        user_info = db.query(UserInformation).filter(
            UserInformation.social_user_id == social_user.social_user_id
        ).first()
        
        return SocialLoginResponse(
            user_id=user_info.user_id,
            nickname=user_info.nickname,
            is_new_user=False
        )

@router.get("/users")
async def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """사용자 목록 조회"""
    users = db.query(UserInformation).filter(
        UserInformation.status == "ACTIVE"
    ).offset(skip).limit(limit).all()
    
    user_responses = []
    for user_info in users:
        user_type = "SOCIAL" if user_info.social_user_id is not None else "REGULAR"
        user_responses.append({
            "user_id": user_info.user_id,
            "nickname": user_info.nickname,
            "user_type": user_type,
            "status": user_info.status,
            "created_at": user_info.created_at.isoformat() if user_info.created_at else None
        })
    
    return {"users": user_responses}

@router.get("/users/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """특정 사용자 조회"""
    user_info = db.query(UserInformation).filter(
        UserInformation.user_id == user_id
    ).first()
    
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
    
    user_type = "SOCIAL" if user_info.social_user_id is not None else "REGULAR"
    
    return {
        "user_id": user_info.user_id,
        "nickname": user_info.nickname,
        "user_type": user_type,
        "status": user_info.status,
        "created_at": user_info.created_at.isoformat() if user_info.created_at else None
    }

@router.put("/users/{user_id}")
async def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    """사용자 정보 수정"""
    user_info = db.query(UserInformation).filter(
        UserInformation.user_id == user_id
    ).first()
    
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
    
    # 닉네임 변경 시 중복 확인
    if user_data.nickname and user_data.nickname != user_info.nickname:
        existing_user = db.query(UserInformation).filter(
            UserInformation.nickname == user_data.nickname,
            UserInformation.user_id != user_id
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 사용 중인 닉네임입니다."
            )
        
        user_info.nickname = user_data.nickname
    
    if hasattr(user_data, 'status') and user_data.status:
        user_info.status = user_data.status
    
    db.commit()
    
    user_type = "SOCIAL" if user_info.social_user_id is not None else "REGULAR"
    
    return {
        "user_id": user_info.user_id,
        "nickname": user_info.nickname,
        "user_type": user_type,
        "status": user_info.status,
        "created_at": user_info.created_at.isoformat() if user_info.created_at else None
    }

@router.post("/users/{user_id}/change-password")
async def change_password(user_id: int, password_data: PasswordChange, db: Session = Depends(get_db)):
    """비밀번호 변경 (일반 사용자만)"""
    user_info = db.query(UserInformation).filter(
        UserInformation.user_id == user_id
    ).first()
    
    if not user_info or not user_info.regular_user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="일반 사용자를 찾을 수 없습니다."
        )
    
    user = db.query(User).filter(
        User.user_id == user_info.regular_user_id
    ).first()
    
    # 현재 비밀번호 확인 (실제로는 해시 비교 필요)
    if user.user_password != password_data.current_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="현재 비밀번호가 일치하지 않습니다."
        )
    
    # 새 비밀번호 설정 (실제로는 해시화 필요)
    user.user_password = password_data.new_password
    db.commit()
    
    return {"message": "비밀번호가 성공적으로 변경되었습니다."}

@router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """사용자 삭제 (비활성화)"""
    user_info = db.query(UserInformation).filter(
        UserInformation.user_id == user_id
    ).first()
    
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
    
    user_info.status = "INACTIVE"
    db.commit()
    
    return {"message": "사용자가 성공적으로 삭제되었습니다."}

@router.get("/users/{user_id}/profile", response_model=dict)
async def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    """마이페이지용 사용자 프로필 조회"""
    from app.models.chat import ChatSession
    from app.models.test import DrawingTest
    from sqlalchemy import func
    
    user_info = db.query(UserInformation).filter(
        UserInformation.user_id == user_id
    ).first()
    
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
    
    # 채팅 세션 수 계산
    total_chats = db.query(func.count(ChatSession.chat_sessions_id)).filter(
        ChatSession.user_id == user_id
    ).scalar() or 0
    
    # 테스트 결과 수 계산
    total_tests = db.query(func.count(DrawingTest.test_id)).filter(
        DrawingTest.user_id == user_id
    ).scalar() or 0
    
    user_type = "SOCIAL" if user_info.social_user_id is not None else "REGULAR"
    
    return {
        "user_id": user_info.user_id,
        "name": user_info.nickname,
        "nickname": user_info.nickname,
        "email": None,  # 추후 이메일 필드 추가시 수정
        "user_type": user_type,
        "status": user_info.status,
        "join_date": user_info.created_at.isoformat() if hasattr(user_info, 'created_at') else None,
        "total_chats": total_chats,
        "total_tests": total_tests
    }

@router.get("/users/{user_id}/chat-history")
async def get_user_chat_history(
    user_id: int, 
    skip: int = 0, 
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """사용자 채팅 히스토리 조회"""
    from app.models.chat import ChatSession, ChatMessage
    from sqlalchemy.orm import joinedload
    
    user_info = db.query(UserInformation).filter(
        UserInformation.user_id == user_id
    ).first()
    
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
    
    # 채팅 세션 조회 (최신순)
    chat_sessions = db.query(ChatSession).options(
        joinedload(ChatSession.messages)
    ).filter(
        ChatSession.user_id == user_id
    ).order_by(ChatSession.created_at.desc()).offset(skip).limit(limit).all()
    
    chat_history = []
    for session in chat_sessions:
        # 마지막 메시지 조회
        last_message = db.query(ChatMessage).filter(
            ChatMessage.session_id == session.chat_sessions_id
        ).order_by(ChatMessage.created_at.desc()).first()
        
        messages = []
        for msg in session.messages:
            messages.append({
                "text": msg.content,
                "sender": "user" if msg.sender_type == "user" else "ai",
                "timestamp": msg.created_at.isoformat()
            })
        
        chat_history.append({
            "id": str(session.chat_sessions_id),
            "character_name": session.session_name or "AI 상담사",
            "character_avatar": "🤖",  # 기본 아바타
            "date": session.created_at.date().isoformat(),
            "last_message_time": last_message.created_at.isoformat() if last_message else session.created_at.isoformat(),
            "messages": messages
        })
    
    return {
        "chat_history": chat_history,
        "total": len(chat_history),
        "has_more": len(chat_sessions) == limit
    }

@router.get("/users/{user_id}/test-results")
async def get_user_test_results(
    user_id: int, 
    skip: int = 0, 
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """사용자 테스트 결과 조회"""
    from app.models.test import DrawingTest, DrawingTestResult
    
    user_info = db.query(UserInformation).filter(
        UserInformation.user_id == user_id
    ).first()
    
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
    
    # 테스트 결과 조회 (최신순)
    from sqlalchemy.orm import joinedload
    test_results = db.query(DrawingTest).options(
        joinedload(DrawingTest.result).joinedload(DrawingTestResult.friend)
    ).filter(
        DrawingTest.user_id == user_id
    ).order_by(DrawingTest.submitted_at.desc()).offset(skip).limit(limit).all()
    
    results = []
    for test in test_results:
        character_match = "미정"
        interpretation = "분석 중..."
        
        if test.result and test.result.friend:
            character_match = test.result.friend.friends_name
            interpretation = test.result.summary_text or "분석 결과가 없습니다."
        
        results.append({
            "id": str(test.test_id),
            "test_type": "그림 검사",
            "character_match": character_match,
            "interpretation": interpretation,
            "date": test.submitted_at.date().isoformat(),
            "created_at": test.submitted_at.isoformat(),
            "images": [test.image_url] if test.image_url else []
        })
    
    return {
        "test_results": results,
        "total": len(results),
        "has_more": len(test_results) == limit
    }

@router.post("/users/{user_id}/check-nickname")
async def check_nickname_availability(
    user_id: int,
    nickname: str,
    db: Session = Depends(get_db)
):
    """닉네임 중복 확인"""
    # 현재 사용자 확인
    current_user = db.query(UserInformation).filter(
        UserInformation.user_id == user_id
    ).first()
    
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
    
    # 현재 사용자의 닉네임과 동일한 경우 사용 가능
    if current_user.nickname == nickname:
        return {"available": True, "message": "현재 사용 중인 닉네임입니다."}
    
    # 다른 사용자가 사용 중인지 확인
    existing_user = db.query(UserInformation).filter(
        UserInformation.nickname == nickname,
        UserInformation.user_id != user_id,
        UserInformation.status == "ACTIVE"
    ).first()
    
    if existing_user:
        return {"available": False, "message": "이미 사용 중인 닉네임입니다."}
    
    return {"available": True, "message": "사용 가능한 닉네임입니다."}