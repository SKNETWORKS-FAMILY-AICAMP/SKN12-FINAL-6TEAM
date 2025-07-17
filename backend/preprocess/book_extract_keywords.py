import PyPDF2
import re
import json
import os

def extract_book_keywords():
    """
    PDF에서 성격 유형별 키워드를 추출합니다.
    """
    # 유형 → 성격 라벨 매핑
    type_to_label = {
        "1": "추진형",
        "3": "추진형", 
        "8": "추진형",
        "2": "관계형",
        "6": "안정형",
        "9": "안정형",
        "7": "쾌락형",
        "4": "내면형",
        "5": "내면형",
    }

    # 결과 담을 리스트
    results = []

    try:
        # PDF 추출 함수
        def extract_section_from_pdf(pdf_path, section_title, next_section_title):
            with open(pdf_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                full_text = ""
                for page in reader.pages:
                    full_text += page.extract_text() + "\n"

            pattern = re.compile(
                rf"{re.escape(section_title)}(.*?)(?={re.escape(next_section_title)}|\Z)",
                re.DOTALL
            )
            match = pattern.search(full_text)
            return match.group(1).strip() if match else ""

        # PDF 경로
        pdf_path = os.path.join(os.path.dirname(__file__), "data/성격유형별_선호도서_추천을_위한_서평_키워드_유효성_연구.pdf")

        # 표 부분 텍스트 추출
        section_text = extract_section_from_pdf(
            pdf_path,
            "<표 8> 성격유형별 형용사 키워드",
            "3.2 도서의 선정"
        )

        # 라벨별 키워드 저장용
        label_keywords = {}

        # 한 줄씩 처리
        lines = section_text.split("\n")
        current_label = None

        for line in lines:
            line = line.strip()
            # 1~9 숫자형 라벨 시작되는 줄인지 확인
            match = re.match(r"^(\d)번", line)
            if match:
                type_num = match.group(1)
                current_label = type_to_label.get(type_num)
                if current_label and current_label not in label_keywords:
                    label_keywords[current_label] = []
                line = line[len(match.group(0)):]  # 숫자부분 제거 후 키워드 처리

            if current_label:
                keywords = re.findall(r"[가-힣]{2,}하다", line)
                label_keywords[current_label].extend(keywords)

        # 중복 제거 + 변환
        results = []
        for label, keywords in label_keywords.items():
            unique_keywords = sorted(set(keywords))
            for kw in unique_keywords:
                results.append({
                    "label": label,
                    "keyword": kw
                })

        # 저장
        output_path = os.path.join(os.path.dirname(__file__), "result/book_keywords.json")
        # 출력 디렉토리가 없으면 생성
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"키워드를 한 줄씩 객체로 변환 완료! → {output_path}")
        return True

    except FileNotFoundError:
        print("error : PDF 파일을 찾을 수 없습니다.")
        return False
    except Exception as e:
        print(f"error : 키워드 추출 중 오류 발생 - {e}")
        return False

if __name__ == "__main__":
    extract_book_keywords()
