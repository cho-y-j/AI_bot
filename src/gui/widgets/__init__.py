"""
GUI Widgets Module - GUI 위젯 관련 모듈
"""

from .chart_widget import ChartWidget
from .stock_table import StockTable
from .order_widget import OrderWidget

__all__ = [
    'ChartWidget',
    'StockTable',
    'OrderWidget'
]

# 예정된 기능:
# - 차트 위젯
#   - 캔들차트 표시
#   - 기술적 지표 표시
#   - 차트 도구 (추세선, 피보나치 등)
#   - 차트 기간 설정
#   - 실시간 업데이트
#
# - 종목 테이블 위젯
#   - 종목 정보 표시
#   - 실시간 가격 업데이트
#   - 정렬 및 필터링
#   - 컨텍스트 메뉴
#
# - 주문 위젯
#   - 주문 유형 선택
#   - 수량/가격 입력
#   - 주문 실행
#   - 주문 취소/정정 