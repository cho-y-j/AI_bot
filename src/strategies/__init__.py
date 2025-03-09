"""
Trading Strategies Module - 트레이딩 전략 관련 모듈
"""

from .base_strategy import BaseStrategy
from .bollinger_strategy import BollingerStrategy
from .ai_strategy import AIStrategy

__all__ = [
    'BaseStrategy',
    'BollingerStrategy',
    'AIStrategy'
]

# 예정된 기능:
# - 기본 전략
#   - 매수/매도 시그널 생성
#   - 포지션 관리
#   - 리스크 관리
#   - 성과 분석
#
# - 볼린저 밴드 전략
#   - 상단/하단 밴드 계산
#   - 돌파 시그널 감지
#   - 추세 추종
#   - 반전 시그널
#
# - AI 전략
#   - 가격 예측 모델
#   - 패턴 인식
#   - 시장 상황 분석
#   - 포트폴리오 최적화
#
# - 추가 예정 전략
#   - 이동평균 전략
#   - MACD 전략
#   - RSI 전략
#   - 삼중창 전략
#   - 패턴 트레이딩 전략
#   - 퀀트 전략 