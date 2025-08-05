import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..config import settings


class ColoredFormatter(logging.Formatter):
    """컬러 출력을 위한 커스텀 포매터"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    level: Optional[str] = None
) -> logging.Logger:
    """
    로거 설정 함수
    
    Args:
        name: 로거 이름
        log_file: 로그 파일 경로 (None이면 settings에서 가져옴)
        level: 로그 레벨 (None이면 settings에서 가져옴)
    
    Returns:
        설정된 로거 객체
    """
    logger = logging.getLogger(name)
    
    # 이미 핸들러가 있으면 재설정하지 않음
    if logger.handlers:
        return logger
    
    # 로그 레벨 설정
    log_level = level or settings.LOG_LEVEL
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # 로그 포맷 설정
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # 콘솔 핸들러 (개발 환경에서만 컬러 사용)
    console_handler = logging.StreamHandler(sys.stdout)
    if settings.DEBUG:
        console_formatter = ColoredFormatter(log_format, datefmt=date_format)
    else:
        console_formatter = logging.Formatter(log_format, datefmt=date_format)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # 파일 핸들러
    if log_file or settings.LOG_FILE:
        file_path = Path(log_file or settings.LOG_FILE)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 로테이팅 파일 핸들러 (10MB, 5개 백업)
        file_handler = logging.handlers.RotatingFileHandler(
            file_path,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_formatter = logging.Formatter(log_format, datefmt=date_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    # 로거가 상위로 전파되지 않도록 설정
    logger.propagate = False
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """로거 가져오기"""
    return setup_logger(name)


# 민감한 정보를 필터링하는 로그 필터
class SensitiveDataFilter(logging.Filter):
    """민감한 정보를 로그에서 제거하는 필터"""
    
    SENSITIVE_PATTERNS = [
        'password', 'token', 'key', 'secret', 'api_key', 
        'access_token', 'refresh_token', 'authorization'
    ]
    
    def filter(self, record):
        # 로그 메시지에서 민감한 정보 마스킹
        message = record.getMessage()
        for pattern in self.SENSITIVE_PATTERNS:
            if pattern in message.lower():
                # 민감한 정보를 ***로 대체
                import re
                # 패턴: key=value 또는 "key": "value" 형태 찾기
                patterns = [
                    rf'{pattern}["\']?\s*[:=]\s*["\']?([^"\'\s,}}]+)',
                    rf'{pattern.upper()}["\']?\s*[:=]\s*["\']?([^"\'\s,}}]+)'
                ]
                for p in patterns:
                    message = re.sub(p, f'{pattern}=***', message, flags=re.IGNORECASE)
        
        record.msg = message
        record.args = ()
        return True


# 기본 로거 설정
root_logger = logging.getLogger()
root_logger.addFilter(SensitiveDataFilter())

# 애플리케이션 로거
app_logger = get_logger("app")
db_logger = get_logger("database")
auth_logger = get_logger("auth")
api_logger = get_logger("api")