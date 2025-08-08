import React, { useState } from 'react';

interface TestResult {
  success: boolean;
  data?: any;
  error?: string;
  timestamp: string;
}

interface PipelineTestPanelProps {
  isVisible: boolean;
  onClose: () => void;
}

const PipelineTestPanel: React.FC<PipelineTestPanelProps> = ({ isVisible, onClose }) => {
  const [results, setResults] = useState<{ [key: string]: TestResult }>({});
  const [loading, setLoading] = useState<{ [key: string]: boolean }>({});

  const testEndpoint = async (endpoint: string, method: string, body?: any) => {
    const testKey = `${method} ${endpoint}`;
    
    setLoading(prev => ({ ...prev, [testKey]: true }));
    
    try {
      // API 기본 URL 설정 (개발 환경)
      const baseUrl = process.env.NODE_ENV === 'development' 
        ? 'http://ec2-3-34-245-132.ap-northeast-2.compute.amazonaws.com/api' 
        : '';
      
      const fullUrl = `${baseUrl}${endpoint}`;
      console.log(`🔗 ${testKey} 요청:`, fullUrl);

      // 다양한 토큰 소스에서 유효한 JWT 토큰 찾기
      let token = localStorage.getItem('token') || 
                  localStorage.getItem('auth_token') || 
                  localStorage.getItem('access_token');
      
      // 쿠키에서도 토큰 찾기 시도
      if (!token) {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
          const [name, value] = cookie.trim().split('=');
          if (name === 'auth_token' || name === 'access_token') {
            token = value;
            break;
          }
        }
      }
      
      console.log(`🔑 ${testKey} 토큰 상태:`, token ? `${token.substring(0, 20)}...` : '토큰 없음');
      
      const headers: Record<string, string> = {
        ...(token && { 'Authorization': `Bearer ${token}` })
      };

      const options: RequestInit = {
        method,
        headers
      };

      if (body) {
        if (body instanceof FormData) {
          // FormData의 경우 Content-Type 헤더를 설정하지 않음 (브라우저가 자동 설정)
          options.body = body;
        } else {
          headers['Content-Type'] = 'application/json';
          options.body = JSON.stringify(body);
        }
      } else {
        headers['Content-Type'] = 'application/json';
      }

      const response = await fetch(fullUrl, options);
      console.log(`📡 ${testKey} 응답:`, response.status, response.headers.get('content-type'));

      let data: any = null;
      let errorMessage: string | undefined = undefined;

      // Content-Type 확인하여 적절하게 파싱
      const contentType = response.headers.get('content-type');
      
      if (contentType && contentType.includes('application/json')) {
        data = await response.json();
      } else {
        const textResponse = await response.text();
        console.warn(`⚠️ ${testKey} JSON이 아닌 응답:`, textResponse.substring(0, 200));
        
        if (!response.ok) {
          errorMessage = `HTTP ${response.status}: ${response.statusText}\n\n응답 내용: ${textResponse.substring(0, 200)}...`;
        } else {
          data = { message: '서버에서 HTML 응답을 받았습니다.', content: textResponse };
        }
      }

      setResults(prev => ({
        ...prev,
        [testKey]: {
          success: response.ok,
          data: response.ok ? data : undefined,
          error: response.ok ? undefined : (errorMessage || `${response.status}: ${data?.detail || response.statusText}`),
          timestamp: new Date().toLocaleTimeString('ko-KR')
        }
      }));

    } catch (error) {
      console.error(`❌ ${testKey} 오류:`, error);
      setResults(prev => ({
        ...prev,
        [testKey]: {
          success: false,
          error: error instanceof Error ? error.message : '알 수 없는 오류',
          timestamp: new Date().toLocaleTimeString('ko-KR')
        }
      }));
    } finally {
      setLoading(prev => ({ ...prev, [testKey]: false }));
    }
  };

  const testHealthCheck = () => {
    testEndpoint('/api/v1/pipeline/pipeline-health', 'GET');
  };

  const testImageAnalysis = () => {
    // 테스트용 더미 이미지 생성
    const canvas = document.createElement('canvas');
    canvas.width = 200;
    canvas.height = 200;
    const ctx = canvas.getContext('2d');
    
    if (ctx) {
      // 흰색 배경
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, 200, 200);
      
      // 간단한 집 그리기 (HTP 테스트용)
      ctx.strokeStyle = '#000000';
      ctx.lineWidth = 2;
      
      // 집 벽
      ctx.strokeRect(50, 100, 100, 80);
      
      // 지붕
      ctx.beginPath();
      ctx.moveTo(40, 100);
      ctx.lineTo(100, 60);
      ctx.lineTo(160, 100);
      ctx.closePath();
      ctx.stroke();
      
      // 문
      ctx.strokeRect(80, 140, 20, 40);
      
      // 창문
      ctx.strokeRect(60, 120, 15, 15);
      ctx.strokeRect(125, 120, 15, 15);
      
      // TEST 텍스트
      ctx.fillStyle = '#666';
      ctx.font = '12px Arial';
      ctx.fillText('Test House', 70, 190);
    }

    canvas.toBlob((blob) => {
      if (blob) {
        console.log('🎨 테스트 이미지 생성 완료:', blob.size, 'bytes');
        
        const formData = new FormData();
        formData.append('image', blob, 'test-house.png');
        formData.append('description', 'API 테스트용 집 그림 - HTP 심리검사 테스트');
        
        console.log('📤 FormData 생성 완료:', {
          image: blob,
          description: 'API 테스트용 집 그림 - HTP 심리검사 테스트'
        });
        
        testEndpoint('/api/v1/pipeline/analyze-image', 'POST', formData);
      } else {
        console.error('❌ 테스트 이미지 생성 실패');
      }
    }, 'image/png');
  };

  const testAnalysisStatus = () => {
    const testId = prompt('확인할 test_id를 입력하세요:', '1');
    if (testId) {
      testEndpoint(`/api/v1/pipeline/analysis-status/${testId}`, 'GET');
    }
  };

  const clearResults = () => {
    setResults({});
  };

  if (!isVisible) return null;

  const TestButton: React.FC<{
    onClick: () => void;
    loading: boolean;
    children: React.ReactNode;
    description: string;
  }> = ({ onClick, loading, children, description }) => (
    <div className="bg-gray-50 rounded-lg p-4">
      <button
        onClick={onClick}
        disabled={loading}
        className={`w-full mb-2 px-4 py-2 rounded-lg font-medium transition-colors ${
          loading
            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
            : 'bg-blue-500 hover:bg-blue-600 text-white'
        }`}
      >
        {loading ? (
          <span className="flex items-center justify-center">
            <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full mr-2"></div>
            테스트 중...
          </span>
        ) : (
          children
        )}
      </button>
      <p className="text-sm text-gray-600">{description}</p>
    </div>
  );

  const ResultCard: React.FC<{ testKey: string; result: TestResult }> = ({ testKey, result }) => (
    <div className={`p-4 rounded-lg border ${result.success ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
      <div className="flex items-center justify-between mb-2">
        <h4 className="font-medium text-gray-800">{testKey}</h4>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-500">{result.timestamp}</span>
          <span className="text-lg">{result.success ? '✅' : '❌'}</span>
        </div>
      </div>
      
      {result.success && result.data && (
        <div className="bg-white rounded p-2 mb-2">
          <pre className="text-xs text-gray-700 whitespace-pre-wrap overflow-x-auto">
            {JSON.stringify(result.data, null, 2)}
          </pre>
        </div>
      )}
      
      {result.error && (
        <div className="bg-red-100 rounded p-2">
          <p className="text-sm text-red-700 font-medium">오류:</p>
          <p className="text-sm text-red-600">{result.error}</p>
        </div>
      )}
    </div>
  );

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl p-6 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-800">🧪 파이프라인 API 테스트</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl font-bold"
          >
            ×
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* 테스트 버튼들 */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-800">API 엔드포인트 테스트</h3>
            
            <TestButton
              onClick={testHealthCheck}
              loading={loading['GET /api/v1/pipeline/pipeline-health'] || false}
              description="파이프라인 구성 요소 상태 확인"
            >
              🔧 Health Check
            </TestButton>

            <TestButton
              onClick={testImageAnalysis}
              loading={loading['POST /api/v1/pipeline/analyze-image'] || false}
              description="더미 이미지로 분석 시작 테스트"
            >
              🚀 Image Analysis
            </TestButton>

            <TestButton
              onClick={testAnalysisStatus}
              loading={loading.analysisStatus || false}
              description="특정 test_id의 분석 상태 확인"
            >
              📊 Analysis Status
            </TestButton>

            <div className="pt-4 border-t">
              <button
                onClick={clearResults}
                className="w-full bg-gray-200 hover:bg-gray-300 text-gray-700 px-4 py-2 rounded-lg font-medium transition-colors"
              >
                🗑️ 결과 지우기
              </button>
            </div>
          </div>

          {/* 테스트 결과 */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-800">테스트 결과</h3>
            
            {Object.keys(results).length === 0 ? (
              <div className="bg-gray-50 rounded-lg p-6 text-center">
                <p className="text-gray-500">아직 테스트를 실행하지 않았습니다.</p>
                <p className="text-sm text-gray-400 mt-1">위의 버튼을 클릭하여 API를 테스트해보세요.</p>
              </div>
            ) : (
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {Object.entries(results)
                  .sort(([,a], [,b]) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
                  .map(([testKey, result]) => (
                    <ResultCard key={testKey} testKey={testKey} result={result} />
                  ))}
              </div>
            )}
          </div>
        </div>

        {/* 사용법 안내 */}
        <div className="mt-6 bg-blue-50 rounded-lg p-4">
          <h4 className="font-semibold text-blue-800 mb-2">💡 사용법 안내</h4>
          <ul className="text-sm text-blue-700 space-y-1">
            <li>• <strong>Health Check</strong>: 파이프라인 구성 요소들의 상태를 확인합니다</li>
            <li>• <strong>Image Analysis</strong>: 더미 이미지로 분석 파이프라인을 테스트합니다</li>
            <li>• <strong>Analysis Status</strong>: 특정 test_id의 분석 진행 상황을 확인합니다</li>
            <li>• 결과는 JSON 형태로 표시되며, 오류 발생 시 상세 정보를 제공합니다</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default PipelineTestPanel;