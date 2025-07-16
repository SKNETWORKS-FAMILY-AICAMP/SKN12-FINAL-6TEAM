from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    social_id = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True)
    nickname = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False, default='ACTIVE')
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    deleted_at = Column(DateTime)
    
    # 관계 정의
    chat_sessions = relationship("ChatSession", back_populates="user")
    drawing_tests = relationship("DrawingTest", back_populates="user")
    ratings = relationship("Rating", back_populates="user")
    agreements = relationship("Agreement", back_populates="user")

class Friend(Base):
    __tablename__ = "friends"
    
    friends_id = Column(Integer, primary_key=True, autoincrement=True)
    friends_name = Column(String(100), nullable=False)
    friends_description = Column(Text, nullable=False)
    tts_audio_url = Column(String(2048))
    tts_voice_type = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    
    # 관계 정의
    chat_sessions = relationship("ChatSession", back_populates="friend")
    drawing_test_results = relationship("DrawingTestResult", back_populates="friend")

class DrawingTest(Base):
    __tablename__ = "drawing_tests"
    
    test_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    image_url = Column(String(2048))
    submitted_at = Column(DateTime, nullable=False, server_default=func.now())
    
    # 관계 정의
    user = relationship("User", back_populates="drawing_tests")
    result = relationship("DrawingTestResult", back_populates="test", uselist=False)

class DrawingTestResult(Base):
    __tablename__ = "drawing_test_results"
    
    result_id = Column(Integer, primary_key=True, autoincrement=True)
    test_id = Column(Integer, ForeignKey('drawing_tests.test_id'), unique=True, nullable=False)
    friends_type = Column(Integer, ForeignKey('friends.friends_id'))
    score = Column(Integer)
    summary_text = Column(Text)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    
    # 관계 정의
    test = relationship("DrawingTest", back_populates="result")
    friend = relationship("Friend", back_populates="drawing_test_results")

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    chat_sessions_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'))
    friends_id = Column(Integer, ForeignKey('friends.friends_id'))
    session_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())
    
    # 관계 정의
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    user = relationship("User", back_populates="chat_sessions")
    friend = relationship("Friend", back_populates="chat_sessions")
    rating = relationship("Rating", back_populates="session", uselist=False)

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    chat_messages_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('chat_sessions.chat_sessions_id', ondelete='CASCADE'))
    sender_type = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    # 관계 정의
    session = relationship("ChatSession", back_populates="messages")

class Rating(Base):
    __tablename__ = "ratings"
    
    ratings_id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey('chat_sessions.chat_sessions_id'), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    
    # 관계 정의
    session = relationship("ChatSession", back_populates="rating")
    user = relationship("User", back_populates="ratings")

class Agreement(Base):
    __tablename__ = "agreements"
    
    agreement_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    is_agree = Column(Boolean, default=False)
    agreed_at = Column(DateTime, nullable=False, server_default=func.now())
    
    # 관계 정의
    user = relationship("User", back_populates="agreements")