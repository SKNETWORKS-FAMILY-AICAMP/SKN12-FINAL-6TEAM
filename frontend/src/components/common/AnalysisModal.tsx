import React from 'react';
import Modal from './Modal';

interface AnalysisModalProps {
  isOpen: boolean;
}

const AnalysisModal: React.FC<AnalysisModalProps> = ({ isOpen }) => {
  return (
    <Modal isOpen={isOpen} onClose={() => {}} className="analysis-loading-modal">
      <div className="analysis-loading-content">
        <div className="analysis-spinner">
          <div className="spinner-circle"></div>
          <div className="spinner-circle"></div>
          <div className="spinner-circle"></div>
        </div>
        
        <h2>그림을 분석하고 있습니다</h2>
        <p>AI가 당신의 그림을 분석하여<br />심리 상태를 파악하고 있습니다</p>
        
        <div className="analysis-steps">
          <div className="step-indicator">
            <div className="step-dot active"></div>
            <span>이미지 처리</span>
          </div>
          <div className="step-indicator">
            <div className="step-dot active"></div>
            <span>패턴 분석</span>
          </div>
          <div className="step-indicator">
            <div className="step-dot loading"></div>
            <span>결과 생성</span>
          </div>
        </div>
        
        <div className="loading-message">
          잠시만 기다려주세요...
        </div>
      </div>
    </Modal>
  );
};

export default AnalysisModal;