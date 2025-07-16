import os
import jwt
from datetime import datetime, timedelta, timezone
from google.auth.transport import requests
from google.oauth2 import id_token
from sqlalchemy.orm import Session
from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate, UserLoginResponse, UserResponse
from typing import Optional, Dict, Any

class AuthService:
    def __init__(self):
        self.google_client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.secret_key = os.getenv("SECRET_KEY")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30 * 24 * 60  # 30 days

    def verify_google_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Google ID 토큰을 검증하고 사용자 정보를 반환합니다."""
        try:
            # Google 토큰 검증
            idinfo = id_token.verify_oauth2_token(
                token, requests.Request(), self.google_client_id
            )
            
            # 발급자 확인
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
                
            return idinfo
            
        except ValueError as e:
            print(f"Token verification failed: {e}")
            return None

    def create_access_token(self, data: dict) -> str:
        """JWT 액세스 토큰을 생성합니다."""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """JWT 토큰을 검증하고 페이로드를 반환합니다."""
        try:
            print(f"Verifying token: {token[:20]}...")
            print(f"Secret key: {self.secret_key[:20]}...")
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            print(f"Token verification successful: {payload}")
            return payload
        except jwt.PyJWTError as e:
            print(f"Token verification failed: {e}")
            return None

    def get_or_create_user(self, db: Session, google_user_info: Dict[str, Any]) -> tuple[User, bool]:
        """Google 사용자 정보로 사용자를 조회하거나 생성합니다."""
        google_id = google_user_info.get('sub')
        email = google_user_info.get('email')
        name = google_user_info.get('name')
        picture = google_user_info.get('picture')
        
        print(f"Processing user: google_id={google_id}, email={email}, name={name}")
        
        # 기존 사용자 조회
        user = db.query(User).filter(User.google_id == google_id).first()
        
        if user:
            # 기존 사용자인 경우 정보 업데이트
            print(f"Existing user found: {user.id}")
            user.email = email
            user.profile_picture = picture
            user.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(user)
            return user, False  # 기존 사용자
        else:
            # 새 사용자 생성
            print(f"Creating new user with email: {email}")
            user_create = UserCreate(
                email=email,
                google_id=google_id,
                name=name,
                profile_picture=picture
            )
            
            new_user = User(
                email=user_create.email,
                google_id=user_create.google_id,
                name=user_create.name,
                profile_picture=user_create.profile_picture,
                is_first_login=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            print(f"Adding new user to database...")
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            print(f"New user created with ID: {new_user.id}")
            return new_user, True  # 새 사용자

    def update_user(self, db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """사용자 정보를 업데이트합니다."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
            
        update_data = user_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
            
        user.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(user)
        return user

    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """ID로 사용자를 조회합니다."""
        return db.query(User).filter(User.id == user_id).first()

    def google_login(self, db: Session, google_token: str) -> Optional[UserLoginResponse]:
        """Google 토큰으로 로그인/회원가입을 처리합니다."""
        # Google 토큰 검증
        google_user_info = self.verify_google_token(google_token)
        if not google_user_info:
            return None
            
        # 사용자 조회/생성
        user, is_new_user = self.get_or_create_user(db, google_user_info)
        
        # JWT 토큰 생성
        access_token = self.create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        
        # 응답 생성
        user_response = UserResponse.model_validate(user)
        return UserLoginResponse(
            user=user_response,
            access_token=access_token,
            is_first_login=user.is_first_login
        )

    def google_login_with_userinfo(self, db: Session, user_info_request) -> Optional[UserLoginResponse]:
        """Google 사용자 정보로 로그인/회원가입을 처리합니다."""
        # 사용자 정보 구성
        google_user_info = {
            'sub': user_info_request.google_id,
            'email': user_info_request.email,
            'name': user_info_request.name,
            'picture': user_info_request.picture
        }
            
        # 사용자 조회/생성
        user, is_new_user = self.get_or_create_user(db, google_user_info)
        
        # JWT 토큰 생성
        access_token = self.create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        
        # 응답 생성
        user_response = UserResponse.model_validate(user)
        return UserLoginResponse(
            user=user_response,
            access_token=access_token,
            is_first_login=user.is_first_login
        )

    def check_nickname_availability(self, db: Session, nickname: str) -> bool:
        """닉네임 사용 가능 여부를 확인합니다."""
        existing_user = db.query(User).filter(User.name == nickname).first()
        return existing_user is None

    def handle_google_callback(self, db: Session, authorization_code: str) -> Optional[UserLoginResponse]:
        """Google OAuth 콜백을 처리합니다."""
        try:
            import requests
            
            # Authorization code를 access token으로 교환
            token_url = "https://oauth2.googleapis.com/token"
            token_data = {
                "client_id": self.google_client_id,
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "code": authorization_code,
                "grant_type": "authorization_code",
                "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")
            }
            
            token_response = requests.post(token_url, data=token_data)
            if not token_response.ok:
                print(f"Token exchange failed: {token_response.text}")
                return None
                
            token_info = token_response.json()
            access_token = token_info.get("access_token")
            
            if not access_token:
                return None
            
            # Access token으로 사용자 정보 가져오기
            userinfo_url = f"https://www.googleapis.com/oauth2/v2/userinfo?access_token={access_token}"
            userinfo_response = requests.get(userinfo_url)
            
            if not userinfo_response.ok:
                print(f"Userinfo fetch failed: {userinfo_response.text}")
                return None
                
            user_info = userinfo_response.json()
            
            # 사용자 정보로 로그인/회원가입 처리
            google_user_info = {
                'sub': user_info.get('id'),
                'email': user_info.get('email'),
                'name': user_info.get('name'),
                'picture': user_info.get('picture')
            }
            
            user, is_new_user = self.get_or_create_user(db, google_user_info)
            
            # JWT 토큰 생성
            jwt_token = self.create_access_token(
                data={"sub": str(user.id), "email": user.email}
            )
            
            # 응답 생성
            user_response = UserResponse.model_validate(user)
            return UserLoginResponse(
                user=user_response,
                access_token=jwt_token,
                is_first_login=user.is_first_login
            )
            
        except Exception as e:
            print(f"Google callback handling failed: {e}")
            return None