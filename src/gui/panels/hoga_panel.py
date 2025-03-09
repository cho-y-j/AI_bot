"""
호가창 패널 모듈
"""
import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView,
    QTabWidget, QGridLayout, QPushButton, QFrame,
    QRadioButton, QButtonGroup
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont

# 로깅 설정
logger = logging.getLogger(__name__)

class HogaPanel(QWidget):
    """호가창 패널 클래스"""
    
    # 시그널 정의
    chart_requested = pyqtSignal(str)  # 차트 요청 시그널
    
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
        self.stock_code = None
        self.stock_name = None
        
        # UI 초기화
        self.init_ui()
        
        # 실시간 데이터 요청 상태
        self.real_time_subscribed = False
    
    def init_ui(self):
        """UI 초기화"""
        main_layout = QVBoxLayout()
        
        # 종목 정보 영역
        self.init_stock_info_area()
        main_layout.addWidget(self.stock_info_frame)
        
        # 호가 선택 라디오 버튼
        hoga_radio_layout = QHBoxLayout()
        self.hoga_radio_group = QButtonGroup(self)
        
        radio_5hoga = QRadioButton("5호가")
        radio_10hoga = QRadioButton("10호가")
        radio_5hoga.setChecked(True)
        
        self.hoga_radio_group.addButton(radio_5hoga, 5)
        self.hoga_radio_group.addButton(radio_10hoga, 10)
        
        hoga_radio_layout.addWidget(radio_5hoga)
        hoga_radio_layout.addWidget(radio_10hoga)
        hoga_radio_layout.addStretch()
        
        main_layout.addLayout(hoga_radio_layout)
        
        # 호가 테이블
        self.init_hoga_table()
        main_layout.addWidget(self.hoga_table)
        
        # 탭 위젯 생성
        tab_widget = QTabWidget()
        
        # 일별 데이터 탭
        daily_tab = QWidget()
        self.init_daily_tab(daily_tab)
        tab_widget.addTab(daily_tab, "일별 데이터")
        
        # 투자자 데이터 탭
        investor_tab = QWidget()
        self.init_investor_tab(investor_tab)
        tab_widget.addTab(investor_tab, "투자자 데이터")
        
        main_layout.addWidget(tab_widget)
        
        # 버튼 영역
        button_layout = QHBoxLayout()
        
        chart_btn = QPushButton("차트")
        chart_btn.clicked.connect(self.request_chart)
        button_layout.addWidget(chart_btn)
        
        refresh_btn = QPushButton("새로고침")
        refresh_btn.clicked.connect(self.refresh_data)
        button_layout.addWidget(refresh_btn)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def init_stock_info_area(self):
        """종목 정보 영역 초기화"""
        self.stock_info_frame = QFrame()
        self.stock_info_frame.setFrameStyle(QFrame.Box | QFrame.Sunken)
        
        layout = QGridLayout()
        
        # 종목명 라벨
        self.stock_name_label = QLabel()
        font = QFont()
        font.setBold(True)
        font.setPointSize(12)
        self.stock_name_label.setFont(font)
        layout.addWidget(self.stock_name_label, 0, 0, 1, 2)
        
        # 현재가 라벨
        self.current_price_label = QLabel()
        self.current_price_label.setFont(font)
        layout.addWidget(self.current_price_label, 0, 2, 1, 2)
        
        # 등락률 라벨
        self.change_rate_label = QLabel()
        layout.addWidget(self.change_rate_label, 1, 0)
        
        # 거래량 라벨
        self.volume_label = QLabel()
        layout.addWidget(self.volume_label, 1, 1)
        
        # 거래대금 라벨
        self.trading_value_label = QLabel()
        layout.addWidget(self.trading_value_label, 1, 2)
        
        self.stock_info_frame.setLayout(layout)
    
    def init_hoga_table(self):
        """호가 테이블 초기화"""
        self.hoga_table = QTableWidget()
        self.hoga_table.setColumnCount(3)
        self.hoga_table.setRowCount(20)  # 10호가 기준
        self.hoga_table.setHorizontalHeaderLabels(["매도잔량", "가격", "매수잔량"])
        
        # 열 너비 설정
        header = self.hoga_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        
        # 수직 헤더 숨기기
        self.hoga_table.verticalHeader().setVisible(False)
        
        # 편집 불가능하게 설정
        self.hoga_table.setEditTriggers(QTableWidget.NoEditTriggers)
    
    def init_daily_tab(self, tab):
        """일별 데이터 탭 초기화"""
        layout = QVBoxLayout()
        
        # 일별 데이터 테이블
        self.daily_table = QTableWidget()
        self.daily_table.setColumnCount(5)
        self.daily_table.setRowCount(20)  # 20일치 데이터
        self.daily_table.setHorizontalHeaderLabels(["일자", "종가", "대비", "등락률", "거래량"])
        
        # 열 너비 설정
        header = self.daily_table.horizontalHeader()
        for i in range(5):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        
        # 수직 헤더 숨기기
        self.daily_table.verticalHeader().setVisible(False)
        
        # 편집 불가능하게 설정
        self.daily_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(self.daily_table)
        tab.setLayout(layout)
    
    def init_investor_tab(self, tab):
        """투자자 데이터 탭 초기화"""
        layout = QVBoxLayout()
        
        # 투자자 데이터 테이블
        self.investor_table = QTableWidget()
        self.investor_table.setColumnCount(6)
        self.investor_table.setRowCount(5)  # 5일치 데이터
        self.investor_table.setHorizontalHeaderLabels(["일자", "외국인", "기관", "연기금", "프로그램", "금융투자"])
        
        # 열 너비 설정
        header = self.investor_table.horizontalHeader()
        for i in range(6):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        
        # 수직 헤더 숨기기
        self.investor_table.verticalHeader().setVisible(False)
        
        # 편집 불가능하게 설정
        self.investor_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(self.investor_table)
        tab.setLayout(layout)
    
    def set_stock(self, code, name=None):
        """종목 설정"""
        try:
            self.stock_code = code
            self.stock_name = name or self.kiwoom.get_master_code_name(code)
            
            # 종목 정보 업데이트
            self.stock_name_label.setText(f"{self.stock_name} ({code})")
            
            # 데이터 갱신
            self.refresh_data()
            
            # 실시간 데이터 등록
            self.register_real_time()
            
        except Exception as e:
            self.log_message(f"종목 설정 중 오류 발생: {str(e)}")
    
    def update_hoga_info(self, stock_code, base_price=None):
        """호가 정보 업데이트"""
        try:
            if self.kiwoom and stock_code:
                # 실제 API 호출로 호가 정보 가져오기
                hoga_data = self.kiwoom.get_hoga_data(stock_code)
                if hoga_data:
                    self.update_hoga_table(hoga_data)
                else:
                    # 임시 데이터 사용 (테스트용)
                    if not base_price:
                        base_price = 30000
                    
                    # 매도호가 (1~10)
                    for i in range(10):
                        price = base_price + (10-i) * 100
                        quantity = (10-i) * 10 + (i*3)
                        
                        sell_item = QTableWidgetItem(f"{quantity:,}")
                        price_item = QTableWidgetItem(f"{price:,}")
                        
                        self.hoga_table.setItem(i, 0, sell_item)
                        self.hoga_table.setItem(i, 1, price_item)
                        
                        sell_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                        price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                        
                        if i > 0:
                            sell_item.setBackground(QColor(220, 240, 255))
                            price_item.setBackground(QColor(220, 240, 255))
                    
                    # 매수호가 (1~10)
                    for i in range(10):
                        price = base_price - (i+1) * 100
                        quantity = (i+1) * 10 + (i*5)
                        
                        price_item = QTableWidgetItem(f"{price:,}")
                        buy_item = QTableWidgetItem(f"{quantity:,}")
                        
                        self.hoga_table.setItem(i+10, 1, price_item)
                        self.hoga_table.setItem(i+10, 2, buy_item)
                        
                        price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                        buy_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                        
                        if i > 0:
                            price_item.setBackground(QColor(255, 230, 230))
                            buy_item.setBackground(QColor(255, 230, 230))
        
        except Exception as e:
            self.log_message(f"호가 정보 업데이트 중 오류 발생: {str(e)}")
    
    def update_daily_data(self):
        """일별 데이터 업데이트"""
        try:
            if self.kiwoom and self.stock_code:
                # 일별 데이터 요청 및 테이블 업데이트
                daily_data = self.kiwoom.get_daily_data(self.stock_code)
                if daily_data:
                    self.update_daily_table(daily_data)
        except Exception as e:
            self.log_message(f"일별 데이터 업데이트 중 오류 발생: {str(e)}")
    
    def update_investor_data(self):
        """투자자 데이터 업데이트"""
        try:
            if self.kiwoom and self.stock_code:
                # 투자자 데이터 요청 및 테이블 업데이트
                investor_data = self.kiwoom.get_investor_data(self.stock_code)
                if investor_data:
                    self.update_investor_table(investor_data)
        except Exception as e:
            self.log_message(f"투자자 데이터 업데이트 중 오류 발생: {str(e)}")
    
    def refresh_data(self):
        """데이터 새로고침"""
        if self.stock_code:
            self.update_hoga_info(self.stock_code)
            self.update_daily_data()
            self.update_investor_data()
    
    def register_real_time(self):
        """실시간 데이터 등록"""
        try:
            if self.kiwoom and self.stock_code and not self.real_time_subscribed:
                self.kiwoom.set_real_time_data(self.stock_code)
                self.real_time_subscribed = True
        except Exception as e:
            self.log_message(f"실시간 데이터 등록 중 오류 발생: {str(e)}")
    
    def unregister_real_time(self):
        """실시간 데이터 해제"""
        try:
            if self.kiwoom and self.stock_code and self.real_time_subscribed:
                self.kiwoom.disset_real_time_data(self.stock_code)
                self.real_time_subscribed = False
        except Exception as e:
            self.log_message(f"실시간 데이터 해제 중 오류 발생: {str(e)}")
    
    def request_chart(self):
        """차트 요청"""
        if self.stock_code:
            self.chart_requested.emit(self.stock_code)
    
    def closeEvent(self, event):
        """패널 종료 시 처리"""
        self.unregister_real_time()
        super().closeEvent(event)
    
    def log_message(self, message):
        """로그 메시지 출력"""
        if hasattr(self.parent, 'log_text'):
            self.parent.log_text.append(message)
        logger.info(message) 