import PyPDF2
import re
import json

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

# PDF 파일 열기
with open("./data/성격유형별 선호도서 추천을 위한 서평 키워드 유효성 연구.pdf", "rb") as file:
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()

        entries = re.split(r'(\d)번 유형', text)

        for i in range(1, len(entries) - 1, 2):
            type_number = entries[i]
            label = type_to_label.get(type_number.strip(), None)
            if not label:
                continue

            keywords_block = entries[i + 1]
            keywords = re.findall(r'[가-힣]+하다', keywords_block)

            for kw in keywords:
                results.append({
                    "label": label,
                    "keyword": kw
                })

# 결과 JSON 파일로 저장
with open("result/personality_keywords_labeled.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("키워드 추출 완료! -> result/personality_keywords_labeled.json 파일 생성됨")
