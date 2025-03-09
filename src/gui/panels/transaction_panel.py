"""
거래내역 패널 모듈
"""
import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QDateEdit
)
from PyQt5.QtCore import Qt, pyqtSignal, QDate

# 로깅 설정
logger = logging.getLogger(__name__)

class TransactionPanel(QWidget):
    """거래내역 패널 클래스"""
    
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
        
        # 거래내역 조회 컨트롤
        transaction_top_layout = QHBoxLayout()
        
        # 조회 기간 선택
        transaction_top_layout.addWidget(QLabel("조회기간:"))
        
        # 시작일
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate().addDays(-7))
        transaction_top_layout.addWidget(self.start_date_edit)
        
        transaction_top_layout.addWidget(QLabel("~"))
        
        # 종료일
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())
        transaction_top_layout.addWidget(self.end_date_edit)
        
        # 조회 버튼
        self.query_button = QPushButton("조회")
        transaction_top_layout.addWidget(self.query_button)
        
        transaction_top_layout.addStretch()
        layout.addLayout(transaction_top_layout)
        
        # 거래내역 테이블
        self.transaction_table = QTableWidget()
        self.transaction_table.setColumnCount(7)
        self.transaction_table.setHorizontalHeaderLabels(["일자", "종목명", "매수/매도", "수량", "단가", "수수료", "세금"])
        self.transaction_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.transaction_table.verticalHeader().setVisible(False)
        layout.addWidget(self.transaction_table)
        
        self.setLayout(layout)
        
        # 이벤트 연결
        self.query_button.clicked.connect(self.on_query_clicked)
    
    def on_query_clicked(self):
        """조회 버튼 클릭 이벤트"""
        start_date = self.start_date_edit.date().toString("yyyyMMdd")
        end_date = self.end_date_edit.date().toString("yyyyMMdd")
        self.update_transactions(start_date, end_date)
    
    def update_transactions(self, start_date, end_date):
        """
        거래내역 업데이트
        
        Args:
            start_date: 시작일 (YYYYMMDD)
            end_date: 종료일 (YYYYMMDD)
        """
        try:
            # 테이블 초기화
            self.transaction_table.setRowCount(0)
            
            # 실제 API 호출로 거래내역 정보 가져오기
            if self.kiwoom:
                transactions = self.kiwoom.get_transaction_history(start_date, end_date)
                if transactions:
                    self.update_transaction_table(transactions)
                    return
            
            # 테스트용 더미 데이터
            self.add_dummy_transactions()
            self.log_message(f"거래내역 업데이트 완료 (테스트 데이터) - {start_date}~{end_date}")
            
        except Exception as e:
            self.log_message(f"거래내역 업데이트 중 오류 발생: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def add_dummy_transactions(self):
        """테스트용 더미 데이터 추가"""
        dummy_transactions = [
            {"일자": "20230601", "종목명": "삼성전자", "매수/매도": "매수", "수량": 10, "단가": 70000, "수수료": 350, "세금": 0},
            {"일자": "20230605", "종목명": "SK하이닉스", "매수/매도": "매수", "수량": 5, "단가": 120000, "수수료": 300, "세금": 0},
            {"일자": "20230610", "종목명": "삼성전자", "매수/매도": "매도", "수량": 5, "단가": 72000, "수수료": 180, "세금": 108},
            {"일자": "20230615", "종목명": "NAVER", "매수/매도": "매수", "수량": 2, "단가": 330000, "수수료": 330, "세금": 0},
            {"일자": "20230620", "종목명": "카카오", "매수/매도": "매수", "수량": 5, "단가": 75000, "수수료": 187, "세금": 0},
            {"일자": "20230625", "종목명": "SK하이닉스", "매수/매도": "매도", "수량": 3, "단가": 125000, "수수료": 187, "세금": 112},
        ]
        
        for transaction in dummy_transactions:
            row = self.transaction_table.rowCount()
            self.transaction_table.insertRow(row)
            
            # 일자
            date_str = transaction['일자']
            formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
            self.transaction_table.setItem(row, 0, QTableWidgetItem(formatted_date))
            
            # 종목명
            self.transaction_table.setItem(row, 1, QTableWidgetItem(transaction['종목명']))
            
            # 매수/매도
            trade_type = transaction['매수/매도']
            trade_item = QTableWidgetItem(trade_type)
            if trade_type == "매수":
                trade_item.setForeground(Qt.red)
            else:
                trade_item.setForeground(Qt.blue)
            self.transaction_table.setItem(row, 2, trade_item)
            
            # 수량
            quantity = transaction['수량']
            quantity_item = QTableWidgetItem(f"{quantity:,}")
            quantity_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.transaction_table.setItem(row, 3, quantity_item)
            
            # 단가
            price = transaction['단가']
            price_item = QTableWidgetItem(f"{price:,}")
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.transaction_table.setItem(row, 4, price_item)
            
            # 수수료
            fee = transaction['수수료']
            fee_item = QTableWidgetItem(f"{fee:,}")
            fee_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.transaction_table.setItem(row, 5, fee_item)
            
            # 세금
            tax = transaction['세금']
            tax_item = QTableWidgetItem(f"{tax:,}")
            tax_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.transaction_table.setItem(row, 6, tax_item)
    
    def update_transaction_table(self, transactions):
        """실제 거래내역 데이터로 테이블 업데이트"""
        # TODO: API 응답 형식에 맞게 구현
        pass
    
    def log_message(self, message):
        """로그 메시지 출력"""
        # 부모의 로그 함수 호출 (있는 경우)
        if hasattr(self.parent, 'log_text'):
            self.parent.log_text.append(message)
        logger.info(message) 