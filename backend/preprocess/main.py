import os
import sys
import json
from talk_extract_text import extract_keywords
from talk_generate_keywords import extract_data
from book_extract_keywords import extract_book_keywords
from book_generate_text import generate_book_text
from chat_extract_text import extract_chat_text

def run_function(func, description):
    """함수를 실행하고 결과를 출력합니다."""
    print(f"\n{'='*50}")
    print(f"{description} 실행 중...")
    print(f"{'='*50}")
    
    try:
        result = func()
        if result:
            print(f"✅ {description} 완료!")
        else:
            print(f"❌ {description} 실패!")
            return False
    except Exception as e:
        print(f"❌ {description} 실행 중 오류 발생: {e}")
        return False
    
    return True

def main():
    """모든 전처리 스크립트를 순서대로 실행합니다."""
    print(" 전처리 스크립트 실행을 시작합니다...")
    
    # 현재 디렉토리를 preprocess 폴더로 변경
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # result 폴더 생성 (이미 존재하면 무시)
    os.makedirs("result", exist_ok=True)
    
    # 실행할 함수들 (순서대로)
    functions = [
        (extract_keywords, "1. 대화 텍스트 추출 (talk_extract_text.py)"),
        (extract_data, "2. 대화 키워드 생성 (talk_generate_keywords.py)"),
        (extract_book_keywords, "3. 논문 키워드 추출 (book_extract_keywords.py)"),
        (generate_book_text, "4. 논문 키워드 텍스트 생성 (book_generate_text.py)"),
        (extract_chat_text, "5. 챗봇 텍스트 추출 (chat_extract_text.py)")
    ]
    
    success_count = 0
    
    for func, description in functions:
        if run_function(func, description):
            success_count += 1
        else:
            print(f"\n{description} 실행 실패로 인해 전체 프로세스를 중단합니다.")
            break
    
    print(f"\n{'='*50}")
    print(f"전처리 완료 요약")
    print(f"{'='*50}")
    print(f"총 {len(functions)}개 함수 중 {success_count}개 성공")
    
    # 결과 파일들 확인
    result_files = []
    if os.path.exists("result"):
        for file in os.listdir("result"):
            if file.endswith((".json", ".csv", ".txt")):
                result_files.append(file)
    
    if result_files:
        print(f"\n생성된 결과 파일들:")
        for file in sorted(result_files):
            file_path = os.path.join("result", file)
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            print(f"   - result/{file} ({file_size} bytes)")
    
    if success_count == len(functions):
        print(f"\n전처리 프로세스가 성공적으로 완료되었습니다!")
    else:
        print(f"\n전처리 프로세스 중 일부가 실패했습니다. ({success_count}/{len(functions)})")

if __name__ == "__main__":
    main()