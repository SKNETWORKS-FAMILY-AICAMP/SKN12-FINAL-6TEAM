import base64
import os
import openai
from dotenv import load_dotenv
import sys
import json
import numpy as np
from openai import OpenAI
import re
import time
from typing import Optional, Dict, Any, Tuple
import logging

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), '../opensearch_modules'))

from opensearch_client import OpenSearchEmbeddingClient

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

IMAGE_DIR = os.path.join(os.path.dirname(__file__), '../detection_results/images')
RESULT_DIR = os.path.join(os.path.dirname(__file__), '../detection_results/results')

# 재시도 설정
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 2  # 초
MAX_RETRY_DELAY = 30  # 초
RETRY_BACKOFF_FACTOR = 2

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=OPENAI_API_KEY)

# OpenSearch RAG 시스템 초기화
try:
    original_cwd = os.getcwd()
    opensearch_modules_dir = os.path.join(os.path.dirname(__file__), '../opensearch_modules')
    os.chdir(opensearch_modules_dir)
    
    opensearch_client = OpenSearchEmbeddingClient()
    RAG_INDEX_NAME = "psychology_analysis"
    
    os.chdir(original_cwd)
    logger.info("OpenSearch RAG 시스템 초기화 완료")
except Exception as e:
    logger.error(f"OpenSearch 초기화 실패: {e}")
    opensearch_client = None
    try:
        os.chdir(original_cwd)
    except:
        pass

def extract_psychological_elements(analysis_text):
    """
    GPT 분석 결과에서 심리 분석 요소들을 추출
    """
    elements = []
    
    # 다양한 형식의 1단계 섹션 패턴 시도
    patterns = [
        r'## 1\. 심리 분석 요소 식별(.*?)(?=## 2\.|$)',
        r'1\. \*\*심리 분석 요소 식별\*\*(.*?)(?=2\.|$)',
        r'### 1\. \*\*심리 분석 요소 식별\*\*(.*?)(?=### 2\.|$)',
        r'1\. 심리 분석 요소 식별(.*?)(?=2\.|$)',
        r'1단계[:\s]+관찰된 특징들(.*?)(?=2단계|$)'
    ]
    
    element_section = None
    for pattern in patterns:
        element_section = re.search(pattern, analysis_text, re.DOTALL | re.IGNORECASE)
        if element_section:
            break
    
    if element_section:
        element_text = element_section.group(1).strip()
        logger.debug(f"요소 섹션 추출 성공: {element_text[:100]}...")
        
        # 각 요소를 개별적으로 추출
        lines = element_text.split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and len(line) > 5:
                # 불필요한 문자 제거 후 요소 추가
                clean_element = re.sub(r'^[-•*]\s*', '', line)
                if clean_element:
                    elements.append(clean_element)
    else:
        logger.warning("요소 섹션을 찾을 수 없습니다. 전체 텍스트에서 키워드 추출 시도...")
        # 대안: 집, 나무, 사람 관련 키워드 직접 추출
        keywords = ['집', '나무', '사람', '지붕', '창문', '문', '굴뚝', '줄기', '가지', '잎', '뿌리', '얼굴', '팔', '다리']
        for keyword in keywords:
            if keyword in analysis_text:
                elements.append(keyword)
    
    return elements

def search_rag_documents(query_elements):
    """
    OpenSearch를 사용하여 관련 RAG 문서 검색
    """
    if not opensearch_client or not query_elements:
        return []
    
    try:
        # 모든 요소를 하나의 쿼리로 합침
        combined_query = ' '.join(query_elements)
        
        # 하이브리드 검색 수행
        search_results = opensearch_client.hybrid_search(
            index_name=RAG_INDEX_NAME,
            query_text=combined_query,
            k=10,
            use_reranker=True
        )
        
        # Reranker 기준 1번째 결과 반환
        if search_results:
            top_result = search_results[0]
            return {
                'text': top_result['text'],
                'metadata': top_result.get('metadata', {}),
                'document': top_result.get('document', ''),
                'element': top_result.get('element', ''),
                'score': top_result.get('rerank_score', top_result.get('score', 0))
            }  
    except Exception as e:
        logger.error(f"RAG 검색 실패: {e}")
    
    return None

PROMPT = '''
        당신은 HTP(House-Tree-Person) 심리검사 분석 전문가입니다. 주어진 그림을 분석해 주세요.
        
        **중요**: 이미지가 보이지 않는다고 말하지 마세요. 제공된 이미지는 HTP 검사 그림이며, 반드시 분석이 가능합니다.
        
        분석 방법
        1단계: 관찰된 특징들
        그림에서 보이는 구체적인 특징들을 나열해 주세요:

        집: 크기, 창문, 문, 지붕, 굴뚝 등의 특징
        나무: 크기, 줄기, 가지, 잎, 뿌리 등의 특징
        사람: 크기, 자세, 얼굴, 옷차림 등의 특징
        전체: 배치, 선의 굵기, 그림 스타일 등

        2단계: 심리적 해석
        각 요소가 나타내는 심리적 의미를 설명해 주세요:

        집 → 가족관계, 안정감, 소속감
        나무 → 성장욕구, 생명력, 적응력
        사람 → 자아상, 대인관계, 정서상태

        3단계: 핵심 감정 키워드
        분석 결과를 바탕으로 주요 감정 키워드를 3-5개 제시해 주세요.
        형식: 키워드만 한 줄씩 나열 (예: 불안, 안정감, 소외감)
        
        **작성 규칙**

        - 모든 답변은 한글로 '~입니다' 체로 작성
        - 단정적 표현보다는 '~로 보입니다', '~한 경향을 나타냅니다' 등 완화된 표현 사용
        - 부정적 해석과 긍정적 해석을 균형있게 제시
        - 이제 주어진 HTP 그림을 분석해 주세요.
        '''

def validate_analysis_response(response_text: str) -> Tuple[bool, str]:
    """
    GPT 응답이 유효한 분석인지 검증
    
    Returns:
        Tuple[bool, str]: (유효 여부, 에러 메시지 또는 빈 문자열)
    """
    # 이미지 인식 불가 관련 문구 체크
    error_phrases = [
        "이미지를 인식할 수 없",
        "이미지가 보이지 않",
        "이미지를 분석할 수 없",
        "이미지가 제공되지 않",
        "이미지를 확인할 수 없",
        "cannot analyze the image",
        "cannot see the image",
        "no image provided",
        "unable to process the image"
    ]
    
    response_lower = response_text.lower()
    for phrase in error_phrases:
        if phrase.lower() in response_lower:
            return False, f"이미지 인식 실패 감지: {phrase}"
    
    # 최소 분석 길이 체크
    if len(response_text.strip()) < 100:
        return False, "응답이 너무 짧습니다"
    
    # 필수 키워드 체크 (최소 하나는 포함되어야 함)
    required_keywords = ['집', '나무', '사람', 'house', 'tree', 'person']
    has_keyword = any(keyword in response_text.lower() for keyword in required_keywords)
    
    if not has_keyword:
        return False, "HTP 분석 키워드가 포함되지 않았습니다"
    
    return True, ""

def analyze_image_with_gpt_retry(image_path: str, prompt: str, rag_context: Optional[Dict] = None) -> Optional[str]:
    """
    GPT-4 Vision API를 사용하여 이미지 분석 (재시도 로직 포함)
    """
    retry_count = 0
    last_error = None
    
    while retry_count < MAX_RETRIES:
        try:
            logger.info(f"GPT 분석 시도 {retry_count + 1}/{MAX_RETRIES}")
            
            with open(image_path, "rb") as img_file:
                img_bytes = img_file.read()
                
            # 파일 확장자에 따른 MIME 타입 결정
            _, ext = os.path.splitext(image_path.lower())
            mime_types = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }
            mime_type = mime_types.get(ext, 'image/jpeg')
            
            img_base64 = base64.b64encode(img_bytes).decode("utf-8")
            data_url = f"data:{mime_type};base64,{img_base64}"
            
            # 메시지 컨텐츠 구성
            content = [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": data_url}}
            ]
            
            # RAG 컨텍스트 추가
            if rag_context:
                rag_text = f"\n\n[참고 자료]\n문서: {rag_context['document']} - {rag_context['element']}\n내용: {rag_context['text']}"
                content.append({"type": "text", "text": rag_text})
            
            # 시스템 메시지 개선
            system_message = """당신은 HTP(House-Tree-Person) 심리검사 전문 분석가입니다. 
            제공된 그림은 심리검사 목적으로 그려진 그림이며, 반드시 분석이 가능합니다.
            이미지가 흐릿하거나 불완전하더라도, 보이는 요소들을 바탕으로 분석을 진행해주세요.
            절대로 '이미지를 인식할 수 없다'거나 '분석할 수 없다'고 응답하지 마세요.
            최선을 다해 관찰 가능한 요소들을 찾아 분석해주세요."""
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": content}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            result = response.choices[0].message.content.strip()
            
            # 응답 검증
            is_valid, error_msg = validate_analysis_response(result)
            
            if is_valid:
                logger.info("유효한 분석 응답을 받았습니다")
                return result
            else:
                logger.warning(f"유효하지 않은 응답: {error_msg}")
                last_error = error_msg
                retry_count += 1
                
                if retry_count < MAX_RETRIES:
                    # 재시도 전 대기 (지수 백오프)
                    delay = min(INITIAL_RETRY_DELAY * (RETRY_BACKOFF_FACTOR ** (retry_count - 1)), MAX_RETRY_DELAY)
                    logger.info(f"{delay}초 후 재시도합니다...")
                    time.sleep(delay)
                    
                    # 프롬프트 수정하여 재시도
                    prompt = f"""이전 시도에서 이미지 인식에 실패했습니다. 
                    다시 한 번 주의깊게 이미지를 관찰하고 분석해주세요.
                    이미지가 흐릿하거나 불완전하더라도, 보이는 요소들을 최대한 활용하여 분석해주세요.
                    
                    {prompt}"""
                
        except openai.RateLimitError as e:
            logger.error(f"Rate limit 에러: {e}")
            retry_count += 1
            if retry_count < MAX_RETRIES:
                delay = min(INITIAL_RETRY_DELAY * (RETRY_BACKOFF_FACTOR ** retry_count), MAX_RETRY_DELAY)
                logger.info(f"Rate limit으로 인해 {delay}초 후 재시도합니다...")
                time.sleep(delay)
        
        except openai.APIError as e:
            logger.error(f"OpenAI API 에러: {e}")
            last_error = str(e)
            retry_count += 1
            if retry_count < MAX_RETRIES:
                delay = INITIAL_RETRY_DELAY * (RETRY_BACKOFF_FACTOR ** (retry_count - 1))
                logger.info(f"{delay}초 후 재시도합니다...")
                time.sleep(delay)
        
        except Exception as e:
            logger.error(f"예상치 못한 에러: {e}")
            last_error = str(e)
            retry_count += 1
            if retry_count < MAX_RETRIES:
                time.sleep(INITIAL_RETRY_DELAY)
    
    logger.error(f"모든 재시도 실패. 마지막 에러: {last_error}")
    return None

def analyze_image_with_gpt(image_path: str, prompt: str, rag_context: Optional[Dict] = None) -> str:
    """
    기존 함수와의 호환성을 위한 래퍼 함수
    """
    result = analyze_image_with_gpt_retry(image_path, prompt, rag_context)
    if result is None:
        # 재시도 모두 실패 시 기본 응답 반환
        logger.warning("모든 재시도가 실패했습니다. 기본 응답을 반환합니다.")
        return """그림 분석을 수행할 수 없었습니다. 
        다음 사항을 확인해 주세요:
        1. 이미지 파일이 정상적으로 업로드되었는지 확인
        2. 이미지가 너무 크거나 손상되지 않았는지 확인
        3. 잠시 후 다시 시도해 주세요."""
    return result

def analyze_image_gpt(image_base):
    """GPT와 OpenSearch RAG를 사용하여 이미지 분석을 수행하는 함수
    
    프롬프트에 정의된 3단계 분석 프로세스를 따릅니다:
    1단계: 관찰된 특징들 파악
    2단계: 심리적 해석 
    3단계: 핵심 감정 키워드 도출
    
    Args:
        image_base (str): 분석할 이미지의 기본 파일명 (예: test4)
        
    Returns:
        dict: 분석 결과를 포함한 딕셔너리
    """
    if not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY가 설정되어 있지 않습니다.")
        return None

    if not os.path.exists(IMAGE_DIR):
        logger.error(f"폴더를 찾을 수 없습니다: {IMAGE_DIR}")
        return None

    target_filename = f"detection_result_{image_base}.jpg"
    image_path = os.path.join(IMAGE_DIR, target_filename)
    
    if not os.path.exists(image_path):
        logger.error(f"{IMAGE_DIR} 폴더에 {target_filename} 파일이 없습니다.")
        try:
            files = os.listdir(IMAGE_DIR)
            logger.info(f"폴더 내 파일 목록: {files}")
        except Exception as e:
            logger.error(f"폴더 목록 조회 실패: {e}")
        return None

    logger.info(f"\n===== {target_filename} 심리 분석 시작 =====")
    
    try:
        # 단계 1: GPT 3단계 분석 (관찰→해석→키워드)
        logger.info("단계 1/3: GPT를 통한 3단계 심리 분석 수행 중...")
        initial_analysis = analyze_image_with_gpt(image_path, PROMPT)
        
        if "그림 분석을 수행할 수 없었습니다" in initial_analysis:
            logger.error("초기 분석 실패")
            return {
                "raw_text": initial_analysis,
                "result_text": initial_analysis,
                "items": [],
                "rag_context": None,
                "error": True
            }
        
        logger.info("GPT 3단계 분석 완료")
        
        # 단계 2: RAG 강화 (선택적)
        logger.info("단계 2/3: RAG 시스템을 통한 전문 자료 검색 중...")
        psychological_elements = extract_psychological_elements(initial_analysis)
        logger.info(f"추출된 요소들: {psychological_elements}")
        
        rag_result = search_rag_documents(psychological_elements)
        
        if rag_result:
            logger.info(f"검색된 관련 자료: {rag_result['document']} - {rag_result['element']}")
            logger.info(f"관련도 점수: {rag_result['score']:.4f}")
            
            # RAG 컨텍스트를 포함한 보강 분석
            enriched_prompt = f"""
                            아래는 HTP 심리 그림 검사의 3단계 분석 결과입니다:

                            {initial_analysis}

                            위 분석 결과와 함께 제공된 전문 참고 자료를 활용하여, 
                            더욱 깊이 있고 전문적인 심리 분석을 제공해 주세요.
                            
                            중요: 기존 3단계 구조(관찰→해석→키워드)를 유지하되,
                            참고 자료의 전문적 해석을 반영하여 내용을 보강해 주세요.
                            반드시 ~입니다 체로 작성해 주세요.
                            """
            result_text_gpt = analyze_image_with_gpt(image_path, enriched_prompt, rag_result)
        else:
            logger.info("관련 RAG 자료를 찾을 수 없어 초기 분석 결과를 사용합니다.")
            result_text_gpt = initial_analysis
        
        # 단계 3: 사용자 친화적 요약
        logger.info("단계 3/3: 사용자 친화적 요약문 생성 중...")
        SUMMARY_PROMPT = f"""
        아래의 HTP 심리 분석 결과를 바탕으로,
        일반 사용자가 이해하기 쉽도록 핵심 내용을 자연스럽게 요약해 주세요.
        
        요약 시 주의사항:
        - 전문 용어는 쉬운 표현으로 바꾸기
        - 긍정적인 면과 개선점을 균형있게 포함
        - 2-3문단으로 간결하게 정리
        - 반드시 ~입니다 체로 작성

        분석 결과:
        {result_text_gpt}
        """
        
        try:
            result_text = analyze_image_with_gpt(image_path, SUMMARY_PROMPT)
        except Exception as e:
            logger.error(f"요약 해석문 생성 실패: {e}")
            result_text = result_text_gpt  # 요약 실패 시 전체 분석 결과 사용
        
        logger.info("전체 분석 프로세스 완료")
        
    except Exception as e:
        logger.error(f"분석 실패: {str(e)}", exc_info=True)
        return None

    # 감정 키워드 추출
    enriched = []
    if rag_result:
        enriched.append({
            'element': rag_result['element'],
            'condition': rag_result['text'][:100] + '...' if len(rag_result['text']) > 100 else rag_result['text'],
            'keywords': rag_result['metadata'].get('keywords', [])
        })

    # 결과 딕셔너리 생성
    result = {
        "raw_text": result_text_gpt,
        "result_text": result_text,
        "items": enriched,
        "rag_context": rag_result,
        "error": False
    }
    
    return result

def main():
    """메인 함수 - 커맨드 라인 인자 처리"""
    import argparse
    
    parser = argparse.ArgumentParser(description="분석할 detection_result_*.jpg 파일명을 지정하세요.")
    parser.add_argument('--image', type=str, required=True, help='분석할 detection_result_*.jpg 파일명 (예: detection_result_test4.jpg)')
    args = parser.parse_args()

    # 사용자가 입력한 파일명에서 확장자 제거
    image_base = os.path.splitext(args.image)[0]
    if image_base.startswith('detection_result_'):
        image_base = image_base.replace('detection_result_', '')
    
    # 분석 수행
    result = analyze_image_gpt(image_base)
    
    if result is None:
        logger.error("분석에 실패했습니다.")
        return
    
    if result.get('error', False):
        logger.error("분석 중 오류가 발생했습니다.")
        print(result.get('result_text', ''))
    else:
        logger.info("분석이 완료되었습니다.")
        print("\n[분석 결과]")
        print(result.get('result_text', ''))

if __name__ == "__main__":
    main()