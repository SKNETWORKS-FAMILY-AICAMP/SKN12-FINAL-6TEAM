import json
import os
from openai import OpenAI
from dotenv import load_dotenv

# .env에서 API 키 로드
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=api_key)

def generate_sentence(label, keyword):
    prompt = f"""
        너는 감정이 풍부한 상담용 AI 챗봇이야.  
        주어진 **성격 유형(label)**과 **형용사 키워드(keyword)**를 바탕으로,  
        해당 인물이 스스로의 감정을 말하듯 **1인칭으로 자연스럽고 감정적인 문장** 하나를 생성해줘.

        - 형식: 1문장, 자연스럽고 짧게
        - 말투: 자기 감정을 털어놓듯 말하는 방식
        - 주어는 "나" 또는 생략된 형태로 (예: "항상 완벽하고 싶어요")
        - 너무 딱딱하거나 설명적인 문장은 피하고, 진심이 느껴지도록

        예시:
        - label: 추진형, keyword: 철저하다 → "작은 실수도 용납할 수 없어요, 항상 완벽하고 싶거든요."
        - label: 관계형, keyword: 따뜻하다 → "따뜻한 말 한마디가 정말 오래 기억에 남더라고요."

        이제 다음 정보를 참고해서 문장을 생성해줘.

        성격 유형: {label}  
        형용사 키워드: {keyword}
        """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.75,
    )
    return response.choices[0].message.content.strip()

def generate_book_text():
    """
    책 키워드 데이터로부터 텍스트를 생성하는 함수
    """
    if not api_key:
        print("error : OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
        return False

    # JSON 불러오기
    input_path = os.path.join(os.path.dirname(__file__), "result/book_keywords.json")
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            keyword_data = json.load(f)
    except FileNotFoundError:
        print(f"error : '{input_path}' 파일을 찾을 수 없습니다.")
        return False

    augmented_data = []

    for item in keyword_data:
        label = item["label"]
        keyword = item["keyword"]
        try:
            text = generate_sentence(label, keyword)
            augmented_data.append({
                "label": label,
                "keyword": keyword,
                "text": text
            })
            print(f"생성 완료: {label} / {keyword}")
        except Exception as e:
            print(f"오류 발생: {label} / {keyword} → {e}")
            augmented_data.append({
                "label": label,
                "keyword": keyword,
                "text": None
            })

    # 출력 파일 경로 설정
    output_path = os.path.join(os.path.dirname(__file__), "result/book_keywords_text.json")
    # 출력 디렉토리가 없으면 생성
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(augmented_data, f, ensure_ascii=False, indent=2)
        print(f" 모든 문장 생성 완료! → {output_path} 저장됨")
        return True
    except IOError as e:
        print(f"error : 파일 저장 중 오류 발생 - {e}")
        return False

if __name__ == "__main__":
    generate_book_text()
