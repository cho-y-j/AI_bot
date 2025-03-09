"""
GUI 패널 모듈 패키지
""" 
'''
#from .stock_search_panel import StockSearchPanel
from .hoga_panel import HogaPanel
from .holdings_panel import HoldingsPanel
# from .favorites_panel import FavoritesPanel  # 아직 개발 중
from .transaction_panel import TransactionPanel
from .log_panel import LogPanel

from .chart_panel import ChartPanel  # 아직 개발 중

# 필요한 패널만 노출
__all__ = [
    'StockSearchPanel',
    'HogaPanel',
    'HoldingsPanel',
    # 'FavoritesPanel',  # 아직 개발 중
    'TransactionPanel',
    'LogPanel',
    # 'ChartPanel'  # 아직 개발 중
] 
'''