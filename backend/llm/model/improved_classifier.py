import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler
from transformers import AutoTokenizer, AutoModel
import torch.nn.functional as F
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.utils.class_weight import compute_class_weight
from collections import Counter
from tqdm import tqdm
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import random; import numpy as np; import torch
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)
    
warnings.filterwarnings('ignore')

class KeywordDataset(Dataset):
    def __init__(self, keywords, labels, tokenizer, max_len=64):
        self.keywords = keywords
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len
    
    def __len__(self):
        return len(self.keywords)
    
    def __getitem__(self, idx):
        keyword = str(self.keywords[idx])
        label = self.labels[idx]
        
        encoding = self.tokenizer(
            keyword,
            add_special_tokens=True,
            max_length=self.max_len,
            return_token_type_ids=False,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
        )
        
        return {
            'keyword_text': keyword,
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

class ImprovedKoBERTClassifier(nn.Module):
    def __init__(self, n_classes, model_name='klue/bert-base', dropout_rate=0.3):
        super(ImprovedKoBERTClassifier, self).__init__()
        self.bert = AutoModel.from_pretrained(model_name)
        self.dropout1 = nn.Dropout(dropout_rate)
        self.dropout2 = nn.Dropout(dropout_rate)
        
        # 더 복잡한 분류기 구조
        self.classifier = nn.Sequential(
            nn.Linear(self.bert.config.hidden_size, 256),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(128, n_classes)
        )
        
        # 배치 정규화 추가
        self.batch_norm = nn.BatchNorm1d(self.bert.config.hidden_size)
    
    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        
        if hasattr(outputs, 'pooler_output') and outputs.pooler_output is not None:
            pooled_output = outputs.pooler_output
        else:
            pooled_output = outputs.last_hidden_state[:, 0, :]
        
        # 배치 정규화 적용
        pooled_output = self.batch_norm(pooled_output)
        pooled_output = self.dropout1(pooled_output)
        
        return self.classifier(pooled_output)

class ImprovedKeywordClassifierTrainer:
    def __init__(self, model_name='klue/bert-base'):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.label_to_idx = {}
        self.idx_to_label = {}
        self.model = None
        self.class_weights = None
        
    def preprocess_data(self, file_path='keyword.md'):
        """데이터 전처리 - 중복 제거 및 데이터 증강"""
        print("데이터 전처리 중...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        keywords = []
        labels = []
        
        # 키워드-라벨 쌍을 딕셔너리로 저장하여 중복 처리
        keyword_label_dict = {}
        
        for line in lines[2:]:
            parts = line.strip().split('|')
            if len(parts) >= 3:
                keyword_text = parts[1].strip()
                label = parts[2].strip()
                
                individual_keywords = [k.strip() for k in keyword_text.split(',') if k.strip()]
                
                for keyword in individual_keywords:
                    if keyword in keyword_label_dict:
                        # 중복 키워드가 있으면 기존 라벨과 비교
                        if keyword_label_dict[keyword] != label:
                            print(f"중복 키워드 발견: '{keyword}' - {keyword_label_dict[keyword]} vs {label}")
                            # 첫 번째 라벨을 유지
                            continue
                    else:
                        keyword_label_dict[keyword] = label
        
        # 딕셔너리에서 리스트로 변환
        for keyword, label in keyword_label_dict.items():
            keywords.append(keyword)
            labels.append(label)
        
        print(f"중복 제거 후 {len(keywords)}개의 고유 키워드")
        
        # 데이터 증강: 유사한 의미의 키워드 조합 생성
        augmented_keywords, augmented_labels = self.augment_data(keywords, labels)
        
        return augmented_keywords, augmented_labels
    
    def augment_data(self, keywords, labels):
        """데이터 증강 – 키워드 조합 생성 + 소수 클래스 오버샘플링"""
        print("데이터 증강 중...")

        # 라벨별 키워드 그룹화
        label_keywords = {}
        for kw, lb in zip(keywords, labels):
            label_keywords.setdefault(lb, []).append(kw)

        augmented_kws, augmented_lbs = keywords.copy(), labels.copy()

        # 클래스별 원본 샘플 수
        counts = {lb: len(kws) for lb, kws in label_keywords.items()}
        max_count = max(counts.values())

        for lb, kws in label_keywords.items():
            n = len(kws)
            # 1) 기존 방식대로 조합 생성 (최대 50개)
            for i in range(min(50, n)):
                for j in range(i+1, min(i+4, n)):
                    augmented_kws.append(f"{kws[i]} {kws[j]}")
                    augmented_lbs.append(lb)

            # 2) 소수 클래스 오버샘플링: max_count만큼 맞춰주기
            if n < max_count:
                needed = max_count - n
                for _ in range(needed):
                    i, j = np.random.choice(n, 2, replace=True)
                    augmented_kws.append(f"{kws[i]} {kws[j]}")
                    augmented_lbs.append(lb)

        print(f"데이터 증강 후 총 {len(augmented_kws)}개 샘플")
        return augmented_kws, augmented_lbs
    
    def calculate_class_weights(self, labels):
        """클래스 불균형 해결을 위한 가중치 계산"""
        unique_labels = list(set(labels))
        class_weights = compute_class_weight(
            'balanced',
            classes=np.array(range(len(unique_labels))),
            y=[self.label_to_idx[label] for label in labels]
        )
        return torch.FloatTensor(class_weights).to(self.device)
    
    def load_data(self, file_path='keyword.md'):
        """데이터 로드 및 전처리"""
        keywords, labels = self.preprocess_data(file_path)
        
        # 라벨 인덱스 매핑 생성
        unique_labels = list(set(labels))
        self.label_to_idx = {label: idx for idx, label in enumerate(unique_labels)}
        self.idx_to_label = {idx: label for label, idx in self.label_to_idx.items()}
        
        # 라벨을 숫자로 변환
        label_indices = [self.label_to_idx[label] for label in labels]
        
        # 클래스 가중치 계산
        self.class_weights = self.calculate_class_weights(labels)
        
        print(f"라벨 분포:")
        label_counts = Counter(labels)
        for label, count in label_counts.items():
            print(f"  {label}: {count}개")
        
        return keywords, label_indices
    
    def create_data_loader(self, keywords, labels, batch_size=32, max_len=64, use_weighted_sampler=True):
        """데이터 로더 생성 (가중치 샘플링 옵션)"""
        dataset = KeywordDataset(
            keywords=keywords,
            labels=labels,
            tokenizer=self.tokenizer,
            max_len=max_len
        )
        
        if use_weighted_sampler:
            # 클래스 불균형 해결을 위한 가중치 샘플링
            label_counts = Counter(labels)
            weights = [1.0 / label_counts[label] for label in labels]
            sampler = WeightedRandomSampler(weights, len(weights))
            return DataLoader(dataset, batch_size=batch_size, sampler=sampler)
        else:
            return DataLoader(dataset, batch_size=batch_size, shuffle=True)
    
    def train_model(self, epochs=15, batch_size=32, learning_rate=3e-5, warmup_steps=100):
        """개선된 모델 학습"""
        print("개선된 모델 학습을 시작합니다...")
        
        # 데이터 로드
        keywords, labels = self.load_data()
        
        # 훈련/검증 데이터 분할 (층화 추출)
        X_train, X_val, y_train, y_val = train_test_split(
            keywords, labels, test_size=0.2, random_state=42, stratify=labels
        )
        
        # 데이터 로더 생성
        train_loader = self.create_data_loader(X_train, y_train, batch_size, use_weighted_sampler=True)
        val_loader = self.create_data_loader(X_val, y_val, batch_size, use_weighted_sampler=False)
        
        # 모델 초기화
        n_classes = len(self.label_to_idx)
        self.model = ImprovedKoBERTClassifier(n_classes=n_classes, model_name=self.model_name)
        self.model = self.model.to(self.device)
        
        # 옵티마이저와 스케줄러
        optimizer = torch.optim.AdamW(self.model.parameters(), lr=learning_rate, weight_decay=0.01)
        
        # 학습률 스케줄러
        total_steps = len(train_loader) * epochs
        scheduler = torch.optim.lr_scheduler.LinearLR(
            optimizer, start_factor=0.1, total_iters=warmup_steps
        )
        
        # 가중치가 적용된 손실 함수
        criterion = nn.CrossEntropyLoss(weight=self.class_weights)
        
        # 조기 종료를 위한 변수
        best_val_accuracy = 0
        patience = 5
        patience_counter = 0
        
        train_losses = []
        val_accuracies = []
        
        for epoch in range(epochs):
            # 훈련
            self.model.train()
            total_loss = 0
            
            for batch in tqdm(train_loader, desc=f'Epoch {epoch+1}/{epochs}'):
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels_batch = batch['labels'].to(self.device)
                
                optimizer.zero_grad()
                outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
                loss = criterion(outputs, labels_batch)
                loss.backward()
                
                # 그래디언트 클리핑
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                
                optimizer.step()
                if epoch == 0 and len(train_losses) < warmup_steps:
                    scheduler.step()
                
                total_loss += loss.item()
            
            avg_train_loss = total_loss / len(train_loader)
            train_losses.append(avg_train_loss)
            
            # 검증
            self.model.eval()
            val_predictions = []
            val_true_labels = []
            
            with torch.no_grad():
                for batch in val_loader:
                    input_ids = batch['input_ids'].to(self.device)
                    attention_mask = batch['attention_mask'].to(self.device)
                    labels_batch = batch['labels'].to(self.device)
                    
                    outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
                    _, preds = torch.max(outputs, dim=1)
                    
                    val_predictions.extend(preds.cpu().tolist())
                    val_true_labels.extend(labels_batch.cpu().tolist())
            
            val_accuracy = accuracy_score(val_true_labels, val_predictions)
            val_accuracies.append(val_accuracy)
            
            print(f'Epoch {epoch+1}/{epochs}:')
            print(f'  평균 훈련 손실: {avg_train_loss:.4f}')
            print(f'  검증 정확도: {val_accuracy:.4f}')
            
            # 조기 종료 확인
            if val_accuracy > best_val_accuracy:
                best_val_accuracy = val_accuracy
                patience_counter = 0
                # 최고 성능 모델 저장
                torch.save(self.model.state_dict(), 'best_keyword_classifier.pth')
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    print(f"조기 종료: {patience} 에포크 동안 성능 향상이 없습니다.")
                    break
            
            print('-' * 50)
        
        # 최종 분류 리포트
        print("\n=== 최종 성능 리포트 ===")
        print(f"최고 검증 정확도: {best_val_accuracy:.4f}")
        
        # 라벨별 성능 확인
        print("\n라벨별 분류 리포트:")
        target_names = [self.idx_to_label[i] for i in range(len(self.idx_to_label))]
        print(classification_report(val_true_labels, val_predictions, target_names=target_names))
        
        return train_losses, val_accuracies
    
    def load_model(self, model_path='best_keyword_classifier.pth'):
        """저장된 모델 로드"""
        if self.model is None:
            _, _ = self.load_data()
            n_classes = len(self.label_to_idx)
            self.model = ImprovedKoBERTClassifier(n_classes=n_classes, model_name=self.model_name)
        
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model = self.model.to(self.device)
        self.model.eval()
        print(f"모델이 '{model_path}'에서 로드되었습니다.")
    
    def predict(self, keyword, model_path=None):
        """키워드 분류 예측"""
        if self.model is None:
            if model_path:
                self.load_model(model_path)
            else:
                print("학습된 모델이 없습니다.")
                return None, None, None
        
        encoding = self.tokenizer(
            keyword,
            add_special_tokens=True,
            max_length=64,
            return_token_type_ids=False,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
        )
        
        input_ids = encoding['input_ids'].to(self.device)
        attention_mask = encoding['attention_mask'].to(self.device)
        
        with torch.no_grad():
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
            probabilities = F.softmax(outputs, dim=1)
            predicted_class = torch.argmax(probabilities, dim=1).item()
            confidence = probabilities[0][predicted_class].item()
        
        predicted_label = self.idx_to_label[predicted_class]
        
        all_probabilities = {}
        for idx, prob in enumerate(probabilities[0]):
            label = self.idx_to_label[idx]
            all_probabilities[label] = prob.item()
        
        return predicted_label, confidence, all_probabilities

def main():
    """메인 실행 함수"""
    trainer = ImprovedKeywordClassifierTrainer()
    
    while True:
        print("\n=== 개선된 KoBERT 키워드 분류기 ===")
        print("1. 모델 학습 (개선된 버전)")
        print("2. 키워드 분류")
        print("3. 종료")
        
        choice = input("\n선택하세요 (1-3): ").strip()
        
        if choice == '1':
            epochs = int(input("학습 에포크 수를 입력하세요 (기본값: 15): ") or "15")
            train_losses, val_accuracies = trainer.train_model(epochs=epochs)
            print(f"\n학습 완료! 최고 검증 정확도: {max(val_accuracies):.4f}")
            
        elif choice == '2':
            try:
                trainer.load_model()
                
                while True:
                    keyword = input("\n분류할 키워드를 입력하세요 (돌아가려면 'q'): ").strip()
                    
                    if keyword.lower() == 'q':
                        break
                    
                    if not keyword:
                        continue
                    
                    predicted_label, confidence, all_probabilities = trainer.predict(keyword)
                    
                    if predicted_label:
                        print(f"\n키워드: '{keyword}'")
                        print(f"예측 라벨: {predicted_label}")
                        print(f"신뢰도: {confidence:.4f} ({confidence*100:.2f}%)")
                        print("\n모든 라벨별 확률:")
                        for label, prob in sorted(all_probabilities.items(), key=lambda x: x[1], reverse=True):
                            print(f"  {label}: {prob:.4f} ({prob*100:.2f}%)")
                        
            except FileNotFoundError:
                print("저장된 모델이 없습니다. 먼저 모델을 학습해주세요.")
                
        elif choice == '3':
            print("프로그램을 종료합니다.")
            break
            
        else:
            print("잘못된 선택입니다.")

if __name__ == "__main__":
    main()