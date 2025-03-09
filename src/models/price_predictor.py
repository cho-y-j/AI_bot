"""
주가 예측 AI 모델
"""
import os
import numpy as np
import pandas as pd
import logging
import joblib
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# 로거 설정
logger = logging.getLogger(__name__)

class PricePredictor:
    """
    주가 예측 AI 모델 클래스
    """
    def __init__(self, model_type='random_forest'):
        """
        초기화 함수
        
        Args:
            model_type (str): 모델 타입 ('random_forest' 또는 'linear')
        """
        self.model_type = model_type
        self.model = None
        self.scaler = MinMaxScaler()
        self.is_trained = False
        self.model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                      'data', 'models')
        
        # 모델 저장 디렉토리 생성
        os.makedirs(self.model_path, exist_ok=True)
        
        logger.info(f"PricePredictor 초기화 완료 (모델 타입: {model_type})")
    
    def _create_features(self, df):
        """
        특성 생성 함수
        
        Args:
            df (DataFrame): 원본 데이터프레임
            
        Returns:
            DataFrame: 특성이 추가된 데이터프레임
        """
        df = df.copy()
        
        # 기술적 지표 추가
        # 이동평균선
        df['ma5'] = df['close'].rolling(window=5).mean()
        df['ma10'] = df['close'].rolling(window=10).mean()
        df['ma20'] = df['close'].rolling(window=20).mean()
        
        # 볼린저 밴드
        df['ma20_std'] = df['close'].rolling(window=20).std()
        df['upper_band'] = df['ma20'] + (df['ma20_std'] * 2)
        df['lower_band'] = df['ma20'] - (df['ma20_std'] * 2)
        
        # MACD
        df['ema12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['ema26'] = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = df['ema12'] - df['ema26']
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # 가격 변화율
        df['price_change'] = df['close'].pct_change()
        df['price_change_1d'] = df['close'].pct_change(periods=1)
        df['price_change_5d'] = df['close'].pct_change(periods=5)
        
        # 거래량 변화율
        df['volume_change'] = df['volume'].pct_change()
        
        # 결측치 제거
        df = df.dropna()
        
        return df
    
    def _prepare_data(self, df, target_column='close', prediction_days=5):
        """
        데이터 준비 함수
        
        Args:
            df (DataFrame): 원본 데이터프레임
            target_column (str): 예측 대상 컬럼
            prediction_days (int): 예측 기간 (일)
            
        Returns:
            tuple: (X, y) 학습 데이터
        """
        # 특성 생성
        df = self._create_features(df)
        
        # 타겟 변수 생성 (n일 후 종가)
        df[f'target_{prediction_days}d'] = df[target_column].shift(-prediction_days)
        
        # 결측치 제거
        df = df.dropna()
        
        # 특성과 타겟 분리
        features = ['open', 'high', 'low', 'close', 'volume', 
                   'ma5', 'ma10', 'ma20', 'upper_band', 'lower_band',
                   'macd', 'macd_signal', 'rsi', 
                   'price_change', 'price_change_1d', 'price_change_5d',
                   'volume_change']
        
        X = df[features]
        y = df[f'target_{prediction_days}d']
        
        # 스케일링
        X_scaled = self.scaler.fit_transform(X)
        
        return X_scaled, y
    
    def train(self, df, target_column='close', prediction_days=5, test_size=0.2):
        """
        모델 학습 함수
        
        Args:
            df (DataFrame): 학습 데이터
            target_column (str): 예측 대상 컬럼
            prediction_days (int): 예측 기간 (일)
            test_size (float): 테스트 데이터 비율
            
        Returns:
            dict: 학습 결과 (metrics)
        """
        try:
            logger.info(f"모델 학습 시작 (데이터 크기: {len(df)})")
            
            # 데이터 준비
            X, y = self._prepare_data(df, target_column, prediction_days)
            
            # 학습/테스트 데이터 분할
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
            
            # 모델 선택
            if self.model_type == 'random_forest':
                self.model = RandomForestRegressor(n_estimators=100, random_state=42)
            else:
                self.model = LinearRegression()
            
            # 모델 학습
            self.model.fit(X_train, y_train)
            
            # 예측 및 평가
            y_pred = self.model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            r2 = r2_score(y_test, y_pred)
            
            self.is_trained = True
            
            logger.info(f"모델 학습 완료 (RMSE: {rmse:.4f}, R2: {r2:.4f})")
            
            return {
                'rmse': rmse,
                'r2': r2,
                'model_type': self.model_type,
                'data_size': len(df),
                'features': X.shape[1],
                'prediction_days': prediction_days
            }
            
        except Exception as e:
            logger.exception(f"모델 학습 중 오류 발생: {e}")
            return None
    
    def predict(self, df, prediction_days=5):
        """
        주가 예측 함수
        
        Args:
            df (DataFrame): 예측에 사용할 데이터
            prediction_days (int): 예측 기간 (일)
            
        Returns:
            float: 예측 가격
        """
        if not self.is_trained or self.model is None:
            logger.error("모델이 학습되지 않았습니다.")
            return None
        
        try:
            # 특성 생성
            df = self._create_features(df)
            
            # 결측치 제거
            df = df.dropna()
            
            if len(df) == 0:
                logger.error("유효한 데이터가 없습니다.")
                return None
            
            # 특성 선택
            features = ['open', 'high', 'low', 'close', 'volume', 
                       'ma5', 'ma10', 'ma20', 'upper_band', 'lower_band',
                       'macd', 'macd_signal', 'rsi', 
                       'price_change', 'price_change_1d', 'price_change_5d',
                       'volume_change']
            
            X = df[features].iloc[-1:].values
            
            # 스케일링
            X_scaled = self.scaler.transform(X)
            
            # 예측
            predicted_price = self.model.predict(X_scaled)[0]
            
            logger.info(f"{prediction_days}일 후 예측 가격: {predicted_price:.2f}")
            
            return predicted_price
            
        except Exception as e:
            logger.exception(f"예측 중 오류 발생: {e}")
            return None
    
    def save_model(self, code):
        """
        모델 저장 함수
        
        Args:
            code (str): 종목 코드
            
        Returns:
            bool: 저장 성공 여부
        """
        if not self.is_trained or self.model is None:
            logger.error("저장할 모델이 없습니다.")
            return False
        
        try:
            # 파일명 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{code}_{self.model_type}_{timestamp}.joblib"
            filepath = os.path.join(self.model_path, filename)
            
            # 모델 저장
            joblib.dump({
                'model': self.model,
                'scaler': self.scaler,
                'model_type': self.model_type,
                'timestamp': timestamp,
                'code': code
            }, filepath)
            
            logger.info(f"모델 저장 완료: {filepath}")
            return True
            
        except Exception as e:
            logger.exception(f"모델 저장 중 오류 발생: {e}")
            return False
    
    def load_model(self, filepath):
        """
        모델 로드 함수
        
        Args:
            filepath (str): 모델 파일 경로
            
        Returns:
            bool: 로드 성공 여부
        """
        try:
            if not os.path.exists(filepath):
                logger.error(f"모델 파일이 존재하지 않습니다: {filepath}")
                return False
            
            # 모델 로드
            model_data = joblib.load(filepath)
            
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.model_type = model_data['model_type']
            self.is_trained = True
            
            logger.info(f"모델 로드 완료: {filepath}")
            return True
            
        except Exception as e:
            logger.exception(f"모델 로드 중 오류 발생: {e}")
            return False
    
    def get_latest_model(self, code):
        """
        최신 모델 가져오기
        
        Args:
            code (str): 종목 코드
            
        Returns:
            str: 모델 파일 경로
        """
        try:
            # 모델 디렉토리 확인
            if not os.path.exists(self.model_path):
                logger.error(f"모델 디렉토리가 존재하지 않습니다: {self.model_path}")
                return None
            
            # 해당 종목 코드의 모델 파일 찾기
            model_files = [f for f in os.listdir(self.model_path) if f.startswith(f"{code}_")]
            
            if not model_files:
                logger.warning(f"종목 코드 {code}에 대한 모델 파일이 없습니다.")
                return None
            
            # 최신 파일 찾기 (파일명에 타임스탬프가 포함되어 있음)
            latest_model = sorted(model_files)[-1]
            
            return os.path.join(self.model_path, latest_model)
            
        except Exception as e:
            logger.exception(f"최신 모델 검색 중 오류 발생: {e}")
            return None 