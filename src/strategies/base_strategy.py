"""
Base Strategy Module - 기본 전략 모듈
"""

from abc import ABC, abstractmethod
import logging
from typing import Dict, List, Optional, Union
import pandas as pd
import numpy as np

class BaseStrategy(ABC):
    """기본 전략 클래스"""
    
    def __init__(self, name: str):
        """초기화
        
        Args:
            name (str): 전략 이름
        """
        self.name = name
        self.logger = logging.getLogger(__name__)
        
        # 포지션 관리
        self.positions: Dict[str, Dict] = {}  # {종목코드: {수량, 평균단가, ...}}
        
        # 성과 기록
        self.performance: Dict[str, float] = {
            'total_profit': 0.0,  # 총 수익
            'win_rate': 0.0,      # 승률
            'profit_factor': 0.0, # 수익률
            'max_drawdown': 0.0,  # 최대 손실폭
        }
        
        # 리스크 관리 설정
        self.risk_settings: Dict[str, float] = {
            'max_position_size': 0.1,  # 최대 포지션 크기 (계좌의 10%)
            'stop_loss': 0.02,         # 손절 기준 (2%)
            'take_profit': 0.05,       # 익절 기준 (5%)
            'max_trades': 10,          # 동시 최대 거래 수
        }
    
    @abstractmethod
    def generate_signal(self, data: pd.DataFrame) -> Dict[str, str]:
        """매매 시그널 생성 (추상 메서드)
        
        Args:
            data (pd.DataFrame): 시장 데이터
            
        Returns:
            Dict[str, str]: {종목코드: 시그널} 형태의 딕셔너리
                시그널: 'buy', 'sell', 'hold' 중 하나
        """
        pass
    
    def update_position(self, code: str, quantity: int, price: float, position_type: str):
        """포지션 업데이트
        
        Args:
            code (str): 종목코드
            quantity (int): 거래 수량
            price (float): 거래 가격
            position_type (str): 'buy' 또는 'sell'
        """
        if position_type not in ['buy', 'sell']:
            self.logger.error(f"잘못된 포지션 타입: {position_type}")
            return
            
        if code not in self.positions:
            self.positions[code] = {
                'quantity': 0,
                'avg_price': 0.0,
                'last_price': price,
                'realized_pnl': 0.0,
                'unrealized_pnl': 0.0
            }
            
        position = self.positions[code]
        
        if position_type == 'buy':
            # 매수 시 평균단가 계산
            total_cost = position['quantity'] * position['avg_price']
            new_total_cost = total_cost + (quantity * price)
            new_quantity = position['quantity'] + quantity
            position['avg_price'] = new_total_cost / new_quantity if new_quantity > 0 else 0
            position['quantity'] = new_quantity
        else:  # sell
            # 매도 시 실현손익 계산
            if position['quantity'] >= quantity:
                realized_pnl = (price - position['avg_price']) * quantity
                position['realized_pnl'] += realized_pnl
                position['quantity'] -= quantity
                if position['quantity'] == 0:
                    position['avg_price'] = 0.0
    
    def calculate_unrealized_pnl(self, code: str, current_price: float) -> float:
        """미실현 손익 계산
        
        Args:
            code (str): 종목코드
            current_price (float): 현재가
            
        Returns:
            float: 미실현 손익
        """
        if code not in self.positions:
            return 0.0
            
        position = self.positions[code]
        position['last_price'] = current_price
        position['unrealized_pnl'] = (current_price - position['avg_price']) * position['quantity']
        return position['unrealized_pnl']
    
    def check_risk_limits(self, code: str, quantity: int, price: float) -> bool:
        """리스크 한도 체크
        
        Args:
            code (str): 종목코드
            quantity (int): 거래 수량
            price (float): 거래 가격
            
        Returns:
            bool: 리스크 한도 내이면 True
        """
        # 최대 포지션 크기 체크
        position_value = quantity * price
        account_value = 100000000  # TODO: 실제 계좌 평가금액으로 대체
        if position_value / account_value > self.risk_settings['max_position_size']:
            self.logger.warning(f"최대 포지션 크기 초과: {code}")
            return False
            
        # 동시 거래 수 체크
        if len(self.positions) >= self.risk_settings['max_trades']:
            self.logger.warning("최대 거래 수 초과")
            return False
            
        return True
    
    def update_performance(self):
        """성과 지표 업데이트"""
        total_realized_pnl = sum(p['realized_pnl'] for p in self.positions.values())
        total_unrealized_pnl = sum(p['unrealized_pnl'] for p in self.positions.values())
        
        self.performance['total_profit'] = total_realized_pnl + total_unrealized_pnl
        
        # TODO: 승률, 수익률, 최대 손실폭 등 추가 지표 계산
    
    def get_position_summary(self) -> Dict[str, Dict]:
        """포지션 요약 정보
        
        Returns:
            Dict[str, Dict]: 종목별 포지션 정보
        """
        return self.positions
    
    def get_performance_summary(self) -> Dict[str, float]:
        """성과 요약 정보
        
        Returns:
            Dict[str, float]: 성과 지표
        """
        self.update_performance()
        return self.performance

# 예정된 기능:
# - 포지션 관리
#   - 포지션 크기 조절
#   - 분할 매수/매도
#   - 피라미딩
#   - 손절/익절 관리
#
# - 리스크 관리
#   - 변동성 기반 포지션 조절
#   - 상관관계 분석
#   - VaR 계산
#   - 리스크 한도 관리
#
# - 성과 분석
#   - 수익률 분석
#   - 샤프 비율
#   - 최대 손실폭
#   - 승률/손실률
#   - 수익 요인 분석
#
# - 백테스팅
#   - 과거 데이터 시뮬레이션
#   - 성과 측정
#   - 최적화
#   - 강건성 테스트 