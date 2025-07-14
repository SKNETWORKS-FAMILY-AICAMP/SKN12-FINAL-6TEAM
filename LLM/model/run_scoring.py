from pathlib import Path
import re
import argparse
import os
import sys
sys.path.append(os.path.dirname(__file__))
from analyze_images_with_gpt import analyze_image_with_gpt, PROMPT, IMAGE_DIR
import numpy as np
from collections import defaultdict
import openai

from difflib import SequenceMatcher
import json

def is_similar(a, b, threshold=0.8):
    return SequenceMatcher(None, a, b).ratio() > threshold

# 경로 상수 정의
DOCS_DIR = os.path.join(os.path.dirname(__file__), '../docs')
TEST_IMG_DIR = os.path.join(os.path.dirname(__file__), '../test_images')
MODEL_DIR = os.path.dirname(__file__)
IMAGE_DIR = os.path.join(os.path.dirname(__file__), '../detection_results/images')

def load_rag_docs():
    base_path = Path("./")
    files = {
        "house": base_path / "rag_doc_house.md",
        "tree": base_path / "rag_doc_tree.md",
        "person": base_path / "rag_doc_person.md"
    }
    rag_data = {}
    for k, path in files.items():
        rag_data[k] = path.read_text(encoding="utf-8")
    return rag_data

def parse_rag_markdown(md_text):
    pattern = r"- 요소:\s*(.*?)\n- 조건:\s*(.*?)\n- 감정 키워드:\s*(.*?)\n"
    return {(m[0], m[1]): m[2] for m in re.findall(pattern, md_text)}

def load_emotion_keywords():
    data = Path(os.path.join(DOCS_DIR, "emotion_keywords.md")).read_text(encoding="utf-8")
    category_map = {}
    current_category = None
    for line in data.splitlines():
        if line.startswith("### "):
            current_category = line.replace("### ", "").strip()
        elif line.strip() and current_category:
            keywords = [k.strip() for k in line.split(",") if k.strip()]
            for k in keywords:
                category_map[k] = current_category
    return category_map

def score_persona(elements, rag_maps, keyword_map):
    scores = {"추진형": 0, "관계형": 0, "안정형": 0, "쾌락형": 0, "내면형": 0}
    for elem in elements:
        key = (elem["element"], elem["condition"])
        doc = rag_maps[elem["category"]]
        keyword = doc.get(key)
        if keyword:
            mapped_type = keyword_map.get(keyword)
            if mapped_type:
                scores[mapped_type] += 1
    return scores

# 요소/조건/카테고리 추출을 위한 파서 함수 (예시)
def parse_elements_from_analysis(analysis_text):
    # "1. 심리 분석 요소 식별" ~ "2. 요소별 심층 분석" 사이의 목록만 추출
    import re
    elements = []
    # 1번 항목 추출
    m = re.search(r"1\. \*\*심리 분석 요소 식별\*\*:(.*?)2\. ", analysis_text, re.DOTALL)
    if not m:
        return elements
    block = m.group(1)
    # 각 줄에서 요소/조건/카테고리 추출 (예: '- 집: 지붕에 있는 창문, 격자무늬')
    for line in block.splitlines():
        line = line.strip('-•* ').strip()
        if not line or ':' not in line:
            continue
        # 예시: '집: 지붕에 있는 창문, 격자무늬'
        category, rest = line.split(':', 1)
        element, *condition = rest.split(',', 1)
        elements.append({
            'category': category.strip(),
            'element': element.strip(),
            'condition': condition[0].strip() if condition else ''
        })
    return elements

# 감정 키워드와 유형 매핑 파싱 함수
def parse_emotion_keywords_md(md_path="emotion_keywords.md"):
    type_map = {}
    current_type = None
    with open(os.path.join(DOCS_DIR, md_path), encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("## "):
                continue
            if line.startswith("### "):
                current_type = line.replace("### ", "").replace("특징 요약", "").strip()
            elif line.startswith("- ") and current_type and not line.startswith("---"):
                kw = line[2:].strip()
                if kw:
                    type_map[kw] = current_type
    return type_map

# 감정 키워드 임베딩 생성 함수
EMBED_MODEL = "text-embedding-3-small"
def get_embedding(text):
    return openai.embeddings.create(input=text, model=EMBED_MODEL).data[0].embedding

def cosine_similarity(a, b):
    a, b = np.array(a), np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# analyze_images_with_gpt 결과에서 감정 키워드만 추출
# (1, 2, 3번 항목 전체에서 쉼표/슬래시/스페이스 등으로 분리)
def extract_result_keywords(analysis_text):
    import re
    # 1, 2, 3번 항목 전체 추출
    matches = re.findall(r"\d+\. ?\*\*.*?\*\*:?(.+?)(?=\n\d+\.|$)", analysis_text, re.DOTALL)
    keywords = []
    for block in matches:
        # 한 줄씩 분리 후, 쉼표/슬래시/스페이스 등으로 분리
        for line in block.splitlines():
            for k in re.split(r"[\s,\/]+", line.strip()):
                if k:
                    keywords.append(k)
    return list(set(keywords))  # 중복 제거

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="분석할 detection_result_*.jpg 파일명을 지정하세요.")
    parser.add_argument('--image', type=str, required=True, help='분석할 원본 이미지 파일명 (예: test4.jpg 또는 test4)')
    parser.add_argument('--embedding', action='store_true', help='임베딩 기반 감정유형 분석 실행')
    args = parser.parse_args()

    # detection_result_*.jpg 경로 생성
    image_base = os.path.splitext(args.image)[0]
    target_filename = f"detection_result_{image_base}.jpg"
    image_path = os.path.join(IMAGE_DIR, target_filename)
    if not os.path.exists(image_path):
        print(f"{IMAGE_DIR} 폴더에 {target_filename} 파일이 없습니다.")
        exit(1)

    # GPT 분석 결과 얻기
    try:
        analysis_text = analyze_image_with_gpt(image_path, PROMPT)
    except Exception as e:
        print(f"분석 실패: {e}")
        exit(1)

    if args.embedding:
        type_map = parse_emotion_keywords_md(os.path.join(DOCS_DIR, "emotion_keywords.md"))
        emotion_keywords = list(type_map.keys())
        keyword_embeddings = {kw: get_embedding(kw) for kw in emotion_keywords}
        result_keywords = extract_result_keywords(analysis_text)
        N = 5
        final_scores = defaultdict(int)
        for rk in result_keywords:
            rk_emb = get_embedding(rk)
            sims = [(kw, cosine_similarity(rk_emb, emb)) for kw, emb in keyword_embeddings.items()]
            sims.sort(key=lambda x: x[1], reverse=True)
            top_n = sims[:N]
            for kw, _ in top_n:
                t = type_map[kw]
                final_scores[t] += 1
        if final_scores:
            print("임베딩 기반 감정유형 점수:", dict(final_scores))
            print("임베딩 기반 최종 감정유형:", max(final_scores, key=final_scores.get))
        else:
            print("임베딩 기반 감정유형 점수 없음")
        exit(0)

    extracted_elements = parse_elements_from_analysis(analysis_text)
    if not extracted_elements:
        print("분석 요소를 추출하지 못했습니다.")
        exit(1)

    # 기존 점수 계산 로직
    rag_raw = load_rag_docs()
    rag_maps = {k: parse_rag_markdown(v) for k, v in rag_raw.items()}
    keyword_map = load_emotion_keywords()

    result = score_persona(extracted_elements, rag_maps, keyword_map)
    print("최종 점수:", result)
    print("예측 유형:", max(result, key=result.get))


# Inserted matching block

    for (elem, cond), emotions in parsed.items():
        matched = False
        for (rag_elem, rag_cond), rag_info in rag_data.items():
            if is_similar(elem, rag_elem) and is_similar(cond, rag_cond):
                matched = True
                print(f"🟢 매칭된 항목: 요소='{elem}', 조건='{cond}' → 감정 키워드: {rag_info['감정 키워드']}")
                keywords = [k.strip() for k in rag_info["감정 키워드"].split(",")]
                for kw in keywords:
                    if kw in emotion_to_persona:
                        scores[emotion_to_persona[kw]] += 1
                matched_results.append((elem, cond, rag_info["해석 설명"]))
                break
        if not matched:
            print(f"⚠️ 매칭 실패: 요소='{elem}', 조건='{cond}'")

