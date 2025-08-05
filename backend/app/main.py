from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import logging
from dotenv import load_dotenv

from .api.chat import router as chat_router
from .api.auth import router as auth_router
from .api.user import router as user_router
from .api.persona import router as persona_router
from .api.test import router as test_router
from .api.rating import router as rating_router
from .api.agreement import router as agreement_router
from .api.admin import router as admin_router
from .api.pipeline import router as pipeline_router
from .database import create_tables
from .config import settings

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI 애플리케이션 생성
app = FastAPI(
    title=settings.APP_NAME,
    description="심리 상담 챗봇 API",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,  # 프로덕션에서 문서 숨기기
    redoc_url="/redoc" if settings.DEBUG else None
)

# CORS 설정 - 환경별로 다르게 적용
if settings.ENVIRONMENT == "development":
    cors_origins = ["http://localhost:3000", "http://localhost:80", "http://localhost:8080"]
else:
    cors_origins = settings.ALLOWED_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 미들웨어 임포트
from .middleware.validation import InputValidationMiddleware
from .middleware.rate_limit import RateLimitMiddleware
from .middleware.security import SecurityHeadersMiddleware

# 미들웨어 추가 (순서 중요 - 보안 헤더가 가장 먼저)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(InputValidationMiddleware)

# 정적 파일 서빙 설정
# result/images 디렉토리가 없으면 생성
if not os.path.exists("result/images"):
    os.makedirs("result/images")

# uploads/profile_images 디렉토리가 없으면 생성  
if not os.path.exists("uploads/profile_images"):
    os.makedirs("uploads/profile_images")
    
app.mount("/images", StaticFiles(directory="result/images"), name="images")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# 라우터 등록
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(persona_router, prefix="/personas", tags=["personas"])
app.include_router(chat_router, prefix="/chat", tags=["chat"])
app.include_router(test_router, prefix="/api/v1/test", tags=["tests"])
app.include_router(rating_router, prefix="/ratings", tags=["ratings"])
app.include_router(agreement_router, prefix="/api/v1/agreement", tags=["agreements"])
app.include_router(admin_router, prefix="/api/v1", tags=["admin"])
app.include_router(pipeline_router, prefix="/api/v1/pipeline", tags=["pipeline"])

# 시작 이벤트
@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행"""
    try:
        # 1. 데이터베이스 테이블 생성
        create_tables()
        logger.info("Database tables created successfully")
        
        # 2. 페르소나 동기화
        from .services.persona_sync import persona_sync_service
        from .database import get_db
        
        db = next(get_db())
        try:
            sync_success = persona_sync_service.sync_personas_table(db)
            if sync_success:
                logger.info("Persona synchronization completed successfully")
            else:
                logger.warning("Persona synchronization failed")
        finally:
            db.close()
        
        logger.info("Care Chat API is starting...")
    except Exception as e:
        logger.error(f"Application initialization failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise

# 422 오류 전용 핸들러 추가
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation Error - URL: {request.url}, Method: {request.method}")
    logger.error(f"Validation Errors: {exc.errors()}")
    
    # 프로덕션에서는 민감한 정보 제거
    if settings.DEBUG:
        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors(), "body": str(exc.body)}
        )
    else:
        return JSONResponse(
            status_code=422,
            content={"detail": "Validation error", "errors": exc.errors()}
        )

# 전역 예외 처리
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}")
    logger.error(f"Request URL: {request.url}, Method: {request.method}")
    import traceback
    logger.error(traceback.format_exc())
    
    # 프로덕션에서는 상세 에러 정보 숨기기
    if settings.DEBUG:
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "detail": str(exc)}
        )
    else:
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )
    
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )