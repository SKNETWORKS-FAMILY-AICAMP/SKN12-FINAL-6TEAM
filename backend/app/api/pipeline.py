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
    PIPELINE_IMPORT_ERROR = None
    print("✅ HTP 파이프라인 모듈 import 성공")
except Exception as e:
    import sys
    error_msg = str(e)
    print(f"❌ HTP 파이프라인 import 실패: {e}", file=sys.stderr)
    
    if "numpy.dtype size changed" in error_msg:
        print(f"💡 numpy/pandas 버전 충돌 해결방법:", file=sys.stderr)
        print(f"   conda install -c conda-forge numpy pandas --force-reinstall", file=sys.stderr)
        print(f"   또는 pip uninstall numpy pandas -y && pip install numpy pandas", file=sys.stderr)
    else:
        print(f"💡 일반적인 해결방법:", file=sys.stderr)
        print(f"   pip install pandas transformers ultralytics torch opencv-python scikit-learn", file=sys.stderr)
    
    HTPAnalysisPipeline = None
    PipelineStatus = None
    PipelineResult = None
    PIPELINE_IMPORT_ERROR = error_msg

router = APIRouter()

# 전역 파이프라인 인스턴스
pipeline_instance= None

def get_pipeline():
    """파이프라인 인스턴스 가져오기 (싱글톤 패턴)"""
    global pipeline_instance
    if pipeline_instance is None:
        if HTPAnalysisPipeline is None:
            missing_packages = ["pandas", "transformers", "ultralytics", "torch", "opencv-python", "scikit-learn"]
            raise HTTPException(
                status_code=503,  # Service Unavailable
                detail={
                    "error": "HTP 분석 파이프라인을 사용할 수 없습니다.",
                    "reason": "필수 패키지가 설치되지 않았습니다.",
                    "missing_packages": missing_packages,
                    "install_command": f"pip install {' '.join(missing_packages)}",
                    "status": "service_unavailable"
                }
            )
        pipeline_instance = HTPAnalysisPipeline()
    return pipeline_instance


@router.post("/analyze-image")
async def analyze_drawing_image(
    background_tasks: BackgroundTasks,
    file: Optional[UploadFile] = File(None),
    image: Optional[UploadFile] = File(None),
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
    # file 또는 image 중 하나를 사용 (프론트엔드 호환성)
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
        image_data = await upload_file.read()
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
            description
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


def run_analysis_pipeline(
    unique_id: str,
    test_id: int,
    description: Optional[str]
):
    """
    백그라운드에서 실행되는 HTP 분석 파이프라인
    
    3단계 프로세스:
    1. YOLO 객체 탐지
    2. GPT-4 3단계 심리 분석 (관찰→해석→키워드)
    3. 키워드 기반 성격 분류
    
    Args:
        unique_id: 고유 이미지 ID
        test_id: 데이터베이스 테스트 ID
        description: 사용자 설명
    """
    # 백그라운드 태스크용 새 DB 세션 생성 (HTTP 요청 세션과 독립적)
    from ..database import SessionLocal
    db = SessionLocal()
    
    try:
        print(f"🚀 백그라운드 분석 시작: {unique_id}")
        print(f"📋 3단계 분석 프로세스 시작")
        
        # 파이프라인 실행
        pipeline = get_pipeline()
        result: PipelineResult = pipeline.analyze_image(unique_id)
        
        print(f"📊 파이프라인 실행 완료: {result.status}")
        
        # 결과를 데이터베이스에 저장 (동기 함수로 변경)
        print(f"🔥 save_analysis_result_sync 함수 호출 시작 - test_id: {test_id}")
        save_analysis_result_sync(result, test_id, description, db)
        print(f"🔥 save_analysis_result_sync 함수 호출 완료 - test_id: {test_id}")
        
        print(f"✅ 3단계 분석 완료 및 저장: {unique_id}")
        
    except Exception as e:
        print(f"❌ 백그라운드 분석 오류: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # 오류 발생 시 데이터베이스에 오류 상태 저장
        try:
            pipeline = get_pipeline()
            pipeline.logger.error(f"백그라운드 분석 오류: {str(e)}")
        except:
            print(f"파이프라인 로거 사용 불가: {str(e)}")
        
        # 빈 결과로 오류 상태 저장
        try:
            error_result = DrawingTestResult(
                test_id=test_id,
                persona_type=None,
                summary_text=f"분석 중 오류가 발생했습니다: {str(e)}",
                created_at=datetime.now()
            )
            
            db.add(error_result)
            db.commit()
            print(f"오류 상태 저장 완료: {test_id}")
        except Exception as db_error:
            print(f"오류 상태 저장 실패: {db_error}")
    finally:
        db.close()



def save_analysis_result_sync(
    result: Any,  # PipelineResult가 None일 수 있으므로 Any 사용
    test_id: int,
    description: Optional[str],
    db: Session
):
    """
    분석 결과를 데이터베이스에 저장 (간소화된 직접 저장 버전)
    JSON 파일 의존성 제거하고 파이프라인 결과를 직접 활용
    
    Args:
        result: 파이프라인 분석 결과
        test_id: 데이터베이스 테스트 ID
        description: 사용자 설명
        db: 데이터베이스 세션
    """
    print(f"🔥 save_analysis_result_sync 함수 진입 - test_id: {test_id}")
    
    try:
        # 파이프라인 인스턴스 가져오기
        pipeline = get_pipeline()
        
        # 성격 유형을 personas 테이블의 ID로 매핑
        personality_mapping = {
            "추진형": 1,  # 추진이
            "내면형": 2,  # 내면이  
            "관계형": 3,  # 관계이
            "쾌락형": 4,  # 쾌락이
            "안정형": 5   # 안정이
        }
        
        # 기본값 설정
        persona_type_id = 2  # 기본값: 내면형
        summary_text = "분석을 완료할 수 없습니다."
        persona_scores = {
            'dog_scores': 0.0,     # 추진형
            'cat_scores': 0.0,     # 내면형
            'rabbit_scores': 0.0,  # 관계형
            'bear_scores': 0.0,    # 쾌락형
            'turtle_scores': 0.0   # 안정형
        }
        
        # 파이프라인 결과가 성공적인 경우 처리
        if (PipelineStatus is not None and 
            hasattr(result, 'status') and 
            result.status == PipelineStatus.SUCCESS):
            
            print(f"📊 파이프라인 결과 처리 시작")
            
            # 1. 키워드 분석 결과 우선 처리 (result 객체에 직접 포함된 경우)
            if hasattr(result, 'keyword_analysis') and result.keyword_analysis:
                keyword_data = result.keyword_analysis
                print(f"🔍 키워드 분석 데이터 발견: {keyword_data}")
                
                predicted_personality = keyword_data.get('predicted_personality')
                confidence = keyword_data.get('confidence', 0.0)
                probabilities = keyword_data.get('probabilities', {})
                
                if probabilities:
                    # 확률에서 가장 높은 유형 찾기
                    highest_prob_type = max(probabilities.items(), key=lambda x: x[1])[0]
                    highest_prob_value = probabilities[highest_prob_type]
                    
                    # 최고 확률 유형을 persona_type_id로 매핑
                    persona_type_id = personality_mapping.get(highest_prob_type, 2)
                    
                    # 확률값을 DB 필드에 매핑 (DECIMAL(5,2) 제한에 맞게 변환: 최대 999.99)
                    persona_scores.update({
                        'dog_scores': round(min(probabilities.get('추진형', 0.0), 999.99), 2),
                        'cat_scores': round(min(probabilities.get('내면형', 0.0), 999.99), 2),
                        'rabbit_scores': round(min(probabilities.get('관계형', 0.0), 999.99), 2),
                        'bear_scores': round(min(probabilities.get('쾌락형', 0.0), 999.99), 2),
                        'turtle_scores': round(min(probabilities.get('안정형', 0.0), 999.99), 2)
                    })
                    
                    print(f"✅ 키워드 분석 결과 적용:")
                    print(f"  - 최고 확률 유형: {highest_prob_type} ({highest_prob_value:.1f}%)")
                    print(f"  - persona_type_id: {persona_type_id}")
                    print(f"  - 확률 분포: {probabilities}")
            
            # 2. 기본 성격 유형 결과 처리
            elif hasattr(result, 'personality_type') and result.personality_type:
                persona_type_id = personality_mapping.get(result.personality_type, 2)
                print(f"📝 기본 성격 유형 적용: {result.personality_type} -> ID: {persona_type_id}")
            
            # 3. GPT 심리 분석 텍스트만 처리 (키워드/기본 분석 정보 제외)
            summary_text = "성격 유형 분석이 완료되었습니다."  # 기본값
            
            if hasattr(result, 'psychological_analysis') and result.psychological_analysis:
                psych_analysis = result.psychological_analysis
                if isinstance(psych_analysis, dict) and psych_analysis.get('result_text'):
                    # GPT 심리 분석 결과만 사용 (다른 정보 추가 없이)
                    summary_text = psych_analysis['result_text']
                    print(f"📄 GPT 심리 분석 텍스트만 사용 (기타 정보 제외)")
                else:
                    print(f"⚠️ GPT 심리 분석 결과가 비어있음")
            else:
                print(f"⚠️ psychological_analysis 데이터가 없음")
            
            print(f"📝 최종 summary_text 생성 완료 (길이: {len(summary_text)}자)")
            print(f"📝 내용 미리보기: {summary_text[:100]}..." if len(summary_text) > 100 else f"📝 전체 내용: {summary_text}")
        
        # 오류 처리 (기존 로직 유지)
        elif hasattr(result, 'error_message') and result.error_message:
            summary_text = f"분석 중 오류가 발생했습니다: {result.error_message}"
            print(f"❌ 오류 메시지: {result.error_message}")
        
        else:
            # 기본 메시지 사용 (이미 설정된 summary_text 사용)
            print(f"⚠️ 파이프라인 결과가 예상과 다름. result 객체 속성: {dir(result) if result else 'None'}")
            print(f"📝 기본 summary_text 사용: {summary_text}")
        
        # 결과 저장 (upsert 패턴)
        existing_result = db.query(DrawingTestResult).filter(
            DrawingTestResult.test_id == test_id
        ).first()
        
        print(f"💾 DB 저장 전 최종 확인:")
        print(f"  - persona_type_id: {persona_type_id}")
        print(f"  - test_id: {test_id}")
        print(f"  - persona_scores: {persona_scores}")
        print(f"  - summary_text 길이: {len(summary_text)}자")
        print(f"  - summary_text 샘플: {summary_text[:50]}..." if len(summary_text) > 50 else f"  - summary_text: {summary_text}")
        
        # DECIMAL 제한 검증 및 조정
        for key, value in persona_scores.items():
            if value > 999.99:
                print(f"⚠️ {key} 값이 DECIMAL(5,2) 제한을 초과함: {value} -> 999.99로 조정")
                persona_scores[key] = 999.99
        
        print(f"📊 조정된 persona_scores: {persona_scores}")
            
        if existing_result:
            # 기존 결과 업데이트
            print(f"🔄 기존 결과 업데이트 - 이전 persona_type: {existing_result.persona_type}")
            existing_result.persona_type = persona_type_id
            existing_result.summary_text = summary_text
            existing_result.created_at = datetime.now()
            
            # 확률 점수 업데이트 (안전한 값으로)
            existing_result.dog_scores = persona_scores['dog_scores']
            existing_result.cat_scores = persona_scores['cat_scores'] 
            existing_result.rabbit_scores = persona_scores['rabbit_scores']
            existing_result.bear_scores = persona_scores['bear_scores']
            existing_result.turtle_scores = persona_scores['turtle_scores']
            
            print(f"🔄 업데이트할 점수들: {persona_scores}")
            print(f"🔄 업데이트할 summary_text 미리보기: {summary_text[:100]}..." if len(summary_text) > 100 else f"🔄 업데이트할 summary_text: {summary_text}")
            
            print(f"🔄 업데이트 완료 - 새 persona_type: {existing_result.persona_type}")
        else:
            # 새 결과 생성
            print(f"🆕 새 결과 생성")
            test_result_data = {
                'test_id': test_id,
                'persona_type': persona_type_id,
                'summary_text': summary_text,
                'created_at': datetime.now(),
                'dog_scores': persona_scores['dog_scores'],
                'cat_scores': persona_scores['cat_scores'],
                'rabbit_scores': persona_scores['rabbit_scores'],
                'bear_scores': persona_scores['bear_scores'],
                'turtle_scores': persona_scores['turtle_scores']
            }
            
            print(f"🆕 새로 생성할 데이터: test_id={test_id}, persona_type={persona_type_id}")
            print(f"🆕 점수 데이터: {persona_scores}")
            print(f"🆕 새 summary_text 미리보기: {summary_text[:100]}..." if len(summary_text) > 100 else f"🆕 새 summary_text: {summary_text}")
            
            test_result = DrawingTestResult(**test_result_data)
            db.add(test_result)
            print(f"🆕 새 결과 DB에 추가됨 - persona_type: {persona_type_id}")
        
        print(f"💾 DB commit 시작...")
        
        try:
            db.commit()
            print(f"✅ DB commit 성공! 분석 결과가 성공적으로 저장되었습니다.")
            print(f"✅ 최종 저장된 summary_text: GPT 심리 분석 결과만 포함 ({len(summary_text)}자)")
        except Exception as commit_error:
            print(f"❌ DB commit 오류: {str(commit_error)}")
            db.rollback()
            raise commit_error
        
        # 파이프라인 로거에 성공 로그 기록
        try:
            pipeline.logger.info(f"분석 결과 저장 성공 - test_id: {test_id}, persona_type: {persona_type_id}")
        except:
            print(f"로거 사용 불가, 콘솔에 기록: test_id: {test_id}, persona_type: {persona_type_id}")
        
    except Exception as e:
        print(f"❌ DB 저장 중 오류 발생: {str(e)}")
        print(f"📊 에러 상세 정보: {repr(e)}")
        
        # 에러 타입별 상세 정보
        import traceback
        print(f"🔍 전체 에러 트레이스:")
        traceback.print_exc()
        
        db.rollback()
        
        try:
            pipeline.logger.error(f"분석 결과 저장 오류: {str(e)}")
        except:
            print(f"분석 결과 저장 오류 (로거 사용 불가): {str(e)}")
        
        # 오류를 다시 발생시켜서 상위에서 처리하도록 함
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
                            "description": "GPT-4를 사용한 3단계 심리상태 분석",
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
            return JSONResponse(content={
                "test_id": test_id,
                "status": "processing", 
                "message": "분석이 진행 중입니다...",
                "steps": [
                    {"name": "객체 탐지", "description": "그림 요소 검출 중", "completed": False, "current": True},
                    {"name": "심리 분석", "description": "심리상태 분석 대기 중", "completed": False, "current": False},
                    {"name": "성격 분류", "description": "키워드 기반 성격유형 분류 대기 중", "completed": False, "current": False}
                ],
                "current_step": 1,
                "completed_steps": 0,
                "total_steps": 3,
                "estimated_remaining": "2-3분"
            })
        
        # DB에서 직접 확률 데이터 가져오기 (기존 JSON 파일 의존성 제거)
        pipeline = get_pipeline()
        result_text = test_result.summary_text  # DB에서 직접 가져오기
        
        # 성격 유형 매핑 (persona_type ID -> 이름)
        personality_mapping = {
            1: "추진형",  # 추진이
            2: "내면형",  # 내면이  
            3: "관계형",  # 관계이
            4: "쾌락형",  # 쾌락이
            5: "안정형"   # 안정이
        }
        
        # DB에서 확률 데이터 추출
        probabilities = {
            "추진형": float(test_result.dog_scores or 0.0),
            "내면형": float(test_result.cat_scores or 0.0),
            "관계형": float(test_result.rabbit_scores or 0.0),
            "쾌락형": float(test_result.bear_scores or 0.0),
            "안정형": float(test_result.turtle_scores or 0.0)
        }
        
        # 최고 확률 유형 찾기
        if probabilities and any(v > 0 for v in probabilities.values()):
            predicted_personality = max(probabilities.items(), key=lambda x: x[1])[0]
            analysis_method = "keyword_classifier"
        else:
            # 확률 데이터가 없는 경우 persona_type에서 가져오기
            predicted_personality = personality_mapping.get(test_result.persona_type, "내면형")
            analysis_method = "fallback"
        
        # 키워드 정보 (기본값 제공)
        keyword_info = {
            "current_keywords": [],
            "previous_keywords": [],  
            "total_keywords": 0,
            "confidence": max(probabilities.values()) / 100.0 if probabilities else 0.0
        }
        
        print(f"📊 API 응답 데이터 준비:")
        print(f"  - predicted_personality: {predicted_personality}")
        print(f"  - probabilities: {probabilities}")
        print(f"  - persona_type: {test_result.persona_type}")
        print(f"  - analysis_method: {analysis_method}")

        # 분석 완료
        return JSONResponse(content={
            "test_id": test_id,
            "status": "completed",
            "message": "분석이 완료되었습니다.",
            "steps": [
                {"name": "객체 탐지", "description": "YOLO를 사용한 그림 요소 검출", "completed": True, "current": False},
                {"name": "심리 분석", "description": "GPT-4를 사용한 심리상태 분석", "completed": True, "current": False},
                {"name": "성격 분류", "description": "키워드 분류기를 사용한 성격유형 분류", "completed": True, "current": False}
            ],
            "current_step": 3,
            "completed_steps": 3,
            "total_steps": 3,
            "result": {
                "persona_type": test_result.persona_type,
                "summary_text": test_result.summary_text,
                "result_text": result_text,
                "predicted_personality": predicted_personality,
                "probabilities": probabilities,
                "analysis_method": analysis_method,
                "keyword_analysis": keyword_info,
                "created_at": test_result.created_at.isoformat() if test_result.created_at else None,
                "image_url": drawing_test.image_url  # 이미지 URL 추가
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
        # 기본 상태 정보
        status = {
            "pipeline_status": "unknown",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "pipeline_import": False,
                "yolo_model": False,
                "openai_api": False,
                "kobert_model": False,
                "directories": False
            },
            "directories": {},
            "error_details": None
        }
        
        # 파이프라인 import 확인
        if HTPAnalysisPipeline is not None:
            status["components"]["pipeline_import"] = True
            
            try:
                pipeline = get_pipeline()
                
                status["directories"] = {
                    "test_images": str(pipeline.config.test_img_dir),
                    "detection_results": str(pipeline.config.detection_results_dir),
                    "rag_docs": str(pipeline.config.rag_dir)
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
                
            except Exception as pipeline_error:
                status["error_details"] = f"Pipeline initialization failed: {str(pipeline_error)}"
        else:
            if PIPELINE_IMPORT_ERROR and "numpy.dtype size changed" in PIPELINE_IMPORT_ERROR:
                status["error_details"] = {
                    "message": "numpy/pandas 버전 호환성 문제",
                    "error": PIPELINE_IMPORT_ERROR,
                    "solution": "conda install -c conda-forge numpy pandas --force-reinstall",
                    "alternative": "pip uninstall numpy pandas -y && pip install numpy pandas",
                    "help": "numpy와 pandas의 버전이 호환되지 않습니다. 재설치가 필요합니다."
                }
            else:
                missing_packages = ["pandas", "transformers", "ultralytics", "torch", "opencv-python", "scikit-learn"]
                status["error_details"] = {
                    "message": "HTPAnalysisPipeline could not be imported",
                    "error": PIPELINE_IMPORT_ERROR or "Unknown import error",
                    "missing_packages": missing_packages,
                    "install_command": f"pip install {' '.join(missing_packages)}",
                    "help": "HTP 분석 기능을 사용하려면 위 패키지들을 설치해주세요."
                }
        
        # 전체 상태 판단
        if status["components"]["pipeline_import"]:
            all_healthy = all(status["components"].values())
            status["pipeline_status"] = "healthy" if all_healthy else "degraded"
        else:
            status["pipeline_status"] = "unavailable"
        
        return JSONResponse(content=status)
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "pipeline_status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "error_details": "Health check failed completely"
            }
        )