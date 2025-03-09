"""
Stock Table Widget Module - 종목 테이블 위젯 모듈
"""

import logging
from PyQt5.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView,
    QMenu, QAction
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QBrush

class StockTable(QTableWidget):
    """종목 테이블 위젯 클래스"""
    
    # 시그널 정의
    stock_selected = pyqtSignal(str)  # 종목 선택 시그널
    
    def __init__(self, parent=None):
        """초기화"""
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        
        self._init_ui()
        self._create_context_menu()
        
    def _init_ui(self):
        """UI 초기화"""
        # 컬럼 설정
        columns = ['종목코드', '종목명', '현재가', '전일대비', '등락률', '거래량', '거래대금']
        self.setColumnCount(len(columns))
        self.setHorizontalHeaderLabels(columns)
        
        # 컬럼 크기 조정
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 종목코드
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # 종목명
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # 현재가
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # 전일대비
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # 등락률
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # 거래량
        header.setSectionResizeMode(6, QHeaderView.Stretch)          # 거래대금
        
        # 테이블 설정
        self.setEditTriggers(QTableWidget.NoEditTriggers)  # 편집 비활성화
        self.setSelectionBehavior(QTableWidget.SelectRows)  # 행 단위 선택
        self.setSelectionMode(QTableWidget.SingleSelection)  # 단일 선택
        self.setAlternatingRowColors(True)  # 행 색상 교차
        
        # 정렬 활성화
        self.setSortingEnabled(True)
        
        # 선택 변경 시그널 연결
        self.itemSelectionChanged.connect(self._on_selection_changed)
        
    def _create_context_menu(self):
        """컨텍스트 메뉴 생성"""
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        
        self.context_menu = QMenu(self)
        
        # 차트 보기 액션
        chart_action = QAction('차트 보기', self)
        chart_action.triggered.connect(self._on_show_chart)
        self.context_menu.addAction(chart_action)
        
        # 현재가 보기 액션
        price_action = QAction('현재가 보기', self)
        price_action.triggered.connect(self._on_show_price)
        self.context_menu.addAction(price_action)
        
        self.context_menu.addSeparator()
        
        # 매수 주문 액션
        buy_action = QAction('매수 주문', self)
        buy_action.triggered.connect(self._on_buy_order)
        self.context_menu.addAction(buy_action)
        
        # 매도 주문 액션
        sell_action = QAction('매도 주문', self)
        sell_action.triggered.connect(self._on_sell_order)
        self.context_menu.addAction(sell_action)
        
    def _show_context_menu(self, pos):
        """컨텍스트 메뉴 표시"""
        self.context_menu.exec_(self.mapToGlobal(pos))
        
    def _on_selection_changed(self):
        """선택 변경 처리"""
        selected_items = self.selectedItems()
        if selected_items:
            code = selected_items[0].text()  # 종목코드
            self.stock_selected.emit(code)
            self.logger.debug(f'종목 선택: {code}')
            
    def _on_show_chart(self):
        """차트 보기 처리 (예정)"""
        pass
        
    def _on_show_price(self):
        """현재가 보기 처리 (예정)"""
        pass
        
    def _on_buy_order(self):
        """매수 주문 처리 (예정)"""
        pass
        
    def _on_sell_order(self):
        """매도 주문 처리 (예정)"""
        pass
        
    def add_stock(self, code, name, price, change, change_ratio, volume, amount):
        """종목 추가"""
        row = self.rowCount()
        self.insertRow(row)
        
        # 종목 정보 설정
        self.setItem(row, 0, QTableWidgetItem(code))
        self.setItem(row, 1, QTableWidgetItem(name))
        self.setItem(row, 2, QTableWidgetItem(f"{price:,}"))
        self.setItem(row, 3, QTableWidgetItem(f"{change:+,}"))
        self.setItem(row, 4, QTableWidgetItem(f"{change_ratio:+.2f}%"))
        self.setItem(row, 5, QTableWidgetItem(f"{volume:,}"))
        self.setItem(row, 6, QTableWidgetItem(f"{amount:,}"))
        
        # 등락에 따른 색상 설정
        color = QColor(255, 0, 0) if change > 0 else QColor(0, 0, 255)
        for col in [2, 3, 4]:  # 현재가, 전일대비, 등락률
            self.item(row, col).setForeground(QBrush(color))
            
    def update_stock(self, code, price, change, change_ratio, volume, amount):
        """종목 정보 업데이트"""
        items = self.findItems(code, Qt.MatchExactly)
        if not items:
            return
            
        row = items[0].row()
        
        # 가격 정보 업데이트
        self.item(row, 2).setText(f"{price:,}")
        self.item(row, 3).setText(f"{change:+,}")
        self.item(row, 4).setText(f"{change_ratio:+.2f}%")
        self.item(row, 5).setText(f"{volume:,}")
        self.item(row, 6).setText(f"{amount:,}")
        
        # 등락에 따른 색상 설정
        color = QColor(255, 0, 0) if change > 0 else QColor(0, 0, 255)
        for col in [2, 3, 4]:  # 현재가, 전일대비, 등락률
            self.item(row, col).setForeground(QBrush(color))
            
# 예정된 기능:
# - 정렬 기능
#   - 각 컬럼별 오름차순/내림차순 정렬
#   - 사용자 정의 정렬 기준
#
# - 필터링 기능
#   - 조건식 기반 필터링
#   - 실시간 필터링
#
# - 컨텍스트 메뉴 기능
#   - 차트 보기
#   - 현재가 보기
#   - 주문 기능
#   - 관심종목 등록/해제
#
# - 실시간 업데이트
#   - 가격 정보 갱신
#   - 거래량 갱신
#   - 등락률 갱신
#   - 색상 변경
#
# - 데이터 저장/불러오기
#   - 관심종목 목록 저장
#   - CSV 파일 내보내기/가져오기 