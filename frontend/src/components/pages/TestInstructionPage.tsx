import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Navigation from '../common/Navigation';
import ConsentModal from '../common/ConsentModal';
import AnalysisModal from '../common/AnalysisModal';

interface TestInstructionPageProps {
  onStartAnalysis: (imageFile: File | null, description: string) => void;
  onNavigate?: (screen: string) => void;
}

const TestInstructionPage: React.FC<TestInstructionPageProps> = ({ onStartAnalysis, onNavigate }) => {
  const navigate = useNavigate();
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [description, setDescription] = useState('');
  const [isDragOver, setIsDragOver] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showConsentModal, setShowConsentModal] = useState(false);

  const handleImageSelect = (file: File) => {
    setSelectedImage(file);
    
    const reader = new FileReader();
    reader.onload = (e) => {
      setImagePreview(e.target?.result as string);
    };
    reader.readAsDataURL(file);
  };

  const handleFileInput = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type.startsWith('image/')) {
      handleImageSelect(file);
    }
  };

  const handleDragOver = (event: React.DragEvent) => {
    event.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (event: React.DragEvent) => {
    event.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (event: React.DragEvent) => {
    event.preventDefault();
    setIsDragOver(false);
    
    const file = event.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      handleImageSelect(file);
    }
  };

  const handleStartTest = () => {
    setShowConsentModal(true);
  };

  const handleConsentAgree = () => {
    setShowConsentModal(false);
  };

  const handleConsentClose = () => {
    setShowConsentModal(false);
  };

  const handleAnalysis = () => {
    setIsAnalyzing(true);
    
    setTimeout(() => {
      onStartAnalysis(selectedImage, description);
      setIsAnalyzing(false);
      navigate('/results');
    }, 3000);
  };

  const canAnalyze = selectedImage !== null && !isAnalyzing;

  return (
    <div className="test-screen">
      <Navigation onNavigate={onNavigate} />
      
      <div className="test-container">
        <div className="test-header">
          <h1>HTP 심리검사</h1>
          <p>그림을 업로드하고 설명을 작성해주세요</p>
        </div>

        <div className="test-content">
          <div className="upload-section">
            <div className="section-header">
              <span className="section-icon">🖼️</span>
              <h2>그림 업로드</h2>
            </div>
            
            <div 
              className={`upload-area ${isDragOver ? 'drag-over' : ''} ${selectedImage ? 'has-image' : ''}`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              {imagePreview ? (
                <div className="image-preview">
                  <img src={imagePreview} alt="업로드된 그림" />
                  <div className="image-overlay">
                    <button 
                      className="change-image-btn"
                      onClick={() => document.getElementById('file-input')?.click()}
                    >
                      이미지 변경
                    </button>
                  </div>
                </div>
              ) : (
                <div className="upload-placeholder">
                  <div className="upload-icon">☁️</div>
                  <p>또는 여기에 파일을 드래그해서 놓으세요</p>
                  <button 
                    className="upload-btn"
                    onClick={() => document.getElementById('file-input')?.click()}
                  >
                    📁 파일 선택하기
                  </button>
                </div>
              )}
              
              <input
                id="file-input"
                type="file"
                accept="image/*"
                onChange={handleFileInput}
                style={{ display: 'none' }}
              />
            </div>
          </div>

          <div className="description-section">
            <div className="section-header">
              <span className="section-icon">✏️</span>
              <h2>그림 설명</h2>
            </div>
            
            <div className="description-area">
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="그림에 대한 설명을 입력하세요. 예: 어떤 기분으로 그렸는지, 특별한 의미가 있는지 등..."
                className="description-input"
                rows={6}
              />
              <div className="description-info">
                <span className="optional-label">선택사항</span>
                <span className="char-count">{description.length}/500</span>
              </div>
            </div>
          </div>

          <div className="analysis-section">
            <button 
              className={`analysis-btn ${canAnalyze ? 'enabled' : 'disabled'}`}
              onClick={handleAnalysis}
              disabled={!canAnalyze}
            >
              {isAnalyzing ? '분석 중...' : canAnalyze ? '🔍 분석 시작하기' : '이미지를 업로드해주세요'}
            </button>
            
            {canAnalyze && !isAnalyzing && (
              <p className="analysis-notice">
                업로드된 이미지를 분석하여 심리 상태를 파악합니다
              </p>
            )}
          </div>
        </div>
      </div>

      <ConsentModal 
        isOpen={showConsentModal}
        onClose={handleConsentClose}
        onAgree={handleConsentAgree}
      />
      
      <AnalysisModal isOpen={isAnalyzing} />
    </div>
  );
};

export default TestInstructionPage;