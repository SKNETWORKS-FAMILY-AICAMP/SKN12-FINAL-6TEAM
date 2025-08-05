"""입력 검증 미들웨어"""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import json
from ..config import settings
from ..utils.logger import api_logger as logger


class InputValidationMiddleware(BaseHTTPMiddleware):
    """요청 데이터 검증 미들웨어"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        # 파일 업로드 검증
        if request.headers.get("content-type", "").startswith("multipart/form-data"):
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > settings.MAX_UPLOAD_SIZE:
                logger.warning(f"File upload too large: {content_length} bytes")
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE} bytes"
                )
        
        # JSON 요청 크기 검증
        if request.headers.get("content-type") == "application/json":
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > 1024 * 1024:  # 1MB
                logger.warning(f"JSON request too large: {content_length} bytes")
                raise HTTPException(
                    status_code=413,
                    detail="Request body too large. Maximum size is 1MB"
                )
        
        # SQL Injection 패턴 검증 (쿼리 파라미터)
        suspicious_patterns = [
            "union select", "drop table", "delete from", 
            "insert into", "update set", "--", "/*", "*/"
        ]
        
        query_string = str(request.url.query).lower()
        for pattern in suspicious_patterns:
            if pattern in query_string:
                logger.error(f"Suspicious SQL pattern detected: {pattern} in {request.url}")
                raise HTTPException(
                    status_code=400,
                    detail="Invalid request parameters"
                )
        
        response = await call_next(request)
        return response