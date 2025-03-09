"""
종목 검색 패널 모듈
"""
import os
import sys
import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QSplitter
)
from PyQt5.QtCore import Qt, pyqtSignal

# 로깅 설정
logger = logging.getLogger(__name__)

class StockSearchPanel(QWidget):
    """종목 검색 패널 클래스"""
    
    # 시그널 정의
    stock_selected = pyqtSignal(str, str)  # 종목코드, 종목명
    buy_requested = pyqtSignal(str)
    sell_requested = pyqtSignal(str)
    chart_requested = pyqtSignal(str)
    
    def __init__(self, parent=None, kiwoom=None):
        """
        초기화
        
        Args:
            parent: 부모 위젯
            kiwoom: 키움 API 객체
        """
        super().__init__(parent)
        self.parent = parent
        self.kiwoom = kiwoom
        self.selected_stock = None
        
        # UI 초기화
        self.init_ui()
    
    def init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout()
        
        # 검색 영역
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("종목명을 입력하세요")
        self.search_button = QPushButton("검색")
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        
        # 테이블 위젯
        self.stock_table = QTableWidget()
        self.stock_table.setColumnCount(2)
        self.stock_table.setHorizontalHeaderLabels(["종목코드", "종목명"])
        
        # 레이아웃 구성
        layout.addLayout(search_layout)
        layout.addWidget(self.stock_table)
        self.setLayout(layout)
        
        # 시그널 연결
        self.search_button.clicked.connect(self.search_stock)
        self.stock_table.itemDoubleClicked.connect(self.on_stock_selected)
        self.search_input.returnPressed.connect(self.search_stock)
    
    def search_stock(self):
        """종목 검색"""
        search_text = self.search_input.text().strip()
        if not search_text:
            return
            
        # 테스트 데이터로 검색 결과 표시
        test_stocks = {
            "삼성전자": "005930",
            "SK하이닉스": "000660",
            "NAVER": "035420",
            "카카오": "035720",
            "삼성전자우": "005935",
            "삼성SDI": "006400",
            "현대차": "005380",
            "기아": "000270",
            "셀트리온": "068270",
            "POSCO홀딩스": "005490"
        }
        
        # 검색어를 포함하는 종목 찾기
        results = []
        for name, code in test_stocks.items():
            if search_text.lower() in name.lower() or search_text in code:
                results.append((code, name))
        
        # 키움 API를 통한 종목 검색 (실제 구현 시)
        if self.kiwoom and not results:
            try:
                # 키움 API를 통한 종목 검색 (예시)
                # api_results = self.kiwoom.search_stock(search_text)
                # if api_results:
                #     for stock in api_results:
                #         results.append((stock['code'], stock['name']))
                pass
            except Exception as e:
                self.log_message(f"종목 검색 중 오류 발생: {str(e)}")
        
        # 검색 결과 표시
        self.update_stock_table(results)
        
        # 검색 결과가 하나인 경우 자동 선택
        if len(results) == 1:
            code, name = results[0]
            self.stock_selected.emit(code, name)
            self.log_message(f"종목 선택: {name}({code})")
    
    def update_stock_table(self, stock_data):
        """테이블에 종목 데이터 업데이트"""
        self.stock_table.setRowCount(len(stock_data))
        for row, (code, name) in enumerate(stock_data):
            self.stock_table.setItem(row, 0, QTableWidgetItem(code))
            self.stock_table.setItem(row, 1, QTableWidgetItem(name))
    
    def on_stock_selected(self, item):
        """항목 선택 이벤트"""
        row = item.row()
        code = self.stock_table.item(row, 0).text()
        name = self.stock_table.item(row, 1).text()
        self.stock_selected.emit(code, name)
    
    def update_hoga_info(self, stock_code):
        """호가 정보 업데이트"""
        try:
            # 실제로는 키움 API를 통해 호가 정보를 가져와야 함
            # 현재는 임시 데이터로 대체
            self.log_message(f"{stock_code} 호가 정보 업데이트")
            
            # 임시 데이터로 호가창 업데이트
            base_price = 30000
            
            # 매도호가 (1~5)
            for i in range(5):
                price = base_price + (5-i) * 100
                quantity = (5-i) * 10 + (i*3)
                
                sell_item = QTableWidgetItem(f"{quantity:,}")
                price_item = QTableWidgetItem(f"{price:,}")
                
                self.hoga_table.setItem(i, 0, sell_item)
                self.hoga_table.setItem(i, 1, price_item)
                
                if i > 0:
                    sell_item.setBackground(Qt.blue)
                    sell_item.setForeground(Qt.white)
                    price_item.setBackground(Qt.blue)
                    price_item.setForeground(Qt.white)
            
            # 매수호가 (1~5)
            for i in range(5):
                price = base_price - (i+1) * 100
                quantity = (i+1) * 10 + (i*5)
                
                price_item = QTableWidgetItem(f"{price:,}")
                buy_item = QTableWidgetItem(f"{quantity:,}")
                
                self.hoga_table.setItem(i+5, 1, price_item)
                self.hoga_table.setItem(i+5, 2, buy_item)
                
                if i > 0:
                    price_item.setBackground(Qt.red)
                    price_item.setForeground(Qt.white)
                    buy_item.setBackground(Qt.red)
                    buy_item.setForeground(Qt.white)
            
        except Exception as e:
            self.log_message(f"호가 정보 업데이트 중 오류 발생: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def on_buy_button_clicked(self):
        """매수 버튼 클릭 이벤트"""
        selected_rows = self.stock_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "경고", "매수할 종목을 선택하세요.")
            return
        
        row = selected_rows[0].row()
        stock_name = self.stock_table.item(row, 1).text()
        stock_code = self.find_stock_code_by_name(stock_name)
        if stock_code:
            self.buy_requested.emit(stock_code)
    
    def on_sell_button_clicked(self):
        """매도 버튼 클릭 이벤트"""
        selected_rows = self.stock_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "경고", "매도할 종목을 선택하세요.")
            return
        
        row = selected_rows[0].row()
        stock_name = self.stock_table.item(row, 1).text()
        stock_code = self.find_stock_code_by_name(stock_name)
        if stock_code:
            self.sell_requested.emit(stock_code)
    
    def on_chart_button_clicked(self):
        """차트 버튼 클릭 이벤트"""
        selected_rows = self.stock_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "경고", "차트를 볼 종목을 선택하세요.")
            return
        
        row = selected_rows[0].row()
        stock_name = self.stock_table.item(row, 1).text()
        stock_code = self.find_stock_code_by_name(stock_name)
        if stock_code:
            self.chart_requested.emit(stock_code)
    
    def find_stock_code_by_name(self, stock_name):
        """종목명으로 종목코드 찾기"""
        # 테스트 데이터
        test_stocks = {
            "삼성전자": "005930",
            "SK하이닉스": "000660",
            "NAVER": "035420",
            "카카오": "035720",
            "삼성전자우": "005935",
            "삼성SDI": "006400",
            "현대차": "005380",
            "기아": "000270",
            "셀트리온": "068270",
            "POSCO홀딩스": "005490"
        }
        
        if stock_name in test_stocks:
            return test_stocks[stock_name]
        
        # 키움 API 사용
        if self.kiwoom:
            code = self.kiwoom.get_stock_code_by_name(stock_name)
            if code:
                return code
        
        self.log_message(f"종목코드를 찾을 수 없습니다: {stock_name}")
        return None
    
    def log_message(self, message):
        """로그 메시지 출력"""
        # 부모의 로그 함수 호출 (있는 경우)
        if hasattr(self.parent, 'log_text'):
            self.parent.log_text.append(message)
        logger.info(message) 