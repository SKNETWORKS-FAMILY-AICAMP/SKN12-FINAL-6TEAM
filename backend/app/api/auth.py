from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.auth_service import AuthService
from ..schemas.user import UserLoginResponse, UserUpdate, UserResponse
from pydantic import BaseModel
from typing import Optional

router = APIRouter()
auth_service = AuthService()

# OAuth2 스키마 설정
from fastapi.security import HTTPBearer
oauth2_scheme = HTTPBearer()

# JWT 토큰에서 현재 사용자 정보를 추출하는 의존성
async def get_current_user(token = Depends(oauth2_scheme)) -> dict:
    """JWT 토큰에서 현재 사용자 정보를 추출합니다."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = auth_service.verify_token(token.credentials)
    if payload is None:
        raise credentials_exception
        
    user_id: str = payload.get("sub")
    email: str = payload.get("email")
    if user_id is None or email is None:
        raise credentials_exception
        
    return {"user_id": int(user_id), "email": email}

class GoogleLoginRequest(BaseModel):
    token: str

class GoogleUserInfoRequest(BaseModel):
    google_id: str
    email: str
    name: str
    picture: str

class UpdateNicknameRequest(BaseModel):
    nickname: str

class CheckNicknameRequest(BaseModel):
    nickname: str

class GoogleCallbackRequest(BaseModel):
    code: str

@router.post("/google", response_model=UserLoginResponse)
async def google_login(
    request: GoogleLoginRequest,
    db: Session = Depends(get_db)
):
    """Google OAuth 로그인/회원가입"""
    try:
        result = auth_service.google_login(db, request.token)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Google token"
            )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.post("/google-userinfo", response_model=UserLoginResponse)
async def google_login_with_userinfo(
    request: GoogleUserInfoRequest,
    db: Session = Depends(get_db)
):
    """Google 사용자 정보로 로그인/회원가입"""
    try:
        result = auth_service.google_login_with_userinfo(db, request)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user information"
            )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.post("/complete-signup")
async def complete_signup(
    request: UpdateNicknameRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """회원가입 완료 (닉네임 설정)"""
    try:
        user_update = UserUpdate(
            name=request.nickname,
            is_first_login=False
        )
        
        updated_user = auth_service.update_user(db, current_user["user_id"], user_update)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        return UserResponse.model_validate(updated_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Signup completion failed: {str(e)}"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """현재 로그인한 사용자 정보 조회"""
    user = auth_service.get_user_by_id(db, current_user["user_id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserResponse.model_validate(user)

@router.post("/check-nickname")
async def check_nickname_availability(
    request: CheckNicknameRequest,
    db: Session = Depends(get_db)
):
    """닉네임 중복 검사"""
    try:
        is_available = auth_service.check_nickname_availability(db, request.nickname)
        return {"available": is_available, "nickname": request.nickname}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Nickname check failed: {str(e)}"
        )

@router.get("/google/callback")
async def google_callback(
    code: str,
    db: Session = Depends(get_db)
):
    """Google OAuth 콜백 처리"""
    try:
        result = auth_service.handle_google_callback(db, code)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization code"
            )
        
        # 프론트엔드로 리다이렉션 (토큰을 쿼리 파라미터로 전달)
        frontend_url = "http://localhost:3000"
        if result.is_first_login:
            redirect_url = f"{frontend_url}/nickname?token={result.access_token}"
        else:
            redirect_url = f"{frontend_url}/main?token={result.access_token}"
        
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=redirect_url)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Callback processing failed: {str(e)}"
        )