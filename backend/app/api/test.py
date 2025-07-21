"""
그림 테스트 API 라우터
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.schemas.test import (
    DrawingTestCreate, DrawingTestUpdate, DrawingTestResponse,
    DrawingTestResultCreate, DrawingTestResultUpdate, DrawingTestResultResponse
)
from app.models.test import DrawingTest, DrawingTestResult
from app.database import get_db

router = APIRouter()

# 그림 테스트 관련 엔드포인트
@router.post("/drawing-tests", response_model=DrawingTestResponse, status_code=status.HTTP_201_CREATED)
async def create_drawing_test(test_data: DrawingTestCreate, db: Session = Depends(get_db)):
    """새 그림 테스트 생성"""
    new_test = DrawingTest(
        test_name=test_data.test_name,
        test_description=test_data.test_description,
        test_instructions=test_data.test_instructions,
        is_active=True
    )
    
    db.add(new_test)
    db.commit()
    db.refresh(new_test)
    
    return DrawingTestResponse(
        test_id=new_test.test_id,
        test_name=new_test.test_name,
        test_description=new_test.test_description,
        test_instructions=new_test.test_instructions,
        is_active=new_test.is_active,
        created_at=new_test.created_at
    )

@router.get("/drawing-tests", response_model=List[DrawingTestResponse])
async def get_drawing_tests(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """그림 테스트 목록 조회"""
    tests = db.query(DrawingTest).filter(
        DrawingTest.is_active == True
    ).offset(skip).limit(limit).all()
    
    return [
        DrawingTestResponse(
            test_id=test.test_id,
            test_name=test.test_name,
            test_description=test.test_description,
            test_instructions=test.test_instructions,
            is_active=test.is_active,
            created_at=test.created_at
        )
        for test in tests
    ]

@router.get("/drawing-tests/{test_id}", response_model=DrawingTestResponse)
async def get_drawing_test(test_id: int, db: Session = Depends(get_db)):
    """특정 그림 테스트 조회"""
    test = db.query(DrawingTest).filter(
        DrawingTest.test_id == test_id
    ).first()
    
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="그림 테스트를 찾을 수 없습니다."
        )
    
    return DrawingTestResponse(
        test_id=test.test_id,
        test_name=test.test_name,
        test_description=test.test_description,
        test_instructions=test.test_instructions,
        is_active=test.is_active,
        created_at=test.created_at
    )

@router.put("/drawing-tests/{test_id}", response_model=DrawingTestResponse)
async def update_drawing_test(test_id: int, test_data: DrawingTestUpdate, db: Session = Depends(get_db)):
    """그림 테스트 수정"""
    test = db.query(DrawingTest).filter(
        DrawingTest.test_id == test_id
    ).first()
    
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="그림 테스트를 찾을 수 없습니다."
        )
    
    if test_data.test_name is not None:
        test.test_name = test_data.test_name
    if test_data.test_description is not None:
        test.test_description = test_data.test_description
    if test_data.test_instructions is not None:
        test.test_instructions = test_data.test_instructions
    if test_data.is_active is not None:
        test.is_active = test_data.is_active
    
    db.commit()
    db.refresh(test)
    
    return DrawingTestResponse(
        test_id=test.test_id,
        test_name=test.test_name,
        test_description=test.test_description,
        test_instructions=test.test_instructions,
        is_active=test.is_active,
        created_at=test.created_at
    )

# 테스트 결과 관련 엔드포인트
@router.post("/drawing-test-results", response_model=DrawingTestResultResponse, status_code=status.HTTP_201_CREATED)
async def create_test_result(result_data: DrawingTestResultCreate, db: Session = Depends(get_db)):
    """테스트 결과 생성"""
    new_result = DrawingTestResult(
        user_id=result_data.user_id,
        test_id=result_data.test_id,
        drawing_data=result_data.drawing_data,
        analysis_result=result_data.analysis_result
    )
    
    db.add(new_result)
    db.commit()
    db.refresh(new_result)
    
    return DrawingTestResultResponse(
        result_id=new_result.result_id,
        user_id=new_result.user_id,
        test_id=new_result.test_id,
        drawing_data=new_result.drawing_data,
        analysis_result=new_result.analysis_result,
        completed_at=new_result.completed_at
    )

@router.get("/drawing-test-results/user/{user_id}", response_model=List[DrawingTestResultResponse])
async def get_user_test_results(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """특정 사용자의 테스트 결과 조회"""
    results = db.query(DrawingTestResult).filter(
        DrawingTestResult.user_id == user_id
    ).offset(skip).limit(limit).all()
    
    return [
        DrawingTestResultResponse(
            result_id=result.result_id,
            user_id=result.user_id,
            test_id=result.test_id,
            drawing_data=result.drawing_data,
            analysis_result=result.analysis_result,
            completed_at=result.completed_at
        )
        for result in results
    ]

@router.get("/drawing-test-results/{result_id}", response_model=DrawingTestResultResponse)
async def get_test_result(result_id: int, db: Session = Depends(get_db)):
    """특정 테스트 결과 조회"""
    result = db.query(DrawingTestResult).filter(
        DrawingTestResult.result_id == result_id
    ).first()
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="테스트 결과를 찾을 수 없습니다."
        )
    
    return DrawingTestResultResponse(
        result_id=result.result_id,
        user_id=result.user_id,
        test_id=result.test_id,
        drawing_data=result.drawing_data,
        analysis_result=result.analysis_result,
        completed_at=result.completed_at
    )

