"""
거북이상담소 HTP 심리검사 파이프라인 API 
이미지 분석 요청을 처리하는 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from enum import Enum
from dataclasses import dataclass
import os
import uuid
import time
import logging
from datetime import datetime
from pathlib import Path

# PIL imports
from PIL import Image as PILImage
from PIL import ImageOps
import io

# 내부 모듈
from ..database import get_db, SessionLocal
from ..models.test import DrawingTest, DrawingTestResult
from .auth import get_current_user

# 로거 설정
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# HTP 파이프라인 모듈 import
import sys
project_root = Path(__file__).parent.parent.parent
pipeline_module_path = project_root / 'llm' / 'model'
sys.path.insert(0, str(pipeline_module_path))

try:
    from main import HTPAnalysisPipeline, PipelineStatus, PipelineResult
    PIPELINE_AVAILABLE = True
    logger.info("✅ HTP 파이프라인 모듈 import 성공")
except Exception as e:
    HTPAnalysisPipeline = None
    PipelineStatus = None
    PipelineResult = None
    PIPELINE_AVAILABLE = False
    logger.error(f"❌ HTP 파이프라인 import 실패: {e}")

router = APIRouter()

class PersonalityType(Enum):
    """성격 유형 Enum"""
    DRIVING = (1, "추진형", "dog_scores")
    INTROSPECTIVE = (2, "내면형", "cat_scores")
    RELATIONAL = (3, "관계형", "rabbit_scores")
    HEDONISTIC = (4, "쾌락형", "bear_scores")
    STABLE = (5, "안정형", "turtle_scores")
    
    def __init__(self, id_: int, korean_name: str, score_field: str):
        self.id = id_
        self.korean_name = korean_name
        self.score_field = score_field

PERSONALITY_MAPPING = {pt.korean_name: pt.id for pt in PersonalityType}
PERSONALITY_REVERSE_MAPPING = {pt.id: pt.korean_name for pt in PersonalityType}
SCORE_FIELD_MAPPING = {pt.korean_name: pt.score_field for pt in PersonalityType}

ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
IMAGE_QUALITY = 95

# ============= Data Classes =============
@dataclass
class AnalysisProgress:
    """분석 진행 상황 데이터 클래스"""
    detection_completed: bool = False
    analysis_completed: bool = False
    classification_completed: bool = False
    
    @property
    def current_step(self) -> int:
        if not self.detection_completed:
            return 1
        elif not self.analysis_completed:
            return 2
        elif not self.classification_completed:
            return 3
        return 3
    
    @property
    def completed_steps(self) -> int:
        return sum([self.detection_completed, self.analysis_completed, self.classification_completed])
    
    @property
    def is_complete(self) -> bool:
        return all([self.detection_completed, self.analysis_completed, self.classification_completed])

# ============= Pipeline Manager =============
class PipelineManager:
    """파이프라인 싱글톤 관리자"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.pipeline = None
        return cls._instance
    
    def get_pipeline(self) -> HTPAnalysisPipeline:
        """파이프라인 인스턴스 가져오기"""
        if not PIPELINE_AVAILABLE:
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "HTP 분석 파이프라인을 사용할 수 없습니다.",
                    "reason": "파이프라인 모듈이 로드되지 않았습니다.",
                    "status": "service_unavailable"
                }
            )
        
        if self.pipeline is None:
            self.pipeline = HTPAnalysisPipeline()
            logger.info("파이프라인 인스턴스 생성 완료")
        
        return self.pipeline

pipeline_manager = PipelineManager()

# ============= Helper Functions =============
async def validate_and_process_image(
    upload_file: UploadFile
) -> tuple[str, Path, PILImage.Image]:
    """
    이미지 파일 검증 및 처리
    
    Returns:
        tuple: (unique_id, save_path, pil_image)
    """
    # 파일 검증
    if not upload_file.content_type or not upload_file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=422,
            detail="지원하지 않는 파일 형식입니다. 이미지 파일을 업로드해주세요."
        )
    
    # 확장자 검증
    file_extension = Path(upload_file.filename).suffix.lower()
    if file_extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=422,
            detail=f"지원하지 않는 이미지 형식입니다. {', '.join(ALLOWED_IMAGE_EXTENSIONS)} 지원"
        )
    
    # 이미지 로드 및 처리
    image_data = await upload_file.read()
    
    # 파일 크기 검증
    if len(image_data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=422,
            detail=f"파일 크기가 {MAX_FILE_SIZE // (1024*1024)}MB를 초과합니다."
        )
    
    pil_image = PILImage.open(io.BytesIO(image_data))
    
    # EXIF 회전 정보 적용
    try:
        pil_image = ImageOps.exif_transpose(pil_image)
    except Exception:
        pass  # EXIF 정보가 없어도 무시
    
    # RGB 모드로 변환
    if pil_image.mode != 'RGB':
        pil_image = pil_image.convert('RGB')
    
    # 고유 ID 생성
    unique_id = str(uuid.uuid4())
    
    # Docker 환경 확인 및 저장 경로 설정
    if Path("/.dockerenv").exists() or os.environ.get("DOCKER_CONTAINER"):
        # Docker 환경
        upload_dir = Path("/app/result/images")
    else:
        # 로컬 환경
        upload_dir = Path.home() / "result" / "images"
    
    upload_dir.mkdir(parents=True, exist_ok=True)
    save_path = upload_dir / f"{unique_id}.jpg"
    logger.info(f"이미지 저장 경로: {save_path}")
    
    return unique_id, save_path, pil_image
def save_images(
    pil_image: PILImage.Image,
    save_path: Path,
    pipeline_path: Optional[Path] = None
) -> None:
    """이미지 저장"""
    # 메인 경로에 저장
    pil_image.save(save_path, 'JPEG', quality=IMAGE_QUALITY)
    
    # 파이프라인 경로에도 저장 (있는 경우)
    if pipeline_path:
        pipeline_path.parent.mkdir(parents=True, exist_ok=True)
        pil_image.save(pipeline_path, 'JPEG', quality=IMAGE_QUALITY)

def extract_analysis_results(result: Any) -> Dict[str, Any]:
    """파이프라인 결과에서 분석 데이터 추출"""
    # 실패 시 None 반환으로 명확히 표시
    data = {
        'persona_type_id': None,  
        'summary_text': None,
        'persona_scores': None,
        'analysis_success': False,
        'error_message': "분석 결과를 처리할 수 없습니다."
    }
    
    if not result or not hasattr(result, 'status'):
        data['error_message'] = "파이프라인 결과가 없습니다."
        return data
    
    # 성공적인 결과 처리
    if result.status == PipelineStatus.SUCCESS:
        data['analysis_success'] = True
        data['error_message'] = None
        data['persona_scores'] = {pt.score_field: 0.0 for pt in PersonalityType}
        
        # 키워드 분석 결과 처리
        if hasattr(result, 'keyword_analysis') and result.keyword_analysis:
            probabilities = result.keyword_analysis.get('probabilities', {})
            if probabilities:
                # 가장 높은 확률의 성격 유형
                highest_type = max(probabilities.items(), key=lambda x: x[1])[0]
                data['persona_type_id'] = PERSONALITY_MAPPING.get(highest_type)
                
                # 점수 매핑
                for p_type, score in probabilities.items():
                    field = SCORE_FIELD_MAPPING.get(p_type)
                    if field:
                        data['persona_scores'][field] = min(score, 999.99)
        
        # 심리 분석 텍스트
        if hasattr(result, 'psychological_analysis') and result.psychological_analysis:
            psych = result.psychological_analysis
            if isinstance(psych, dict) and psych.get('result_text'):
                data['summary_text'] = psych['result_text']
        
        # 필수 데이터 검증
        if data['persona_type_id'] is None:
            data['analysis_success'] = False
            data['error_message'] = "성격 유형을 결정할 수 없습니다."
        if data['summary_text'] is None:
            data['summary_text'] = "심리 분석 결과를 생성할 수 없습니다."
    
    # 오류 메시지 처리
    elif hasattr(result, 'error_message'):
        data['error_message'] = f"분석 오류: {result.error_message}"
    
    return data

# ============= API Endpoints =============
@router.post("/analyze-image")
async def analyze_drawing_image(
    background_tasks: BackgroundTasks,
    file: Optional[UploadFile] = File(None),
    image: Optional[UploadFile] = File(None),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """그림 이미지 분석 API"""
    
    start_time = time.time()
    upload_file = file or image
    
    print(f"🔍 API 엔드포인트 진입 - 함수 시작")
    print(f"📋 요청 파라미터 정보:")
    print(f"  - file: {file}")
    print(f"  - image: {image}")
    print(f"  - upload_file: {upload_file}")
    print(f"  - filename: {getattr(upload_file, 'filename', 'N/A') if upload_file else 'N/A'}")
    print(f"  - content_type: {getattr(upload_file, 'content_type', 'N/A') if upload_file else 'N/A'}")
    print(f"  - description: {description}")
    print(f"  - current_user: {current_user}")
    
    try:
        if not upload_file:
            print(f"❌ 검증 실패: 파일이 업로드되지 않음")
            raise HTTPException(
                status_code=422,
                detail="이미지 파일이 업로드되지 않았습니다. 'file' 또는 'image' 필드에 파일을 첨부해주세요."
            )
        
        print(f"🚀 이미지 분석 요청 시작 - 사용자: {current_user['user_id']}")
        print(f"📁 이미지 파일: {upload_file.filename}, 크기: {upload_file.size if upload_file.size else 'unknown'}, 타입: {upload_file.content_type}")
        print(f"📝 설명: {description}")
        
        if not upload_file.filename:
            print(f"❌ 검증 실패: 파일명이 없음")
            raise HTTPException(
                status_code=422,
                detail="이미지 파일명이 없습니다."
            )
        
        # 1. 파일 검증
        if not upload_file.content_type or not upload_file.content_type.startswith('image/'):
            print(f"❌ 검증 실패: 잘못된 content-type: {upload_file.content_type}")
            raise HTTPException(
                status_code=422,
                detail="지원하지 않는 파일 형식입니다. 이미지 파일을 업로드해주세요."
            )
        
        # 2. 고유 파일명 생성
        file_extension = Path(upload_file.filename).suffix.lower()
        if file_extension not in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
            print(f"❌ 검증 실패: 지원하지 않는 확장자: {file_extension}")
            raise HTTPException(
                status_code=422,
                detail="지원하지 않는 이미지 형식입니다. (.jpg, .jpeg, .png, .bmp, .gif 지원)"
            )
        
        unique_id = str(uuid.uuid4())
        image_filename = f"{unique_id}{file_extension}"
        
        # 3. 다중 해상도 이미지 디렉토리 설정
        backend_root = Path(__file__).parent.parent.parent
        base_dir = backend_root / "result" / "images"
        
        # 다중 해상도별 디렉토리 생성
        original_dir = base_dir / "original"    # 원본 (사용자 조회용)
        yolo_dir = base_dir / "yolo"           # YOLO 분석용 (320x320, q=10)
        web_dir = base_dir / "web"             # 웹 표시용 (640x640, q=85)
        
        for dir_path in [original_dir, yolo_dir, web_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # 4. 파일 경로 설정 (JPG로 통일)
        original_path = original_dir / f"{unique_id}.jpg"
        yolo_path = yolo_dir / f"{unique_id}.jpg"
        web_path = web_dir / f"{unique_id}.jpg"
        
        # 5. 파이프라인용 디렉토리 (기존 호환성 유지)
        pipeline = pipeline_manager.get_pipeline()
        pipeline_upload_dir = pipeline.config.test_img_dir
        pipeline_upload_dir.mkdir(parents=True, exist_ok=True)
        pipeline_image_path = pipeline_upload_dir / f"{unique_id}.jpg"
        
        # 이미지를 JPG 형식으로 변환하여 저장
        import PIL.Image as PILImage
        from PIL import ImageOps
        import io
        
        # 업로드된 파일을 PIL Image로 로드
        image_data = await upload_file.read()
        pil_image = PILImage.open(io.BytesIO(image_data))
        
        # EXIF 회전 정보 자동 적용 (스마트폰 사진 회전 문제 해결)
        try:
            pil_image = ImageOps.exif_transpose(pil_image)
            print(f"✅ EXIF 회전 정보 적용 완료")
        except Exception as e:
            print(f"⚠️ EXIF 회전 정보 적용 실패 (무시 가능): {e}")
        
        # RGB 모드로 변환 (RGBA 등 다른 모드 처리)
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # 다중 해상도 이미지 저장
        print(f"📸 다중 해상도 이미지 저장 시작...")
        
        # 1. 원본 저장 (사용자 조회용, 고품질)
        pil_image.save(original_path, 'JPEG', quality=95, optimize=True)
        print(f"✅ 원본 저장 완료: {original_path}")
        
        # 2. YOLO용 압축 (320x320, quality=10)
        yolo_image = pil_image.copy()
        yolo_image.thumbnail((320, 320), PILImage.Resampling.LANCZOS)
        yolo_image.save(yolo_path, 'JPEG', quality=10, optimize=True)
        print(f"✅ YOLO용 압축 완료: {yolo_path} (320x320, q=10)")
        
        # 3. 웹용 중간 품질 (640x640, quality=85)
        web_image = pil_image.copy()
        web_image.thumbnail((640, 640), PILImage.Resampling.LANCZOS)
        web_image.save(web_path, 'JPEG', quality=85, optimize=True)
        print(f"✅ 웹용 이미지 완료: {web_path} (640x640, q=85)")
        
        # 4. 파이프라인용 디렉토리에 YOLO 압축본 저장 (기존 호환성)
        yolo_image.save(pipeline_image_path, 'JPEG', quality=10, optimize=True)
        print(f"✅ 파이프라인 호환성 저장 완료: {pipeline_image_path}")
        
        # 6. 데이터베이스에 테스트 레코드 생성 (원본 이미지 경로 저장)
        drawing_test = DrawingTest(
            user_id=current_user["user_id"],
            image_url=f"result/images/original/{unique_id}.jpg",  # 원본 이미지 경로
            submitted_at=datetime.now()
        )
        
        db.add(drawing_test)
        db.commit()
        db.refresh(drawing_test)
        
        # 백그라운드 태스크 실행
        background_tasks.add_task(
            run_analysis_pipeline,
            unique_id,
            drawing_test.test_id,
            description
        )
        
        elapsed = time.time() - start_time
        logger.info(f"이미지 업로드 처리 완료: {elapsed:.2f}초")
        
        return JSONResponse(
            status_code=202,
            content={
                "message": "이미지 분석이 시작되었습니다.",
                "test_id": drawing_test.test_id,
                "task_id": unique_id,
                "status": "processing",
                "estimated_time": "2-3분 소요 예상"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"이미지 분석 요청 오류: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"이미지 분석 요청 처리 중 오류가 발생했습니다: {str(e)}"
        )

def run_analysis_pipeline(
    unique_id: str,
    test_id: int,
    description: Optional[str]
):
    """백그라운드 분석 파이프라인 실행"""
    
    db = SessionLocal()
    start_time = time.time()
    
    try:
        logger.info(f"백그라운드 분석 시작: {unique_id}")
        
        # 파이프라인 실행
        pipeline = pipeline_manager.get_pipeline()
        result = pipeline.analyze_image(unique_id)
        
        elapsed = time.time() - start_time
        logger.info(f"파이프라인 실행 완료: {elapsed:.2f}초")
        
        # 결과 저장
        save_analysis_result(result, test_id, description, db)
        
        total_elapsed = time.time() - start_time
        logger.info(f"분석 완료 (총 {total_elapsed:.2f}초): {unique_id}")
        
    except Exception as e:
        logger.error(f"백그라운드 분석 오류: {e}")
        
        # 오류 상태 저장
        try:
            error_result = DrawingTestResult(
                test_id=test_id,
                persona_type=None,
                summary_text=f"분석 중 오류가 발생했습니다: {str(e)}",
                created_at=datetime.now()
            )
            db.add(error_result)
            db.commit()
        except Exception as db_error:
            logger.error(f"오류 상태 저장 실패: {db_error}")
    finally:
        db.close()

def save_analysis_result(
    result: Any,
    test_id: int,
    description: Optional[str],
    db: Session
):
    """분석 결과 데이터베이스 저장"""
    
    try:
        # 결과 추출
        analysis_data = extract_analysis_results(result)
        
        # 분석 실패 시 에러 결과 저장
        if not analysis_data['analysis_success']:
            error_result = DrawingTestResult(
                test_id=test_id,
                persona_type=None,  # NULL로 저장
                summary_text=analysis_data['error_message'],
                created_at=datetime.now(),
                # 모든 점수를 NULL로
                dog_scores=None,
                cat_scores=None,
                rabbit_scores=None,
                bear_scores=None,
                turtle_scores=None
            )
            db.add(error_result)
            db.commit()
            logger.warning(f"분석 실패 결과 저장: test_id={test_id}, error={analysis_data['error_message']}")
            return
        
        # 성공한 경우만 정상 저장
        existing = db.query(DrawingTestResult).filter(
            DrawingTestResult.test_id == test_id
        ).first()
        
        if existing:
            # 업데이트
            existing.persona_type = analysis_data['persona_type_id']
            existing.summary_text = analysis_data['summary_text']
            existing.created_at = datetime.now()
            
            # 점수 업데이트
            for field, value in analysis_data['persona_scores'].items():
                setattr(existing, field, value)
                
            logger.info(f"결과 업데이트: test_id={test_id}")
        else:
            # 신규 생성
            new_result = DrawingTestResult(
                test_id=test_id,
                persona_type=analysis_data['persona_type_id'],
                summary_text=analysis_data['summary_text'],
                created_at=datetime.now(),
                **analysis_data['persona_scores']
            )
            db.add(new_result)
            logger.info(f"새 결과 생성: test_id={test_id}")
        
        db.commit()
        logger.info(f"분석 결과 저장 성공: test_id={test_id}")
        
    except Exception as e:
        logger.error(f"결과 저장 오류: {e}")
        db.rollback()
        
        # 저장 실패 시 에러 상태 기록
        try:
            error_result = DrawingTestResult(
                test_id=test_id,
                persona_type=None,
                summary_text=f"결과 저장 중 오류 발생: {str(e)}",
                created_at=datetime.now()
            )
            db.add(error_result)
            db.commit()
        except:
            pass  # 에러 저장도 실패하면 포기
        
        raise

@router.get("/analysis-status/{test_id}")
async def get_analysis_status(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """분석 상태 조회 API"""
    
    try:
        # 테스트 조회
        drawing_test = db.query(DrawingTest).filter(
            DrawingTest.test_id == test_id,
            DrawingTest.user_id == current_user["user_id"]
        ).first()
        
        if not drawing_test:
            raise HTTPException(status_code=404, detail="테스트를 찾을 수 없습니다.")
        
        # 결과 조회
        test_result = db.query(DrawingTestResult).filter(
            DrawingTestResult.test_id == test_id
        ).first()
        
        if not test_result:
            # 진행 중 상태 반환
            progress = AnalysisProgress()
            
            # 이미지 파일명 추출 (URL에서 파일명 부분만)
            image_url = drawing_test.image_url  # "result/images/original/{unique_id}.jpg"
            if image_url:
                # "result/images/original/uuid.jpg" -> "uuid"
                import re
                match = re.search(r'result/images/original/(.+?)\.jpg', image_url)
                if match:
                    unique_id = match.group(1)
                    status_info = pipeline_manager.get_pipeline().get_analysis_status(unique_id)
                    
                    # 단계별 진행상황 구성
                    detection_completed = status_info.get("detection_completed", False)
                    analysis_completed = status_info.get("analysis_completed", False)
                    classification_completed = status_info.get("classification_completed", False)
                    
                    steps = [
                        {
                            "name": "객체 탐지",
                            "description": "YOLO를 사용한 그림 요소 검출",
                            "completed": detection_completed,
                            "current": not detection_completed
                        },
                        {
                            "name": "심리 분석", 
                            "description": "GPT-4를 사용한 심리상태 분석",
                            "completed": analysis_completed,
                            "current": detection_completed and not analysis_completed
                        },
                        {
                            "name": "성격 분류",
                            "description": "키워드 분류기를 사용한 성격유형 분류", 
                            "completed": classification_completed,
                            "current": analysis_completed and not classification_completed
                        }
                    ]
                    
                    # 현재 진행 중인 단계 찾기
                    current_step = next((i+1 for i, step in enumerate(steps) if step["current"]), 1)
                    completed_steps = sum(1 for step in steps if step["completed"])
                    
                    # 모든 단계가 완료되었는지 확인
                    if classification_completed:
                        # 3단계 모두 완료된 경우, 최종 결과가 DB에 저장될 때까지 잠시 대기
                        print(f"🎯 모든 단계 완료됨 - 최종 결과 대기 중")
                        return JSONResponse(content={
                            "test_id": test_id,
                            "status": "processing",
                            "message": "최종 결과 생성 중...",
                            "steps": steps,
                            "current_step": 3,
                            "completed_steps": 3,
                            "total_steps": 3,
                            "estimated_remaining": "잠시만 기다려주세요"
                        })
                    
                    return JSONResponse(content={
                        "test_id": test_id,
                        "status": "processing",
                        "message": f"단계 {current_step}/3 진행 중...",
                        "steps": steps,
                        "current_step": current_step,
                        "completed_steps": completed_steps,
                        "total_steps": 3,
                        "estimated_remaining": f"{4-completed_steps}분 소요 예상"
                    })
            
            # 기본 응답 (파일명 추출 실패 시)
            default_steps = [
                {
                    "name": "객체 탐지",
                    "description": "YOLO를 사용한 그림 요소 검출",
                    "completed": progress.detection_completed,
                    "current": not progress.detection_completed
                },
                {
                    "name": "심리 분석", 
                    "description": "GPT-4를 사용한 심리상태 분석",
                    "completed": progress.analysis_completed,
                    "current": progress.detection_completed and not progress.analysis_completed
                },
                {
                    "name": "성격 분류",
                    "description": "키워드 분류기를 사용한 성격유형 분류", 
                    "completed": progress.classification_completed,
                    "current": progress.analysis_completed and not progress.classification_completed
                }
            ]
            
            return JSONResponse(content={
                "test_id": test_id,
                "status": "processing",
                "message": f"단계 {progress.current_step}/3 진행 중...",
                "steps": default_steps,
                "current_step": progress.current_step,
                "completed_steps": progress.completed_steps,
                "total_steps": 3,
                "estimated_remaining": f"{3 - progress.completed_steps}분 소요 예상"
            })
        
        # 완료된 결과 반환
        # NULL 체크 - 분석 실패한 경우
        if test_result.persona_type is None:
            return JSONResponse(
                status_code=200,
                content={
                    "test_id": test_id,
                    "status": "failed",
                    "message": "분석에 실패했습니다.",
                    "error": test_result.summary_text,
                    "result": None
                }
            )
        
        # 정상 결과 반환
        probabilities = {
            "추진형": float(test_result.dog_scores or 0.0),
            "내면형": float(test_result.cat_scores or 0.0),
            "관계형": float(test_result.rabbit_scores or 0.0),
            "쾌락형": float(test_result.bear_scores or 0.0),
            "안정형": float(test_result.turtle_scores or 0.0)
        }
        
        # 예측된 성격 유형 결정
        if probabilities and any(probabilities.values()):
            predicted_personality = max(probabilities.items(), key=lambda x: x[1])[0]
        elif test_result.persona_type in PERSONALITY_REVERSE_MAPPING:
            predicted_personality = PERSONALITY_REVERSE_MAPPING[test_result.persona_type]
        else:
            # 이 경우는 발생하면 안 됨 (데이터 무결성 문제)
            logger.error(f"Invalid persona_type in DB: {test_result.persona_type}")
            return JSONResponse(
                status_code=500,
                content={
                    "test_id": test_id,
                    "status": "error",
                    "message": "데이터 무결성 오류",
                    "error": "유효하지 않은 성격 유형 ID"
                }
            )
        
        return JSONResponse(content={
            "test_id": test_id,
            "status": "completed",
            "message": "분석이 완료되었습니다.",
            "steps": [
                {"name": "객체 탐지", "completed": True, "current": False},
                {"name": "심리 분석", "completed": True, "current": False},
                {"name": "성격 분류", "completed": True, "current": False}
            ],
            "current_step": 3,
            "completed_steps": 3,
            "total_steps": 3,
            "result": {
                "persona_type": test_result.persona_type,
                "summary_text": test_result.summary_text,
                "predicted_personality": predicted_personality,
                "probabilities": probabilities,
                "created_at": test_result.created_at.isoformat() if test_result.created_at else None,
                "image_url": drawing_test.image_url
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"상태 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="분석 상태 조회 중 오류가 발생했습니다.")

@router.get("/pipeline-health")
async def check_pipeline_health():
    """파이프라인 상태 확인 API"""
    
    status = {
        "pipeline_status": "unknown",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "pipeline_import": PIPELINE_AVAILABLE,
            "yolo_model": False,
            "openai_api": False,
            "kobert_model": False,
            "directories": False
        },
        "directories": {},
        "error_details": None
    }
    
    if PIPELINE_AVAILABLE:
        try:
            pipeline = pipeline_manager.get_pipeline()
            
            # 디렉토리 정보
            status["directories"] = {
                "test_images": str(pipeline.config.test_img_dir),
                "detection_results": str(pipeline.config.detection_results_dir),
                "rag_docs": str(pipeline.config.rag_dir)
            }
            
            # 컴포넌트 상태 확인
            yolo_path = pipeline.config.model_dir / pipeline.config.yolo_model_path
            status["components"]["yolo_model"] = yolo_path.exists()
            
            status["components"]["openai_api"] = bool(os.getenv('OPENAI_API_KEY'))
            
            kobert_path = pipeline.config.model_dir / pipeline.config.kobert_model_path
            status["components"]["kobert_model"] = kobert_path.exists()
            
            required_dirs = [
                pipeline.config.test_img_dir,
                pipeline.config.detection_results_dir,
                pipeline.config.rag_dir
            ]
            status["components"]["directories"] = all(d.exists() for d in required_dirs)
            
            # 전체 상태 판단
            all_healthy = all(status["components"].values())
            status["pipeline_status"] = "healthy" if all_healthy else "degraded"
            
        except Exception as e:
            status["pipeline_status"] = "error"
            status["error_details"] = str(e)
    else:
        status["pipeline_status"] = "unavailable"
        status["error_details"] = "파이프라인 모듈을 로드할 수 없습니다."
    
    return JSONResponse(content=status)