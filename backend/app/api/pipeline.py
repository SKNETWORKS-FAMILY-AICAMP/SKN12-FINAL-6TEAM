"""
거북이상담소 HTP 심리검사 파이프라인 API

이 모듈은 프론트엔드에서 이미지 분석 요청을 처리하는 API 엔드포인트를 제공합니다.
TestPage.tsx에서 버튼 클릭 시 호출되는 통합 파이프라인 인터페이스입니다.
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import os
import uuid
import json
import asyncio
from datetime import datetime
from pathlib import Path

# 내부 모듈
from ..database import get_db
from ..models.test import DrawingTest, DrawingTestResult
from ..models.user import UserInformation
from ..schemas.test import DrawingTestCreate, DrawingTestResultCreate
from .auth import get_current_user

# HTP 파이프라인 모듈 (절대 경로로 import)
import sys
project_root = Path(__file__).parent.parent.parent
pipeline_module_path = project_root / 'llm' / 'model'
sys.path.insert(0, str(pipeline_module_path))

try:
    from main import HTPAnalysisPipeline, PipelineStatus, PipelineResult
except ImportError as e:
    HTPAnalysisPipeline = None

router = APIRouter()

# 전역 파이프라인 인스턴스
pipeline_instance: Optional[HTPAnalysisPipeline] = None

def get_pipeline() -> HTPAnalysisPipeline:
    """파이프라인 인스턴스 가져오기 (싱글톤 패턴)"""
    global pipeline_instance
    if pipeline_instance is None:
        if HTPAnalysisPipeline is None:
            raise HTTPException(
                status_code=500, 
                detail="HTP 분석 파이프라인을 로드할 수 없습니다."
            )
        pipeline_instance = HTPAnalysisPipeline()
    return pipeline_instance


@router.post("/analyze-image")
async def analyze_drawing_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    그림 이미지 분석 API
    
    TestPage.tsx의 '분석 시작하기' 버튼에서 호출됩니다.
    업로드된 이미지를 HTP 심리검사 파이프라인으로 처리합니다.
    
    Args:
        file: 업로드된 이미지 파일
        description: 사용자가 입력한 그림 설명 (선택사항)
        db: 데이터베이스 세션
        current_user: 현재 로그인한 사용자
        
    Returns:
        JSON: 분석 작업 시작 응답 및 작업 ID
    """
    print(f"🔍 API 엔드포인트 진입 - 함수 시작")
    print(f"📋 요청 파라미터 정보:")
    print(f"  - file: {file}")
    print(f"  - file.filename: {getattr(file, 'filename', 'N/A')}")
    print(f"  - file.content_type: {getattr(file, 'content_type', 'N/A')}")
    print(f"  - description: {description}")
    print(f"  - current_user: {current_user}")
    
    try:
        print(f"🚀 이미지 분석 요청 시작 - 사용자: {current_user['user_id']}")
        print(f"📁 이미지 파일: {file.filename}, 크기: {file.size if file.size else 'unknown'}, 타입: {file.content_type}")
        print(f"📝 설명: {description}")
        
        if not file.filename:
            print(f"❌ 검증 실패: 파일명이 없음")
            raise HTTPException(
                status_code=422,
                detail="이미지 파일명이 없습니다."
            )
        
        # 1. 파일 검증
        if not file.content_type or not file.content_type.startswith('image/'):
            print(f"❌ 검증 실패: 잘못된 content-type: {file.content_type}")
            raise HTTPException(
                status_code=422,
                detail="지원하지 않는 파일 형식입니다. 이미지 파일을 업로드해주세요."
            )
        
        # 2. 고유 파일명 생성
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
            print(f"❌ 검증 실패: 지원하지 않는 확장자: {file_extension}")
            raise HTTPException(
                status_code=422,
                detail="지원하지 않는 이미지 형식입니다. (.jpg, .jpeg, .png, .bmp, .gif 지원)"
            )
        
        unique_id = str(uuid.uuid4())
        image_filename = f"{unique_id}{file_extension}"
        
        # 3. 업로드 디렉토리 설정 (backend/result/images)
        backend_root = Path(__file__).parent.parent.parent
        upload_dir = backend_root / "result" / "images"
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # 4. 파일 저장 (JPG로 통일)
        image_path = upload_dir / f"{unique_id}.jpg"
        
        # 5. 파이프라인용 디렉토리에도 복사 (기존 분석 파이프라인 호환성)
        pipeline = get_pipeline()
        pipeline_upload_dir = pipeline.config.test_img_dir
        pipeline_upload_dir.mkdir(parents=True, exist_ok=True)
        pipeline_image_path = pipeline_upload_dir / f"{unique_id}.jpg"
        
        # 이미지를 JPG 형식으로 변환하여 저장
        import PIL.Image as PILImage
        import io
        
        # 업로드된 파일을 PIL Image로 로드
        image_data = await file.read()
        pil_image = PILImage.open(io.BytesIO(image_data))
        
        # RGB 모드로 변환 (RGBA 등 다른 모드 처리)
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # JPG로 저장 (backend/result/images)
        pil_image.save(image_path, 'JPEG', quality=95)
        
        # 파이프라인용 디렉토리에도 저장
        pil_image.save(pipeline_image_path, 'JPEG', quality=95)
        
        # 6. 데이터베이스에 테스트 레코드 생성
        drawing_test = DrawingTest(
            user_id=current_user["user_id"],
            image_url=f"result/images/{unique_id}.jpg",  # backend/result/images 경로
            submitted_at=datetime.now()
        )
        
        db.add(drawing_test)
        db.commit()
        db.refresh(drawing_test)
        
        # 7. 백그라운드에서 분석 실행
        background_tasks.add_task(
            run_analysis_pipeline,
            unique_id,
            drawing_test.test_id,
            description,
            db
        )
        
        return JSONResponse(
            status_code=202,  # Accepted
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
        raise HTTPException(
            status_code=500,
            detail=f"이미지 분석 요청 처리 중 오류가 발생했습니다: {str(e)}"
        )


async def run_analysis_pipeline(
    unique_id: str,
    test_id: int,
    description: Optional[str],
    db: Session
):
    """
    백그라운드에서 실행되는 HTP 분석 파이프라인
    
    Args:
        unique_id: 고유 이미지 ID
        test_id: 데이터베이스 테스트 ID
        description: 사용자 설명
        db: 데이터베이스 세션
    """
    try:
        # 파이프라인 실행
        pipeline = get_pipeline()
        result: PipelineResult = pipeline.analyze_image(unique_id)
        
        # 결과를 데이터베이스에 저장
        await save_analysis_result(result, test_id, description, db)
        
    except Exception as e:
        # 오류 발생 시 데이터베이스에 오류 상태 저장
        try:
            pipeline = get_pipeline()
            pipeline.logger.error(f"백그라운드 분석 오류: {str(e)}")
        except:
            print(f"백그라운드 분석 오류: {str(e)}")
        
        # 빈 결과로 오류 상태 저장
        error_result = DrawingTestResult(
            test_id=test_id,
            friends_type=None,
            summary_text=f"분석 중 오류가 발생했습니다: {str(e)}",
            created_at=datetime.now()
        )
        
        db.add(error_result)
        db.commit()


async def save_analysis_result(
    result: PipelineResult,
    test_id: int,
    description: Optional[str],
    db: Session
):
    """
    분석 결과를 데이터베이스에 저장
    
    Args:
        result: 파이프라인 분석 결과
        test_id: 데이터베이스 테스트 ID
        description: 사용자 설명
        db: 데이터베이스 세션
    """
    try:
        # 파이프라인 인스턴스 가져오기
        pipeline = get_pipeline()
        
        # 성격 유형을 friends 테이블의 ID로 매핑
        personality_mapping = {
            "추진형": 1,  # 추진이
            "내면형": 2,  # 내면이  
            "관계형": 3,  # 관계이
            "쾌락형": 4,  # 쾌락이
            "안정형": 5   # 안정이
        }
        
        friends_type_id = None
        summary_text = "분석을 완료할 수 없습니다."
        
        if result.status == PipelineStatus.SUCCESS and result.personality_type:
            friends_type_id = personality_mapping.get(result.personality_type)
            
            # result 파일에서 확률 정보 가져오기
            result_file_path = pipeline.config.detection_results_dir / "results" / f"result_{result.image_base}.json"
            probabilities = None
            if result_file_path.exists():
                try:
                    with open(result_file_path, 'r', encoding='utf-8') as f:
                        result_data = json.load(f)
                        personality_analysis = result_data.get('personality_analysis', {})
                        probabilities = personality_analysis.get('probabilities', {})
                except Exception as e:
                    pipeline.logger.warning(f"result 파일 읽기 실패: {e}")
            
            # 상세 분석 결과 구성
            summary_parts = []
            
            if result.psychological_analysis:
                analysis = result.psychological_analysis
                summary_parts.append(f"🎯 성격 유형: {result.personality_type}")
                summary_parts.append(f"📊 신뢰도: {result.confidence_score:.1%}")
                summary_parts.append("")
                
                # 확률 정보 추가
                if probabilities:
                    summary_parts.append("📈 유형별 확률 분석:")
                    for persona_type, prob in sorted(probabilities.items(), key=lambda x: -x[1]):
                        summary_parts.append(f"• {persona_type}: {prob:.1f}%")
                    summary_parts.append("")
                
                if analysis.get('result_text'):
                    summary_parts.append("📋 심리 분석 요약:")
                    summary_parts.append(analysis['result_text'])
                    summary_parts.append("")
                
                if analysis.get('items') and isinstance(analysis['items'], list):
                    summary_parts.append("🔍 세부 분석 요소:")
                    for item in analysis['items'][:5]:  # 최대 5개 항목만 표시
                        if isinstance(item, dict):
                            element = item.get('element', 'N/A')
                            condition = item.get('condition', 'N/A')
                            keywords = item.get('keywords', [])
                            if isinstance(keywords, list) and keywords:
                                keyword_str = ', '.join(keywords[:3])  # 최대 3개 키워드
                                summary_parts.append(f"• {element}: {condition} ({keyword_str})")
            
            if description:
                summary_parts.append("")
                summary_parts.append("💭 사용자 설명:")
                summary_parts.append(description)
            
            summary_text = "\n".join(summary_parts)
            
        elif result.error_message:
            summary_text = f"분석 중 오류가 발생했습니다: {result.error_message}"
        
        # 결과 저장 (upsert 패턴)
        existing_result = db.query(DrawingTestResult).filter(
            DrawingTestResult.test_id == test_id
        ).first()
        
        if existing_result:
            # 기존 결과 업데이트
            existing_result.friends_type = friends_type_id
            existing_result.summary_text = summary_text
            existing_result.created_at = datetime.now()
        else:
            # 새 결과 생성
            test_result = DrawingTestResult(
                test_id=test_id,
                friends_type=friends_type_id,
                summary_text=summary_text,
                created_at=datetime.now()
            )
            db.add(test_result)
        
        db.commit()
        
    except Exception as e:
        db.rollback()
        try:
            pipeline.logger.error(f"분석 결과 저장 오류: {str(e)}")
        except:
            print(f"분석 결과 저장 오류: {str(e)}")
        raise


@router.get("/analysis-status/{test_id}")
async def get_analysis_status(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    분석 상태 조회 API
    
    프론트엔드에서 분석 진행 상황을 확인할 때 사용합니다.
    
    Args:
        test_id: 테스트 ID
        db: 데이터베이스 세션
        current_user: 현재 사용자
        
    Returns:
        JSON: 분석 상태 정보
    """
    try:
        # 테스트 레코드 조회
        drawing_test = db.query(DrawingTest).filter(
            DrawingTest.test_id == test_id,
            DrawingTest.user_id == current_user["user_id"]
        ).first()
        
        if not drawing_test:
            raise HTTPException(
                status_code=404,
                detail="해당 테스트를 찾을 수 없습니다."
            )
        
        # 결과 조회
        test_result = db.query(DrawingTestResult).filter(
            DrawingTestResult.test_id == test_id
        ).first()
        
        if not test_result:
            # 파이프라인 진행상황 확인
            pipeline = get_pipeline()
            
            # 이미지 파일명 추출 (URL에서 파일명 부분만)
            image_url = drawing_test.image_url  # "result/images/{unique_id}.jpg"
            if image_url:
                # "result/images/uuid.jpg" -> "uuid"
                import re
                match = re.search(r'result/images/(.+?)\.jpg', image_url)
                if match:
                    unique_id = match.group(1)
                    status_info = pipeline.get_analysis_status(unique_id)
                    
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
                            "description": "KoBERT를 사용한 성격유형 분류", 
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
            return JSONResponse(content={
                "test_id": test_id,
                "status": "processing", 
                "message": "분석이 진행 중입니다...",
                "steps": [
                    {"name": "객체 탐지", "description": "그림 요소 검출 중", "completed": False, "current": True},
                    {"name": "심리 분석", "description": "심리상태 분석 대기 중", "completed": False, "current": False},
                    {"name": "성격 분류", "description": "성격유형 분류 대기 중", "completed": False, "current": False}
                ],
                "current_step": 1,
                "completed_steps": 0,
                "total_steps": 3,
                "estimated_remaining": "2-3분"
            })
        
        # result 파일에서 추가 데이터 읽기
        pipeline = get_pipeline()
        image_url = drawing_test.image_url
        result_text = None
        predicted_personality = None
        probabilities = {}
        
        if image_url:
            import re
            match = re.search(r'result/images/(.+?)\.jpg', image_url)
            if match:
                unique_id = match.group(1)
                result_file_path = pipeline.config.detection_results_dir / "results" / f"result_{unique_id}.json"
                
                if result_file_path.exists():
                    try:
                        with open(result_file_path, 'r', encoding='utf-8') as f:
                            result_data = json.load(f)
                            result_text = result_data.get('result_text', '')
                            personality_analysis = result_data.get('personality_analysis', {})
                            predicted_personality = personality_analysis.get('predicted_personality', '')
                            probabilities = personality_analysis.get('probabilities', {})
                    except Exception as e:
                        pipeline.logger.warning(f"result 파일 읽기 실패: {e}")

        # 분석 완료
        return JSONResponse(content={
            "test_id": test_id,
            "status": "completed",
            "message": "분석이 완료되었습니다.",
            "steps": [
                {"name": "객체 탐지", "description": "YOLO를 사용한 그림 요소 검출", "completed": True, "current": False},
                {"name": "심리 분석", "description": "GPT-4를 사용한 심리상태 분석", "completed": True, "current": False},
                {"name": "성격 분류", "description": "KoBERT를 사용한 성격유형 분류", "completed": True, "current": False}
            ],
            "current_step": 3,
            "completed_steps": 3,
            "total_steps": 3,
            "result": {
                "friends_type": test_result.friends_type,
                "summary_text": test_result.summary_text,
                "result_text": result_text,
                "predicted_personality": predicted_personality,
                "probabilities": probabilities,
                "created_at": test_result.created_at.isoformat() if test_result.created_at else None
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"분석 상태 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/pipeline-health")
async def check_pipeline_health():
    """
    파이프라인 상태 확인 API
    
    시스템 관리자가 파이프라인 구성 요소의 상태를 확인할 때 사용합니다.
    
    Returns:
        JSON: 파이프라인 상태 정보
    """
    try:
        pipeline = get_pipeline()
        
        # 각 구성 요소 상태 확인
        status = {
            "pipeline_status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "yolo_model": False,
                "openai_api": False,
                "kobert_model": False,
                "directories": False
            },
            "directories": {
                "test_images": str(pipeline.config.test_img_dir),
                "detection_results": str(pipeline.config.detection_results_dir),
                "rag_docs": str(pipeline.config.rag_dir)
            }
        }
        
        # YOLO 모델 확인
        yolo_path = pipeline.config.model_dir / pipeline.config.yolo_model_path
        status["components"]["yolo_model"] = yolo_path.exists()
        
        # OpenAI API 키 확인
        status["components"]["openai_api"] = bool(os.getenv('OPENAI_API_KEY'))
        
        # KoBERT 모델 확인
        kobert_path = pipeline.config.model_dir / pipeline.config.kobert_model_path
        status["components"]["kobert_model"] = kobert_path.exists()
        
        # 디렉토리 확인
        required_dirs = [
            pipeline.config.test_img_dir,
            pipeline.config.detection_results_dir,
            pipeline.config.rag_dir
        ]
        status["components"]["directories"] = all(d.exists() for d in required_dirs)
        
        # 전체 상태 판단
        all_healthy = all(status["components"].values())
        status["pipeline_status"] = "healthy" if all_healthy else "degraded"
        
        return JSONResponse(content=status)
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "pipeline_status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )