import os
import jwt
from datetime import datetime, timedelta, timezone
from google.auth.transport import requests
from google.oauth2 import id_token
from sqlalchemy.orm import Session
from ..models.user import SocialUser, User, UserInformation
from ..schemas.user import UserCreate, UserUpdate, UserResponse, SocialLoginResponse
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

    def get_or_create_user(self, db: Session, google_user_info: Dict[str, Any]) -> tuple[UserInformation, bool]:
        """Google 사용자 정보로 사용자를 조회하거나 생성합니다."""
        google_id = google_user_info.get('sub')
        email = google_user_info.get('email')
        name = google_user_info.get('name')
        picture = google_user_info.get('picture')
        
        print(f"Processing user: google_id={google_id}, email={email}, name={name}")
        
        # race condition 방지를 위한 트랜잭션 격리
        from sqlalchemy.exc import IntegrityError
        from sqlalchemy import and_
        
        # 최대 3회 재시도로 race condition 완전 해결
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # 기존 소셜 사용자 조회
                social_user = db.query(SocialUser).filter(
                    SocialUser.social_id == google_id
                ).first()
            
                if social_user:
                    # 동일한 Google ID로 생성된 모든 social_user 조회 (중복 계정 감지)
                    all_social_users = db.query(SocialUser).filter(
                        SocialUser.social_id == google_id
                    ).all()
                    
                    if len(all_social_users) > 1:
                        print(f"⚠️ Multiple social_users detected for {google_id}: {len(all_social_users)} accounts")
                        # 중복 계정 정리 로직 호출
                        social_user = self._cleanup_duplicate_users(db, all_social_users, google_id)
                    
                    # 기존 사용자인 경우 사용자 정보 조회
                    user_info = db.query(UserInformation).filter(
                        UserInformation.social_user_id == social_user.social_user_id
                    ).first()
                    
                    if user_info:
                        print(f"Existing user found: {user_info.user_id}, nickname: {user_info.nickname}, status: {user_info.status}")
                        
                        # INACTIVE 사용자 복구 체크
                        if user_info.status == "INACTIVE":
                            from datetime import datetime, timezone, timedelta
                            
                            # 1년 이내인지 확인
                            if user_info.deleted_at:
                                one_year_ago = datetime.now(timezone.utc) - timedelta(days=365)
                                
                                # deleted_at이 timezone-naive인 경우 UTC로 간주
                                deleted_at = user_info.deleted_at
                                if deleted_at.tzinfo is None:
                                    deleted_at = deleted_at.replace(tzinfo=timezone.utc)
                                
                                if deleted_at > one_year_ago:
                                    # 1년 이내면 복구
                                    user_info.status = "ACTIVE"
                                    user_info.deleted_at = None
                                    db.commit()
                                    db.refresh(user_info)
                                    print(f"User reactivated: {user_info.user_id}")
                                else:
                                    # 1년 초과면 로그인 거부
                                    print(f"User account expired: {user_info.user_id}")
                                    return None, False
                            else:
                                # deleted_at이 없는 INACTIVE 사용자도 복구 (기존 데이터 호환성)
                                user_info.status = "ACTIVE"
                                db.commit()
                                db.refresh(user_info)
                                print(f"User reactivated (no deleted_at): {user_info.user_id}")
                        
                        # temp_user_로 시작하는 닉네임이면 신규 사용자로 판단
                        is_new_user = user_info.nickname.startswith('temp_user_')
                        print(f"Is new user check: {is_new_user} (nickname: {user_info.nickname})")
                        return user_info, is_new_user
                    else:
                        # social_user는 있지만 user_info가 없는 경우 (데이터 불일치 상황)
                        print(f"Social user exists but no user_info found. Creating user_info for existing social_user: {social_user.social_user_id}")
                        temp_nickname = f"temp_user_{social_user.social_user_id}"
                        new_user_info = UserInformation(
                            nickname=temp_nickname,
                            social_user_id=social_user.social_user_id,
                            status='ACTIVE'
                        )
                        
                        db.add(new_user_info)
                        db.commit()
                        db.refresh(new_user_info)
                        print(f"User info created for existing social user: {new_user_info.user_id}")
                        return new_user_info, True  # 신규 사용자로 판단
                
                # 새 사용자 생성
                print(f"Creating new user with email: {email} (attempt {attempt + 1})")
                
                # 소셜 사용자 생성
                new_social_user = SocialUser(social_id=google_id)
                db.add(new_social_user)
                db.flush()
                
                # 사용자 정보 생성 (새 사용자는 임시 닉네임으로 시작)
                temp_nickname = f"temp_user_{new_social_user.social_user_id}"
                new_user_info = UserInformation(
                    nickname=temp_nickname,
                    social_user_id=new_social_user.social_user_id,
                    status='ACTIVE'
                )
                
                print(f"Adding new user to database...")
                db.add(new_user_info)
                db.commit()
                db.refresh(new_user_info)
                print(f"New user created with ID: {new_user_info.user_id}, nickname: {new_user_info.nickname}")
                return new_user_info, True  # 새 사용자
                
            except IntegrityError as e:
                # 중복 생성 시도 시 롤백 후 재시도
                print(f"IntegrityError caught (attempt {attempt + 1}): {e}")
                db.rollback()
                
                if attempt < max_retries - 1:
                    import time
                    time.sleep(0.1 * (attempt + 1))  # 지수 백오프
                    continue
                else:
                    # 최종 시도에서도 실패하면 기존 사용자 찾기
                    social_user = db.query(SocialUser).filter(SocialUser.social_id == google_id).first()
                    if social_user:
                        user_info = db.query(UserInformation).filter(
                            UserInformation.social_user_id == social_user.social_user_id
                        ).first()
                        if user_info:
                            is_new_user = user_info.nickname.startswith('temp_user_')
                            print(f"Found existing user after final IntegrityError: {user_info.user_id}")
                            return user_info, is_new_user
                    
                    print(f"Failed to create or find user after all retries")
                    return None, False
                    
            except Exception as e:
                print(f"Unexpected error (attempt {attempt + 1}): {e}")
                db.rollback()
                if attempt < max_retries - 1:
                    import time
                    time.sleep(0.1 * (attempt + 1))
                    continue
                else:
                    return None, False
        
        # 모든 재시도 실패
        print(f"All retry attempts failed")
        return None, False

    def _cleanup_duplicate_users(self, db: Session, all_social_users, google_id: str) -> SocialUser:
        """중복 생성된 social_user 계정을 정리하고 유효한 하나만 남김"""
        print(f"🔧 Cleaning up {len(all_social_users)} duplicate social_users for {google_id}")
        
        # 각 social_user에 대한 user_info 조회
        valid_users = []
        temp_users = []
        
        for social_user in all_social_users:
            user_info = db.query(UserInformation).filter(
                UserInformation.social_user_id == social_user.social_user_id
            ).first()
            
            if user_info:
                if user_info.nickname.startswith('temp_user_'):
                    temp_users.append((social_user, user_info))
                else:
                    valid_users.append((social_user, user_info))
                    
        print(f"Found {len(valid_users)} valid users, {len(temp_users)} temp users")
        
        # 유효한 닉네임을 가진 사용자가 있으면 그것을 우선
        if valid_users:
            keep_social_user, keep_user_info = valid_users[0]
            print(f"✅ Keeping valid user: {keep_user_info.nickname} (social_user_id: {keep_social_user.social_user_id})")
            
            # 나머지 모든 계정 삭제 (temp_users + 추가 valid_users)
            for social_user, user_info in temp_users + valid_users[1:]:
                try:
                    print(f"🗑️ Deleting duplicate: {user_info.nickname} (social_user_id: {social_user.social_user_id})")
                    # CASCADE로 user_info도 함께 삭제됨
                    db.delete(social_user)
                except Exception as e:
                    print(f"❌ Error deleting duplicate social_user {social_user.social_user_id}: {e}")
                    
            return keep_social_user
            
        elif temp_users:
            # 모든 사용자가 temp_user인 경우, 첫 번째 것만 유지
            keep_social_user, keep_user_info = temp_users[0]
            print(f"⚠️ All users are temp_users, keeping first: {keep_user_info.nickname}")
            
            # 나머지 temp_user들 삭제
            for social_user, user_info in temp_users[1:]:
                try:
                    print(f"🗑️ Deleting duplicate temp_user: {user_info.nickname} (social_user_id: {social_user.social_user_id})")
                    db.delete(social_user)
                except Exception as e:
                    print(f"❌ Error deleting duplicate temp_user {social_user.social_user_id}: {e}")
                    
            return keep_social_user
            
        else:
            # user_info가 없는 social_user들만 있는 경우 (이상한 상황)
            print(f"⚠️ All social_users have no user_info, keeping first")
            keep_social_user = all_social_users[0]
            
            # 나머지 삭제
            for social_user in all_social_users[1:]:
                try:
                    print(f"🗑️ Deleting social_user without user_info: {social_user.social_user_id}")
                    db.delete(social_user)
                except Exception as e:
                    print(f"❌ Error deleting social_user {social_user.social_user_id}: {e}")
                    
            return keep_social_user

    def update_user(self, db: Session, user_id: int, user_update: UserUpdate) -> Optional[UserInformation]:
        """사용자 정보를 업데이트합니다."""
        user_info = db.query(UserInformation).filter(UserInformation.user_id == user_id).first()
        if not user_info:
            return None
            
        update_data = user_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(user_info, field):
                setattr(user_info, field, value)
            
        db.commit()
        db.refresh(user_info)
        return user_info

    def get_user_by_id(self, db: Session, user_id: int) -> Optional[UserInformation]:
        """ID로 사용자를 조회합니다."""
        return db.query(UserInformation).filter(UserInformation.user_id == user_id).first()

    def google_login(self, db: Session, google_token: str) -> Optional[dict]:
        """Google 토큰으로 로그인/회원가입을 처리합니다."""
        print(f"Starting Google login with token: {google_token[:50]}...")
        
        # Google 토큰 검증
        google_user_info = self.verify_google_token(google_token)
        if not google_user_info:
            print("Google token verification failed")
            return None
            
        print(f"Google user info: {google_user_info}")
        
        # 사용자 조회/생성
        user_info, is_new_user = self.get_or_create_user(db, google_user_info)
        
        print(f"User created/found: user_id={user_info.user_id}, is_new_user={is_new_user}, nickname={user_info.nickname}")
        
        # 응답 생성 (SocialLoginResponse 대신 dict로 반환하여 더 많은 정보 포함)
        result = {
            "user_id": user_info.user_id,
            "nickname": user_info.nickname,
            "is_new_user": is_new_user,
            "email": google_user_info.get('email'),
            "google_id": google_user_info.get('sub'),
            "name": google_user_info.get('name'),
            "picture": google_user_info.get('picture'),
            "created_at": user_info.created_at.isoformat() if user_info.created_at else None
        }
        
        print(f"Google login result: {result}")
        return result

    def google_login_with_userinfo(self, db: Session, user_info_request) -> Optional[SocialLoginResponse]:
        """Google 사용자 정보로 로그인/회원가입을 처리합니다."""
        # 사용자 정보 구성
        google_user_info = {
            'sub': user_info_request.google_id,
            'email': user_info_request.email,
            'name': user_info_request.name,
            'picture': user_info_request.picture
        }
            
        # 사용자 조회/생성
        user_info, is_new_user = self.get_or_create_user(db, google_user_info)
        
        # JWT 토큰 생성
        access_token = self.create_access_token(
            data={"sub": str(user_info.user_id), "email": google_user_info.get('email')}
        )
        
        # 응답 생성
        return SocialLoginResponse(
            user_id=user_info.user_id,
            nickname=user_info.nickname,
            is_new_user=is_new_user
        )

    def check_nickname_availability(self, db: Session, nickname: str) -> bool:
        """닉네임 사용 가능 여부를 확인합니다."""
        existing_user = db.query(UserInformation).filter(UserInformation.nickname == nickname).first()
        return existing_user is None

    def handle_google_callback(self, db: Session, authorization_code: str) -> Optional[SocialLoginResponse]:
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
                "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI", "http://ec2-3-34-245-132.ap-northeast-2.compute.amazonaws.com/auth/google/callback")
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
            
            user_info, is_new_user = self.get_or_create_user(db, google_user_info)
            
            # JWT 토큰 생성
            jwt_token = self.create_access_token(
                data={"sub": str(user_info.user_id), "email": google_user_info.get('email')}
            )
            
            # 응답 생성
            return SocialLoginResponse(
                user_id=user_info.user_id,
                nickname=user_info.nickname,
                is_new_user=is_new_user
            )
            
        except Exception as e:
            print(f"Google callback handling failed: {e}")
            return None