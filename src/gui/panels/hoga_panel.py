"""
호가창 패널 모듈
"""
import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt, pyqtSignal

# 로깅 설정
logger = logging.getLogger(__name__)

class HogaPanel(QWidget):
    """호가창 패널 클래스"""
    
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
        
        # UI 초기화
        self.init_ui()
    
    def init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout()
        
        # 호가창 레이블
        layout.addWidget(QLabel("호가창"))
        
        # 호가 테이블
        self.hoga_table = QTableWidget()
        self.hoga_table.setColumnCount(3)
        self.hoga_table.setRowCount(10)
        self.hoga_table.setHorizontalHeaderLabels(["매도호가", "가격", "매수호가"])
        self.hoga_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.hoga_table.verticalHeader().setVisible(False)
        layout.addWidget(self.hoga_table)
        
        self.setLayout(layout)
    
    def update_hoga_info(self, stock_code, base_price=None):
        """
        호가 정보 업데이트
        
        Args:
            stock_code: 종목코드
            base_price: 기준가격 (없으면 API에서 조회)
        """
        try:
            # 실제 API 호출로 호가 정보 가져오기
            if self.kiwoom and not base_price:
                hoga_data = self.kiwoom.get_hoga_data(stock_code)
                if hoga_data:
                    # TODO: API 응답 형식에 맞게 처리
                    pass
            
            # 임시 데이터 사용 (테스트용)
            if not base_price:
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
            
            self.log_message(f"{stock_code} 호가 정보가 업데이트되었습니다.")
            
        except Exception as e:
            self.log_message(f"호가 정보 업데이트 중 오류 발생: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def log_message(self, message):
        """로그 메시지 출력"""
        # 부모의 로그 함수 호출 (있는 경우)
        if hasattr(self.parent, 'log_text'):
            self.parent.log_text.append(message)
        logger.info(message) 