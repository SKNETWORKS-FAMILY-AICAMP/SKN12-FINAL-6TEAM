import base64
import os
import openai
from dotenv import load_dotenv
import sys
import json
import numpy as np
from openai import OpenAI
import re
from PIL import Image, ImageOps
import io
from datetime import datetime
import pytz

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), '../opensearch_modules'))

from opensearch_client import OpenSearchEmbeddingClient

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENSEARCH_HOST = os.getenv("OPENSEARCH_HOST")
IMAGE_DIR = os.path.join(os.path.dirname(__file__), '../detection_results/images')
RESULT_DIR = os.path.join(os.path.dirname(__file__), '../detection_results/results')
OPENSEARCH_HOST = os.getenv("OPENSEARCH_HOST")

# OpenSearch RAG 시스템 초기화
try:
    # 작업 디렉토리를 opensearch_modules로 변경하여 임베딩 파일 접근
    original_cwd = os.getcwd()
    opensearch_modules_dir = os.path.join(os.path.dirname(__file__), '../opensearch_modules')
    os.chdir(opensearch_modules_dir)
    
    opensearch_client = OpenSearchEmbeddingClient(host=OPENSEARCH_HOST)
    RAG_INDEX_NAME = "psychology_analysis"
    
    # 작업 디렉토리 복구
    os.chdir(original_cwd)
    print("OpenSearch RAG 시스템 초기화 완료")
    
except Exception as e:
    print(f"OpenSearch 초기화 실패: {e}")
    opensearch_client = None
    # 작업 디렉토리 복구 (에러 발생 시에도)
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
        r'## 1\. 심리 분석 요소 식별(.*?)(?=## 2\.|$)',  # ## 형식
        r'1\. \*\*심리 분석 요소 식별\*\*(.*?)(?=2\.|$)',  # ** 형식  
        r'### 1\. \*\*심리 분석 요소 식별\*\*(.*?)(?=### 2\.|$)',  # ### 형식
        r'1\. 심리 분석 요소 식별(.*?)(?=2\.|$)'  # 단순 형식
    ]
    
    element_section = None
    for pattern in patterns:
        element_section = re.search(pattern, analysis_text, re.DOTALL)
        if element_section:
            break
    
    if element_section:
        element_text = element_section.group(1).strip()
        print(f"요소 섹션 추출 성공: {element_text[:100]}...")
        
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
        print("요소 섹션을 찾을 수 없습니다. 전체 텍스트에서 키워드 추출 시도...")
        # 대안: 집, 나무, 사람 관련 키워드 직접 추출
        if '집' in analysis_text:
            elements.append('집')
        if '나무' in analysis_text:
            elements.append('나무')  
        if '사람' in analysis_text:
            elements.append('사람')
    
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
        print(f"RAG 검색 실패: {e}")
    
    return None

PROMPT = '''
        당신은 HTP(House-Tree-Person) 심리검사 분석 전문가입니다. 주어진 그림을 분석해 주세요.
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

openai.api_key = OPENAI_API_KEY

def optimize_image_for_gpt(image_path: str, max_size: tuple = (1024, 1024), quality: int = 85) -> tuple:
    """
    GPT Vision API 호출을 위해 이미지를 최적화
    
    Args:
        image_path (str): 원본 이미지 경로
        max_size (tuple): 최대 크기 (width, height)
        quality (int): JPEG 압축 품질 (1-100)
        
    Returns:
        tuple: (optimized_base64_string, compression_info)
    """
    try:
        # 원본 파일 크기 확인
        original_size = os.path.getsize(image_path)
        
        # 이미지 로드
        with Image.open(image_path) as img:
            # EXIF 회전 정보 적용
            img = ImageOps.exif_transpose(img)
            
            # RGB로 변환
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 원본 크기 저장
            original_dimensions = img.size
            
            # 크기 조정 (종횡비 유지)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # 메모리 버퍼에 압축하여 저장
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=quality, optimize=True)
            
            # Base64 인코딩
            compressed_bytes = buffer.getvalue()
            compressed_base64 = base64.b64encode(compressed_bytes).decode('utf-8')
            
            # 압축 정보
            compression_info = {
                'original_file_size': original_size,
                'compressed_size': len(compressed_bytes),
                'compression_ratio': round((1 - len(compressed_bytes) / original_size) * 100, 1),
                'original_dimensions': original_dimensions,
                'compressed_dimensions': img.size,
                'base64_length': len(compressed_base64),
                'quality': quality
            }
            
            return compressed_base64, compression_info
            
    except Exception as e:
        print(f"이미지 최적화 실패: {e}")
        # 실패 시 원본 방식 사용
        with open(image_path, "rb") as img_file:
            img_bytes = img_file.read()
            return base64.b64encode(img_bytes).decode("utf-8"), {
                'original_file_size': len(img_bytes),
                'compressed_size': len(img_bytes),
                'compression_ratio': 0,
                'error': str(e)
            }

def analyze_image_with_gpt(image_path, prompt, rag_context=None, max_retries=5):
    """
    GPT Vision API를 사용하여 이미지를 분석하는 함수 (거부 방지 로직 포함)
    
    Args:
        image_path (str): 분석할 이미지 파일 경로
        prompt (str): GPT에게 전달할 프롬프트
        rag_context (dict): RAG 검색 결과 (선택사항)
        max_retries (int): 최대 재시도 횟수
        
    Returns:
        str: GPT 분석 결과 텍스트
    """
    # 거부 응답 패턴 정의
    rejection_patterns = [
        "I'm unable to",
        "I can't provide an analysis",
        "I'm sorry",
        "죄송합니다",
        "죄송하지만",
        "분석할 수 없습니다",
        "분석하기 어렵습니다",
        "정확하게 분석하기 어렵습니다",
        "인식을 하기 굉장히 어렵습니다",
        "이미지를 분석하기 어렵습니다",
        "추가 정보나 설명을 제공해 주시면",
        "하지만 일반적인",
        "예를 들어 설명할 수 있습니다",
        "이미지를 인식할 수 없습니다"
    ]
    
    for attempt in range(max_retries):
        try:
            # 재시도 시 프롬프트 강화
            if attempt > 0:
                enhanced_prompt = f"""
{prompt}

[중요] 이전 시도에서 이미지 분석이 거부되었습니다. 
이번에는 반드시 이미지의 시각적 요소들을 관찰하여 HTP 심리검사 분석을 수행해주세요.
이미지가 흐리거나 불분명하더라도 보이는 요소들(선, 모양, 크기, 위치 등)을 바탕으로 분석해주세요.
완전한 거부보다는 관찰 가능한 요소라도 분석해주시기 바랍니다.
"""
            else:
                enhanced_prompt = prompt

            # 🚀 이미지 최적화: 이미 YOLO에서 320x320으로 압축된 이미지인지 확인
            try:
                import os
                from PIL import Image
                
                # 파일 크기와 이미지 크기 확인
                file_size = os.path.getsize(image_path)
                with Image.open(image_path) as img:
                    img_size = img.size
                
                # 이미 작은 이미지(YOLO 처리된)이면 추가 압축 없이 사용
                if img_size[0] <= 320 and img_size[1] <= 320 and file_size < 50000:  # 50KB 미만
                    print(f"📸 이미 최적화된 이미지 감지: {img_size}, {file_size:,} bytes - 추가 압축 생략")
                    with open(image_path, 'rb') as f:
                        img_base64 = base64.b64encode(f.read()).decode('utf-8')
                    compression_info = {
                        'original_file_size': file_size,
                        'compressed_size': file_size,
                        'compression_ratio': 0,
                        'original_dimensions': img_size,
                        'compressed_dimensions': img_size
                    }
                else:
                    print(f"📸 큰 이미지 감지: {img_size}, {file_size:,} bytes - GPT용 압축 적용")
                    img_base64, compression_info = optimize_image_for_gpt(image_path, max_size=(1024, 1024), quality=85)
                    
            except Exception as e:
                print(f"⚠️ 이미지 크기 확인 실패, 기본 압축 적용: {e}")
                img_base64, compression_info = optimize_image_for_gpt(image_path, max_size=(1024, 1024), quality=85)
            
            # 압축 결과 로그
            print(f"이미지 파일 크기: {compression_info['original_file_size']:,} bytes")
            if 'error' not in compression_info:
                print(f"처리 후 크기: {compression_info['compressed_size']:,} bytes")
                print(f"압축률: {compression_info['compression_ratio']}%")
                print(f"원본 크기: {compression_info['original_dimensions']}")
                print(f"처리 후 크기: {compression_info['compressed_dimensions']}")
            
            data_url = f"data:image/jpeg;base64,{img_base64}"
            print(f"MIME 타입: image/jpeg")
            print(f"Base64 길이: {len(img_base64)}")
            
            # 메시지 컨텐츠 구성
            content = [
                {"type": "text", "text": enhanced_prompt},
                {"type": "image_url", "image_url": {"url": data_url}}
            ]
            
            # RAG 컨텍스트 추가
            if rag_context:
                rag_text = f"\n\n[참고 자료]\n문서: {rag_context['document']} - {rag_context['element']}\n내용: {rag_context['text']}"
                content.append({"type": "text", "text": rag_text})

            import time
            gpt_start_time = time.time()
            gpt_start_datetime = datetime.now(pytz.timezone('Asia/Seoul'))
            print(f"🤖 [TIMING] GPT API 호출 시작: {gpt_start_datetime.strftime('%H:%M:%S.%f')[:-3]} (시도 {attempt + 1}/{max_retries})")
            
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "당신은 HTP(House-Tree-Person) 심리검사 전문 분석가입니다. 제공된 그림은 심리검사 목적으로 그려진 그림이며, 실제 인물의 신원 식별이 아닌 심리적 특성 분석을 위한 것입니다. 그림의 시각적 요소들을 통해 심리 상태를 분석해 주세요. 개인의 정체성이나 신원을 파악하려는 것이 아니라, 그림 표현 방식을 통한 심리 분석임을 명심하세요. 이미지가 제대로 보이지 않으면 '이미지를 인식할 수 없습니다'라고 응답하지 말고, 다시 시도해보거나 이미지 파일 문제일 수 있다고 안내해주세요."},
                    {
                        "role": "user",
                        "content": content
                    }
                ],
                max_tokens=2000,
            )
            
            gpt_end_time = time.time()
            gpt_duration = gpt_end_time - gpt_start_time
            gpt_end_datetime = datetime.now(pytz.timezone('Asia/Seoul'))
            print(f"✅ [TIMING] GPT API 호출 완료: {gpt_end_datetime.strftime('%H:%M:%S.%f')[:-3]}")
            print(f"⏱️  [TIMING] GPT API 소요시간: {gpt_duration:.2f}초")
            
            result_text = response.choices[0].message.content.strip()
            
            # 거부 응답 패턴 확인
            is_rejection = False
            for pattern in rejection_patterns:
                if pattern.lower() in result_text.lower():
                    is_rejection = True
                    print(f"거부 응답 패턴 감지: '{pattern}' (시도 {attempt + 1}/{max_retries})")
                    break
            
            # 거부 응답이 아니거나 마지막 시도라면 결과 반환
            if not is_rejection or attempt == max_retries - 1:
                if is_rejection and attempt == max_retries - 1:
                    print(f"경고: 모든 재시도가 실패했습니다. 마지막 응답을 반환합니다.")
                return result_text
            
            # 재시도 전 잠시 대기
            print(f"거부 응답으로 인한 재시도 대기 중... (2초)")
            time.sleep(2)
            
        except Exception as e:
            print(f"GPT API 호출 실패 (시도 {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                raise
            # 재시도 전 잠시 대기
            import time
            time.sleep(2)
    
    return "분석을 완료할 수 없습니다."


def analyze_image_gpt(image_base):
    """GPT와 OpenSearch RAG를 사용하여 이미지 분석을 수행하는 함수
    
    Args:
        image_base (str): 분석할 이미지의 기본 파일명 (예: test4)
        
    Returns:
        dict: 분석 결과를 포함한 딕셔너리
    """
    if not OPENAI_API_KEY:
        print("OPENAI_API_KEY가 설정되어 있지 않습니다. .env 파일을 확인하세요.")
        print(f"현재 OPENAI_API_KEY 값: {OPENAI_API_KEY[:10] if OPENAI_API_KEY else 'None'}...")
        return None

    print(f"IMAGE_DIR 경로: {IMAGE_DIR}")
    if not os.path.exists(IMAGE_DIR):
        print(f"폴더를 찾을 수 없습니다: {IMAGE_DIR}")
        print(f"현재 작업 디렉토리: {os.getcwd()}")
        return None

    target_filename = f"detection_result_{image_base}.jpg"
    image_path = os.path.join(IMAGE_DIR, target_filename)
    print(f"찾는 이미지 파일: {image_path}")
    if not os.path.exists(image_path):
        print(f"{IMAGE_DIR} 폴더에 {target_filename} 파일이 없습니다.")
        # 폴더 내 파일 목록 출력
        try:
            files = os.listdir(IMAGE_DIR)
            print(f"폴더 내 파일 목록: {files}")
        except Exception as e:
            print(f"폴더 목록 조회 실패: {e}")
        return None

    print(f"\n===== {target_filename} 심리 분석 결과 =====")
    
    # 분석 시작 시간 기록
    import time
    analysis_start_time = time.time()
    analysis_start_datetime = datetime.now(pytz.timezone('Asia/Seoul'))
    print(f"🚀 [TIMING] 심리 분석 전체 시작: {analysis_start_datetime.strftime('%H:%M:%S.%f')[:-3]}")
    
    try:
        # 1차 GPT 해석 (초기 분석)
        print("1단계: 초기 심리 분석 수행 중...")
        initial_analysis = analyze_image_with_gpt(image_path, PROMPT)
        print("\n[초기 분석 결과]")
        print(initial_analysis)
        
        # 심리 분석 요소 추출
        print("\n2단계: 심리 분석 요소 추출 중...")
        psychological_elements = extract_psychological_elements(initial_analysis)
        print(f"추출된 요소들: {psychological_elements}")
        
        # OpenSearch RAG 검색
        print("\n3단계: RAG 시스템을 통한 관련 자료 검색 중...")
        rag_result = search_rag_documents(psychological_elements)
        
        if rag_result:
            print(f"검색된 관련 자료: {rag_result['document']} - {rag_result['element']}")
            print(f"관련도 점수: {rag_result['score']:.4f}")
            
            # RAG 컨텍스트를 포함한 최종 분석
            print("\n4단계: RAG 컨텍스트를 활용한 최종 분석 수행 중...")
            final_prompt = f"""
                            아래는 심리 그림 검사의 초기 분석 결과입니다:

                            {initial_analysis}

                            위 분석 결과를 바탕으로, 제공된 참고 자료를 활용하여 더욱 정확하고 전문적인 최종 심리 분석을 제공해 주세요.
                            특히 참고 자료의 전문적 해석을 반영하여 분석의 깊이를 더해주세요.
                            반드시 ~입니다 체로 작성해 주세요.
                            """
            result_text_gpt = analyze_image_with_gpt(image_path, final_prompt, rag_result)
        else:
            print("관련 RAG 자료를 찾을 수 없어 초기 분석 결과를 사용합니다.")
            result_text_gpt = initial_analysis
        
        print("\n[최종 분석 결과]")
        print(result_text_gpt)
        
    except Exception as e:
        # 오류 시간 기록
        error_time = time.time()
        error_duration = error_time - analysis_start_time if 'analysis_start_time' in locals() else 0
        error_datetime = datetime.now(pytz.timezone('Asia/Seoul'))
        print(f"❌ [TIMING] 심리 분석 오류 발생: {error_datetime.strftime('%H:%M:%S.%f')[:-3]}")
        if error_duration > 0:
            print(f"⏱️  [TIMING] 오류까지 소요시간: {error_duration:.2f}초 ({error_duration/60:.1f}분)")
        
        print(f"분석 실패 - 상세 오류: {str(e)}")
        print(f"오류 타입: {type(e)}")
        import traceback
        print("전체 오류 추적:")
        traceback.print_exc()
        return None

    # 요약 해석문 생성
    print("\n5단계: 요약 해석문 생성 중...")
    SUMMARY_PROMPT = f"""
        아래의 그림 심리 분석 결과를 참고하여,
        사용자가 이해하기 쉽도록 전체적인 심리 상태와 특징을 자연스럽게 요약·정리해주는 해석문을 작성해 주세요.
        반드시 ~입니다 체로 작성해 주세요.

        분석 결과:
        {result_text_gpt}
        """
    try:
        result_text = analyze_image_with_gpt(image_path, SUMMARY_PROMPT)
    except Exception as e:
        print(f"요약 해석문 생성 실패: {e}")
        result_text = "(요약 해석문 생성 실패)"

    # 감정 키워드 추출 (기존 방식 유지)
    enriched = []
    if rag_result:
        enriched.append({
            'element': rag_result['element'],
            'condition': rag_result['text'][:100] + '...' if len(rag_result['text']) > 100 else rag_result['text'],
            'keywords': rag_result['metadata'].get('keywords', [])
        })

    # 결과 딕셔너리 생성 (파일 저장 없이)
    result = {
        "raw_text": result_text_gpt,
        "result_text": result_text,
        "items": enriched,
        "rag_context": rag_result
    }
    
    # 분석 완료 시간 기록
    analysis_end_time = time.time()
    analysis_duration = analysis_end_time - analysis_start_time
    analysis_end_datetime = datetime.now(pytz.timezone('Asia/Seoul'))
    print(f"✅ [TIMING] 심리 분석 전체 완료: {analysis_end_datetime.strftime('%H:%M:%S.%f')[:-3]}")
    print(f"⏱️  [TIMING] 심리 분석 총 소요시간: {analysis_duration:.2f}초 ({analysis_duration/60:.1f}분)")
    
    return result

def main():
    """메인 함수 - 커맨드 라인 인자 처리"""
    import argparse
    
    parser = argparse.ArgumentParser(description="분석할 detection_result_*.jpg 파일명을 지정하세요.")
    parser.add_argument('--image', type=str, required=True, help='분석할 detection_result_*.jpg 파일명 (예: detection_result_test4.jpg)')
    args = parser.parse_args()

    # 사용자가 입력한 파일명에서 확장자 제거 (test4.jpg → test4, test4 → test4)
    image_base = os.path.splitext(args.image)[0]
    
    # 새로운 모듈화된 함수 호출
    result = analyze_image_gpt(image_base)
    
    if result is None:
        print("분석에 실패했습니다.")
        return
    
    print("분석이 완료되었습니다.")

if __name__ == "__main__":
    main()
