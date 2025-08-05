"""Rate limiting 미들웨어"""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, Dict
import time
import asyncio
from collections import defaultdict
from ..config import settings
from ..utils.logger import api_logger as logger


class RateLimitMiddleware(BaseHTTPMiddleware):
    """요청 속도 제한 미들웨어"""
    
    def __init__(self, app, calls: int = settings.RATE_LIMIT_PER_MINUTE, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients: Dict[str, list] = defaultdict(list)
        self._cleanup_task = None
        
    async def dispatch(self, request: Request, call_next: Callable):
        # 클라이언트 IP 가져오기
        client_ip = request.client.host
        if forwarded_for := request.headers.get("X-Forwarded-For"):
            client_ip = forwarded_for.split(",")[0].strip()
        
        # 현재 시간
        current_time = time.time()
        
        # 클라이언트의 요청 기록 가져오기
        request_times = self.clients[client_ip]
        
        # 오래된 요청 기록 제거
        request_times[:] = [t for t in request_times if current_time - t < self.period]
        
        # Rate limit 확인
        if len(request_times) >= self.calls:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Maximum {self.calls} requests per {self.period} seconds",
                headers={"Retry-After": str(self.period)}
            )
        
        # 현재 요청 기록
        request_times.append(current_time)
        
        # 주기적으로 오래된 기록 정리
        if not self._cleanup_task:
            self._cleanup_task = asyncio.create_task(self._cleanup_old_entries())
        
        response = await call_next(request)
        
        # Rate limit 정보를 헤더에 추가
        remaining = self.calls - len(request_times)
        response.headers["X-RateLimit-Limit"] = str(self.calls)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(current_time + self.period))
        
        return response
    
    async def _cleanup_old_entries(self):
        """오래된 요청 기록을 주기적으로 정리"""
        while True:
            await asyncio.sleep(self.period)
            current_time = time.time()
            
            # 메모리 절약을 위해 오래된 클라이언트 기록 삭제
            empty_clients = []
            for client_ip, request_times in self.clients.items():
                request_times[:] = [t for t in request_times if current_time - t < self.period]
                if not request_times:
                    empty_clients.append(client_ip)
            
            for client_ip in empty_clients:
                del self.clients[client_ip]
            
            if empty_clients:
                logger.debug(f"Cleaned up rate limit records for {len(empty_clients)} clients")