import base64
import os
import openai
from dotenv import load_dotenv
import argparse
import sys
import json
import numpy as np
from openai import OpenAI

sys.path.append(os.path.dirname(__file__))

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

DOCS_DIR = os.path.join(os.path.dirname(__file__), '../docs')
IMAGE_DIR = os.path.join(os.path.dirname(__file__), '../detection_results/images')
RESULT_DIR = os.path.join(os.path.dirname(__file__), '../detection_results/results')

# RAG 문서 불러오기
RAG_FILES = [
    os.path.join(DOCS_DIR, "rag_doc_house.md"),
    os.path.join(DOCS_DIR, "rag_doc_tree.md"),
    os.path.join(DOCS_DIR, "rag_doc_person.md"),
]
def load_rag_docs():
    docs = []
    for fname in RAG_FILES:
        with open(fname, encoding="utf-8") as f:
            docs.append(f.read())
    return "\n\n".join(docs)

RAG_GUIDE = load_rag_docs()

PROMPT = f'''
모든 답변은 반드시 한글로 작성해 주세요.
주어진 그림은 실제 장소나 인물이 아닌, 심리 검사를 위해 직접 손으로 그린 그림입니다. 
분석은 전문가처럼 자세하고 상세히 제시해야 하며, 모든 답변은 ~입니다 체로 적습니다.

아래의 세 단계로 분석을 수행해 주세요:

1. **심리 분석 요소 식별**  
   - 그림에서 보이는 시각적 특징들을 가능한 한 많이 구체적으로 식별해 주세요.  
   - 심리적 해석 없이 관찰 가능한 요소만 나열해 주세요.

2. **요소별 심층 분석**  
   - 집, 나무, 사람 순서로 분석합니다.  
   - 각 요소에 대해 그 특징이 시사하는 심리적 해석을 구체적으로 제시해 주세요.

3. **주요 감정 키워드**  
   - 아래와 같이 요소, 조건 없이 감정 키워드만 한 줄씩 나열해 주세요.  
   - 최소 3개 이상의 키워드를 반드시 포함해 주세요.  
   - 예시:
     불안, 안정, 자기표현, 갈등

아래의 해석 기준을 반드시 참고하여 분석을 수행하세요:

{RAG_GUIDE}
'''

openai.api_key = OPENAI_API_KEY

def analyze_image_with_gpt(image_path, prompt):
    with open(image_path, "rb") as img_file:
        img_bytes = img_file.read()
        img_base64 = base64.b64encode(img_bytes).decode("utf-8")
        data_url = f"data:image/jpeg;base64,{img_base64}"

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 심리 분석가입니다."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": data_url}}
                    ]
                }
            ],
            max_tokens=2000,
        )
    return response.choices[0].message.content.strip()

# RAG 문서 파싱 함수 (요소/조건/감정키워드 추출)
def parse_rag_md(md_path):
    rag_items = []
    with open(md_path, encoding="utf-8") as f:
        block = {}
        for line in f:
            line = line.strip()
            if line.startswith('- 요소:'):
                block['element'] = line.replace('- 요소:', '').strip()
            elif line.startswith('- 조건:'):
                block['condition'] = line.replace('- 조건:', '').strip()
            elif line.startswith('- 감정 키워드:'):
                block['keywords'] = [k.strip() for k in line.replace('- 감정 키워드:', '').split(',') if k.strip()]
            elif line == '' and block:
                rag_items.append(block)
                block = {}
        if block:
            rag_items.append(block)
    return rag_items

def parse_gpt_result_with_rag(raw_text, rag_md_paths):
    # rag_doc_*.md에서 요소/조건/감정키워드 모두 모으기
    rag_items = []
    for md_path in rag_md_paths:
        rag_items.extend(parse_rag_md(md_path))
    # raw_text에 등장하는 요소만 추출
    result = []
    for item in rag_items:
        if item['element'] in raw_text:
            result.append(item)
    return result

def main():
    parser = argparse.ArgumentParser(description="분석할 detection_result_*.jpg 파일명을 지정하세요.")
    parser.add_argument('--image', type=str, required=True, help='분석할 detection_result_*.jpg 파일명 (예: detection_result_test4.jpg)')
    args = parser.parse_args()

    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY가 설정되어 있지 않습니다. .env 파일을 확인하세요.")
        return

    if not os.path.exists(IMAGE_DIR):
        print(f"폴더를 찾을 수 없습니다: {IMAGE_DIR}")
        return

    # 사용자가 입력한 파일명에서 확장자 제거 (test4.jpg → test4, test4 → test4)
    image_base = os.path.splitext(args.image)[0]
    target_filename = f"detection_result_{image_base}.jpg"
    image_path = os.path.join(IMAGE_DIR, target_filename)
    if not os.path.exists(image_path):
        print(f"{IMAGE_DIR} 폴더에 {target_filename} 파일이 없습니다.")
        return

    print(f"\n===== {target_filename} 심리 분석 결과 =====")
    try:
        # 1차 GPT 해석
        result_text_gpt = analyze_image_with_gpt(image_path, PROMPT)
        print(result_text_gpt)  # 1차 해석 텍스트 바로 출력
        # rag_doc_*.md 경로 리스트
        rag_md_paths = RAG_FILES
        # rag 기반 요소/조건/감정키워드 추출
        gpt_items = parse_gpt_result_with_rag(result_text_gpt, rag_md_paths)
    except Exception as e:
        print(f"분석 실패: {e}")
        return

    # enrich_keywords_with_rag 호출 제거, rag 기반 추출 결과를 그대로 사용
    enriched = gpt_items

    # 사용자에게 제공할 종합 해석문(result_text) 생성용 프롬프트
    SUMMARY_PROMPT = f"""
아래의 그림 심리 분석 결과(1,2,3단계)를 참고하여,
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

    # 최종 해석본 json 저장 (raw_text, result_text, items)
    result_json_path = os.path.join(RESULT_DIR, f"result_{image_base}.json")
    result = {
        "raw_text": result_text_gpt,
        "result_text": result_text,
        "items": enriched  # 반드시 포함
    }
    with open(result_json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"최종 해석본이 {result_json_path}에 저장되었습니다.")

if __name__ == "__main__":
    main() 