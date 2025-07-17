import os
import sys
import subprocess
import json

def run_script(script_name, description):
    """스크립트를 실행하고 결과를 출력합니다."""
    print(f"\n{'='*50}")
    print(f"🚀 {description} 실행 중...")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print(f" {description} 완료!")
            if result.stdout:
                print(result.stdout)
        else:
            print(f" {description} 실패!")
            if result.stderr:
                print(f"에러: {result.stderr}")
            return False
    except Exception as e:
        print(f" {description} 실행 중 오류 발생: {e}")
        return False
    
    return True

def main():
    """모든 전처리 스크립트를 순서대로 실행합니다."""
    print("🔧 전처리 스크립트 실행을 시작합니다...")
    
    # 현재 디렉토리를 preprocess 폴더로 변경
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # result 폴더 생성 (이미 존재하면 무시)
    os.makedirs("result", exist_ok=True)
    
    # 실행할 스크립트들 (순서대로)
    scripts = [
        ("book_extract_keywords.py", "도서 키워드 추출"),
        ("talk_extract_data.py", "대화 데이터 추출"),
        ("talk_extract_keyword.py", "대화 키워드 추출"),
    ]
    
    success_count = 0
    
    for script_name, description in scripts:
        if os.path.exists(script_name):
            if run_script(script_name, description):
                success_count += 1
            else:
                print(f"\n {script_name} 실행 실패로 인해 전체 프로세스를 중단합니다.")
                break
        else:
            print(f"{script_name} 파일을 찾을 수 없습니다.")
    
    print(f"\n{'='*50}")
    print(f"전처리 완료 요약")
    print(f"{'='*50}")
    print(f"총 {len(scripts)}개 스크립트 중 {success_count}개 성공")
    
    # 결과 파일들 확인
    result_files = []
    for file in os.listdir("result"):
        if file.endswith((".json", ".csv")):
            result_files.append(file)
    
    if result_files:
        print(f"\n 생성된 결과 파일들:")
        for file in result_files:
            print(f"   - result/{file}")
    
    print(f"\n 전처리 프로세스가 완료되었습니다!")

if __name__ == "__main__":
    main()