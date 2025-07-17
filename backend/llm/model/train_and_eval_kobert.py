import os
import pandas as pd
from datasets import Dataset
from evaluate import load
from sklearn.metrics import f1_score, accuracy_score, precision_score, recall_score
from transformers import AutoTokenizer, BertForSequenceClassification, Trainer, TrainingArguments
from sklearn.model_selection import train_test_split
import torch
import json

# 현재 파일 기준으로 상위 두 단계 위의 data 폴더 경로를 지정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "../../data/emotion_persona_1000.csv")

def train_model():
    df = pd.read_csv(DATA_PATH)  # columns=["text", "label"]

    # label을 숫자 인덱스로 변환
    label2id = {"추진형": 0, "내면형": 1, "안정형": 2, "관계형": 3, "쾌락형": 4}
    id2label = {v: k for k, v in label2id.items()}
    df["label_id"] = df["label"].map(label2id)

    # Trainer가 'label' 컬럼을 자동으로 사용하므로, label_id를 label로 복사
    # (문자형 label 컬럼을 숫자로 덮어씀)
    df["label"] = df["label_id"]

    # 2. 클래스 불균형 확인 (선택)
    print(df['label'].value_counts())

    # 3. 학습/평가 데이터 분리 (8:2)
    train_df, eval_df = train_test_split(df, test_size=0.2, stratify=df['label'], random_state=42)
    train_dataset = Dataset.from_pandas(train_df)
    eval_dataset = Dataset.from_pandas(eval_df)

    # 4. 토크나이저 및 데이터 전처리
    KOBERT_MODEL = "skt/kobert-base-v1"
    tokenizer = AutoTokenizer.from_pretrained(KOBERT_MODEL)

    def preprocess(example):
        return tokenizer(example["text"], truncation=True, padding="max_length", max_length=128)

    train_dataset = train_dataset.map(preprocess, batched=True)
    eval_dataset = eval_dataset.map(preprocess, batched=True)

    # 5. KoBERT 분류 모델 준비
    model = BertForSequenceClassification.from_pretrained(KOBERT_MODEL, num_labels=5)

    # 6. Trainer 설정
    training_args = TrainingArguments(
        output_dir=os.path.join(BASE_DIR, "kobert_model"),
        per_device_train_batch_size=8,
        per_device_eval_batch_size=16,
        num_train_epochs=5,
        learning_rate=2e-5,
        weight_decay=0.01,
        warmup_steps=100,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        logging_dir=os.path.join(BASE_DIR, "logs"),
        load_best_model_at_end=True,
        metric_for_best_model="macro_f1",
        logging_steps=50,
        save_total_limit=3,
    )

    # 7. 평가 지표 정의
    accuracy_metric = load("accuracy")
    precision_metric = load("precision")
    recall_metric = load("recall")
    f1_metric = load("f1")

    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        preds = logits.argmax(axis=-1)
        acc = accuracy_metric.compute(predictions=preds, references=labels)["accuracy"]
        prec = precision_metric.compute(predictions=preds, references=labels, average="macro")["precision"]
        rec = recall_metric.compute(predictions=preds, references=labels, average="macro")["recall"]
        macro_f1 = f1_metric.compute(predictions=preds, references=labels, average="macro")["f1"]
        return {
            "accuracy": acc,
            "precision": prec,
            "recall": rec,
            "macro_f1": macro_f1
        }

    # 8. Trainer 객체 생성 및 학습
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        compute_metrics=compute_metrics,
    )

    trainer.train()

    # 9. 평가
    eval_result = trainer.evaluate()
    loss = eval_result.get("eval_loss", None)
    acc = eval_result.get("eval_accuracy", None)
    prec = eval_result.get("eval_precision", None)
    rec = eval_result.get("eval_recall", None)
    f1 = eval_result.get("eval_macro_f1", None)

    # 10. 모델 저장
    model_save_path = os.path.join(BASE_DIR, "kobert_model")
    model.save_pretrained(model_save_path)
    tokenizer.save_pretrained(model_save_path)
    
    # 평가 결과를 파일에 저장
    eval_metrics = {
        "loss": loss,
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "macro_f1": f1
    }
    with open(os.path.join(model_save_path, "eval_metrics.json"), "w", encoding="utf-8") as f:
        json.dump(eval_metrics, f, ensure_ascii=False, indent=2)

# 11. 예측 함수 예시
def predict_persona(text, model_dir=None):
    if model_dir is None:
        model_dir = os.path.join(BASE_DIR, "kobert_model")
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model = BertForSequenceClassification.from_pretrained(model_dir)
    model.eval()
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding="max_length", max_length=128)
    # token_type_ids 제거
    if "token_type_ids" in inputs:
        del inputs["token_type_ids"]
    with torch.no_grad():
        outputs = model(**inputs)
        pred = torch.argmax(outputs.logits, dim=1).item()
    id2label = {0: "추진형", 1: "내면형", 2: "안정형", 3: "관계형", 4: "쾌락형"}
    return id2label[pred]

def get_raw_text_from_result_json(result_json_path):
    with open(result_json_path, encoding="utf-8") as f:
        result = json.load(f)
    return result.get("raw_text", "")

def run_persona_prediction_from_result(image_base, quiet=True):
    result_json_path = os.path.join(BASE_DIR, f"../../LLM/detection_results/results/result_{image_base}.json")
    test_text = get_raw_text_from_result_json(result_json_path)
    
    # 모델 경로 설정
    model_path = os.path.join(BASE_DIR, "kobert_model")
    eval_metrics_path = os.path.join(model_path, "eval_metrics.json")
    
    # 저장된 평가 결과가 있으면 출력
    if os.path.exists(eval_metrics_path):
        with open(eval_metrics_path, "r", encoding="utf-8") as f:
            eval_metrics = json.load(f)
        
        print("\n [최종 평가 결과]")
        if eval_metrics.get("loss") is not None:
            print(f"Loss: {eval_metrics['loss']:.4f}")
        if eval_metrics.get("accuracy") is not None:
            print(f"Accuracy: {eval_metrics['accuracy']:.4f}")
        if eval_metrics.get("precision") is not None:
            print(f"Precision: {eval_metrics['precision']:.4f}")
        if eval_metrics.get("recall") is not None:
            print(f"Recall: {eval_metrics['recall']:.4f}")
        if eval_metrics.get("macro_f1") is not None:
            print(f"Macro F1 Score: {eval_metrics['macro_f1']:.4f}")
    
    persona = predict_persona(test_text)
    print(f"\n[예측 결과] : 당신의 유형은 {persona}입니다.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="KoBERT 기반 감정 유형 분류 실행")
    parser.add_argument('--image', type=str, default="test5", help='분석할 원본 이미지 파일명 (예: test5.jpg 또는 test5)')
    parser.add_argument('--train', action='store_true', help='모델 학습 실행')
    args = parser.parse_args()
    
    if args.train:
        train_model()
    else:
        image_base = args.image
        if image_base.endswith('.jpg'):
            image_base = image_base[:-4]
        run_persona_prediction_from_result(image_base)

