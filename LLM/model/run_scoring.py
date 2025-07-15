
import argparse
import json
import re
from collections import defaultdict
from difflib import SequenceMatcher
import sys
import os
sys.path.append(os.path.dirname(__file__))

DOCS_DIR = os.path.join(os.path.dirname(__file__), '../docs')
IMAGE_DIR = os.path.join(os.path.dirname(__file__), '../detection_results/images')
RESULT_DIR = os.path.join(os.path.dirname(__file__), '../detection_results/results')


def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def load_emotion_keywords(filepath=None):
    if filepath is None:
        filepath = os.path.join(DOCS_DIR, 'emotion_keywords.json')
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    keyword_to_type = {}
    for persona_type, keywords in data.items():
        for kw in keywords:
            keyword_to_type[kw] = persona_type
    return keyword_to_type

def extract_keywords_from_result_json(result_json_path):
    with open(result_json_path, encoding='utf-8') as f:
        result = json.load(f)
    keywords = []
    for item in result.get('items', []):
        keywords.extend(item.get('keywords', []))
    return keywords

def score_by_result_keywords(keywords, keyword_to_type):
    score = defaultdict(int)
    detail = defaultdict(list)  # 유형별로 기여한 키워드 리스트
    for kw in keywords:
        for known_kw, persona in keyword_to_type.items():
            if kw in known_kw or known_kw in kw:
                score[persona] += 1
                detail[persona].append(kw)
                break
            elif similarity(kw, known_kw) > 0.75:
                score[persona] += 1
                detail[persona].append(kw)
                break
    return dict(score), dict(detail)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--result_json", type=str, help="분석 결과 result_*.json 파일 경로")
    parser.add_argument("--image", type=str, help="분석할 원본 이미지 파일명 (예: test5.jpg 또는 test5)")
    parser.add_argument("--emotion_json", type=str, help="emotion_keywords.json 파일 경로 (기본값: ../docs/emotion_keywords.json)")
    args = parser.parse_args()

    # result_json이 없고 image가 있으면 자동 경로 생성
    result_json_path = args.result_json
    if not result_json_path and args.image:
        image_base = args.image
        if image_base.endswith('.jpg'):
            image_base = image_base[:-4]
        result_json_path = os.path.join(RESULT_DIR, f'result_{image_base}.json')

    if not result_json_path:
        print("Error: --result_json 또는 --image 인자 중 하나는 반드시 입력해야 합니다.")
        exit(1)

    # emotion_keywords.json 경로 지정
    emotion_json_path = args.emotion_json if args.emotion_json else os.path.join(DOCS_DIR, 'emotion_keywords.json')
    keyword_to_type = load_emotion_keywords(emotion_json_path)
    keywords = extract_keywords_from_result_json(result_json_path)
    result, detail = score_by_result_keywords(keywords, keyword_to_type)

    print("감정 유형 점수 및 기여 키워드:")
    for k, v in result.items():
        print(f"{k}: {v}  (키워드: {detail.get(k, [])})")

    if result:
        best_type = max(result, key=result.get)
        print(f"\n당신의 유형은 {best_type}입니다")

