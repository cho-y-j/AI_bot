"""
볼린저 밴드 트레이딩 전략
"""
import logging
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Union

from src.strategies.base_strategy import BaseStrategy

# 로거 설정
logger = logging.getLogger(__name__)

class BollingerStrategy(BaseStrategy):
    """
    볼린저 밴드 트레이딩 전략 클래스
    """
    def __init__(self, name: str = "볼린저밴드"):
        """
        초기화 함수
        
        Args:
            name (str, optional): 전략 이름. Defaults to "볼린저밴드".
        """
        super().__init__(name)
        
        # 전략 파라미터
        self.params = {
            'period': 20,       # 기간
            'std_dev': 2.0,     # 표준편차
            'position_size': 1.0,  # 포지션 크기 (1.0 = 100%)
            'entry_threshold': 0.02,  # 진입 임계값 (2%)
            'exit_threshold': 0.01,   # 청산 임계값 (1%)
        }
        
        # 볼린저 밴드 데이터
        self.bands: Dict[str, pd.DataFrame] = {}  # {종목코드: DataFrame}
        
        logger.info(f"볼린저 밴드 전략 초기화 완료 (period={self.params['period']}, std_dev={self.params['std_dev']})")
    
    def calculate_bands(self, data: pd.DataFrame) -> pd.DataFrame:
        """볼린저 밴드 계산
        
        Args:
            data (pd.DataFrame): OHLCV 데이터
            
        Returns:
            pd.DataFrame: 볼린저 밴드가 추가된 데이터프레임
        """
        df = data.copy()
        
        # 중심선 (이동평균)
        df['middle_band'] = df['close'].rolling(window=self.params['period']).mean()
        
        # 표준편차
        df['std'] = df['close'].rolling(window=self.params['period']).std()
        
        # 상단/하단 밴드
        df['upper_band'] = df['middle_band'] + (df['std'] * self.params['std_dev'])
        df['lower_band'] = df['middle_band'] - (df['std'] * self.params['std_dev'])
        
        # 밴드폭
        df['bandwidth'] = (df['upper_band'] - df['lower_band']) / df['middle_band']
        
        # %B ((현재가 - 하단밴드) / (상단밴드 - 하단밴드))
        df['percent_b'] = (df['close'] - df['lower_band']) / (df['upper_band'] - df['lower_band'])
        
        return df
    
    def generate_signal(self, data: pd.DataFrame) -> Dict[str, str]:
        """매매 시그널 생성
        
        Args:
            data (pd.DataFrame): OHLCV 데이터
            
        Returns:
            Dict[str, str]: {종목코드: 시그널} 형태의 딕셔너리
                시그널: 'buy', 'sell', 'hold' 중 하나
        """
        signals = {}
        
        for code in data.index.get_level_values(0).unique():
            # 해당 종목의 데이터 추출
            stock_data = data.loc[code]
            
            # 볼린저 밴드 계산
            if code not in self.bands:
                self.bands[code] = self.calculate_bands(stock_data)
            band_data = self.bands[code]
            
            # 현재 데이터
            current = band_data.iloc[-1]
            prev = band_data.iloc[-2]
            
            # 현재 포지션 확인
            position = self.positions.get(code, {'quantity': 0})
            
            # 매매 신호 생성
            signal = 'hold'
            
            if position['quantity'] == 0:  # 미보유 상태
                # 매수 신호: %B가 진입 임계값보다 낮고, 상승 반전
                if (current['percent_b'] < self.params['entry_threshold'] and
                    current['close'] > prev['close']):
                    signal = 'buy'
            else:  # 보유 상태
                # 매도 신호: %B가 (1 - 청산 임계값)보다 높고, 하락 반전
                if (current['percent_b'] > (1 - self.params['exit_threshold']) and
                    current['close'] < prev['close']):
                    signal = 'sell'
                
                # 손절 신호: 하단 밴드 하향 돌파
                elif current['close'] < current['lower_band']:
                    signal = 'sell'
            
            signals[code] = signal
            
            # 로깅
            self.logger.debug(f"볼린저 밴드 신호 생성: {code} - {signal}")
            self.logger.debug(f"현재 %B: {current['percent_b']:.2f}")
            self.logger.debug(f"밴드폭: {current['bandwidth']:.2f}")
        
        return signals
    
    def update_params(self, params: Dict[str, Union[int, float]]):
        """전략 파라미터 업데이트
        
        Args:
            params (Dict[str, Union[int, float]]): 업데이트할 파라미터
        """
        self.params.update(params)
        
        # 파라미터 변경 시 밴드 데이터 초기화
        self.bands = {}
        
        self.logger.info(f"전략 파라미터 업데이트: {params}")
    
    def get_band_data(self, code: str) -> Optional[pd.DataFrame]:
        """볼린저 밴드 데이터 조회
        
        Args:
            code (str): 종목코드
            
        Returns:
            Optional[pd.DataFrame]: 볼린저 밴드 데이터
        """
        return self.bands.get(code)

# 예정된 기능:
# - 추가 시그널
#   - 밴드폭 확장/수축 감지
#   - 이중 밴드 전략
#   - 추세 추종 모드
#   - 반전 모드
#
# - 최적화
#   - 파라미터 최적화
#   - 변동성 기반 파라미터 조정
#   - 수익률 기반 파라미터 조정
#
# - 리스크 관리
#   - 동적 손절/익절
#   - 변동성 기반 포지션 조절
#   - 상관관계 기반 포지션 조절
#
# - 성과 분석
#   - 전략 성과 분석
#   - 승률/손실률 분석
#   - 수익 요인 분석
#   - 강건성 테스트 