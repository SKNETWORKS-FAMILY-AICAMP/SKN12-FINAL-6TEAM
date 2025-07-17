import subprocess
import argparse
import os
import sys
import json
from train_and_eval_kobert import run_persona_prediction_from_result
sys.path.append(os.path.dirname(__file__))

MODEL_DIR = os.path.dirname(__file__)
DOCS_DIR = os.path.join(os.path.dirname(__file__), '../docs')
TEST_IMG_DIR = os.path.join(os.path.dirname(__file__), '../test_images')

def main():
    parser = argparse.ArgumentParser(description="이미지 분석 전체 파이프라인 실행")
    parser.add_argument('--image', type=str, required=True, help='분석할 원본 이미지 파일명 (예: test5.jpg 또는 test5)')
    args = parser.parse_args()

    image_base = args.image
    if image_base.endswith('.jpg'):
        image_base = image_base[:-4]
    image_path = os.path.join(TEST_IMG_DIR, image_base + '.jpg')

    # [1/3] 객체 탐지
    print("[1/3] 객체 탐지 및 결과 이미지 생성 중...")
    subprocess.run(['python', 'crop_by_labels.py', '--image', image_path], cwd=os.path.dirname(__file__) or '.')

    # [2/3] GPT 분석
    print("[2/3] GPT 분석 실행 중...")
    subprocess.run(['python', 'analyze_images_with_gpt.py', '--image', image_base], cwd=os.path.dirname(__file__) or '.')

    # [3/3] 감정 유형화
    print("[3/3] 감정 유형화 결과:")
    run_persona_prediction_from_result(image_base)

if __name__ == "__main__":
    main()