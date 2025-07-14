import subprocess
import argparse
import os
import sys
sys.path.append(os.path.dirname(__file__))

MODEL_DIR = os.path.dirname(__file__)
DOCS_DIR = os.path.join(os.path.dirname(__file__), '../docs')
TEST_IMG_DIR = os.path.join(os.path.dirname(__file__), '../test_images')

def main():
    parser = argparse.ArgumentParser(description="이미지 분석 전체 파이프라인 실행")
    parser.add_argument('--image', type=str, required=True, help='분석할 원본 이미지 파일명 (예: test4.jpg 또는 test4)')
    parser.add_argument('--embedding', action='store_true', help='임베딩 기반 감정유형 분석까지 실행')
    args = parser.parse_args()

    image_arg = args.image
    image_base = os.path.splitext(image_arg)[0]
    image_path = image_arg if image_arg.endswith('.jpg') else image_base + '.jpg'

    # 1. crop_by_labels.py 실행
    print("[1/3] 객체 탐지 및 결과 이미지 생성 중...")
    subprocess.run(['python', 'crop_by_labels.py', '--image', os.path.join(TEST_IMG_DIR, image_path)], cwd=os.path.dirname(__file__) or '.')

    # 2. analyze_images_with_gpt.py 실행
    print("[2/3] GPT 분석 실행 중...")
    subprocess.run(['python', 'analyze_images_with_gpt.py', '--image', image_base], cwd=os.path.dirname(__file__) or '.')

    # 3. run_scoring.py 실행 (embedding 옵션에 따라)
    print("[3/3] 점수 계산 및 감정유형 분석 중...")
    scoring_cmd = ['python', 'run_scoring.py', '--image', image_base]
    if args.embedding:
        scoring_cmd.append('--embedding')
    subprocess.run(scoring_cmd, cwd=os.path.dirname(__file__) or '.')

if __name__ == "__main__":
    main() 