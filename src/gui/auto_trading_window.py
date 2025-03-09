import sys
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QSpinBox, 
    QDoubleSpinBox, QGroupBox, QFormLayout, QTabWidget, QMessageBox,
    QHeaderView, QSizePolicy, QFrame, QApplication, QCheckBox
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QColor

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import mplfinance as mpf

from src.gui.main_window import AccountPasswordDialog
from src.gui.chart_view import ChartView, MplCanvas

class AutoTradingWindow(QMainWindow):
    """자동주문 창 클래스"""
    
    def __init__(self, trading_bot, parent=None):
        super(AutoTradingWindow, self).__init__(parent)
        self.trading_bot = trading_bot
        self.kiwoom_api = trading_bot.kiwoom
        self.parent = parent  # MainWindow 참조 저장
        
        self.setWindowTitle("자동주문 시스템")
        self.setGeometry(100, 100, 1200, 800)
        
        self.chart_data = None
        self.current_code = ""
        self.current_name = ""
        
        self.init_ui()
        
    def init_ui(self):
        """UI 초기화"""
        # 중앙 위젯 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃
        main_layout = QVBoxLayout(central_widget)
        
        # 상단 그룹 (계좌 정보, 종목 검색)
        top_group = self.create_top_group()
        main_layout.addWidget(top_group)
        
        # 탭 위젯 생성
        tab_widget = QTabWidget()
        
        # 전략 설정 탭
        strategy_tab = self.create_strategy_tab()
        tab_widget.addTab(strategy_tab, "전략 설정")
        
        # 차트 탭
        chart_tab = self.create_chart_tab()
        tab_widget.addTab(chart_tab, "차트")
        
        # 거래 기록 탭
        history_tab = self.create_history_tab()
        tab_widget.addTab(history_tab, "거래 기록")
        
        main_layout.addWidget(tab_widget)
        
        # 하단 버튼 영역
        bottom_layout = QHBoxLayout()
        
        # 자동매매 시작 버튼
        self.start_button = QPushButton("자동매매 시작")
        self.start_button.setStyleSheet("background-color: #4CAF50; color: white;")
        self.start_button.clicked.connect(self.start_auto_trading)
        bottom_layout.addWidget(self.start_button)
        
        # 자동매매 중지 버튼
        self.stop_button = QPushButton("자동매매 중지")
        self.stop_button.setStyleSheet("background-color: #f44336; color: white;")
        self.stop_button.clicked.connect(self.stop_auto_trading)
        self.stop_button.setEnabled(False)
        bottom_layout.addWidget(self.stop_button)
        
        main_layout.addLayout(bottom_layout)
    
    def create_top_group(self):
        """상단 그룹 생성"""
        group = QGroupBox('계좌 정보')
        layout = QVBoxLayout()
        
        # 계좌 선택 및 정보 표시
        account_layout = QHBoxLayout()
        
        # 계좌 선택
        account_label = QLabel("계좌:")
        self.account_combo = QComboBox()
        account_layout.addWidget(account_label)
        account_layout.addWidget(self.account_combo)
        
        # 계좌 정보 조회 버튼
        refresh_btn = QPushButton("조회")
        refresh_btn.clicked.connect(self.refresh_account_info)
        account_layout.addWidget(refresh_btn)
        
        account_layout.addStretch(1)
        layout.addLayout(account_layout)
        
        # 계좌 정보 표시
        info_layout = QHBoxLayout()
        
        # 계좌 잔고
        self.account_balance_label = QLabel("계좌 잔고: 조회 필요")
        info_layout.addWidget(self.account_balance_label)
        
        # 주문 가능 금액
        self.available_amount_label = QLabel("주문 가능금액: 조회 필요")
        info_layout.addWidget(self.available_amount_label)
        
        info_layout.addStretch(1)
        layout.addLayout(info_layout)
        
        # 종목 검색 영역
        search_layout = QHBoxLayout()
        
        # 종목 코드 입력
        code_label = QLabel("종목코드:")
        self.stock_code_edit = QLineEdit()
        self.stock_code_edit.setPlaceholderText("종목코드 입력")
        self.stock_code_edit.setFixedWidth(100)
        search_layout.addWidget(code_label)
        search_layout.addWidget(self.stock_code_edit)
        
        # 종목명 입력
        name_label = QLabel("종목명:")
        self.stock_name_edit = QLineEdit()
        self.stock_name_edit.setPlaceholderText("종목명 입력")
        search_layout.addWidget(name_label)
        search_layout.addWidget(self.stock_name_edit)
        
        # 검색 버튼
        search_btn = QPushButton("검색")
        search_btn.clicked.connect(self.search_stock)
        search_layout.addWidget(search_btn)
        
        search_layout.addStretch(1)
        layout.addLayout(search_layout)
        
        # 종목 정보 표시
        stock_info_layout = QHBoxLayout()
        
        self.stock_code_label = QLabel("종목 코드: ")
        stock_info_layout.addWidget(self.stock_code_label)
        
        self.stock_name_label = QLabel("종목명: ")
        stock_info_layout.addWidget(self.stock_name_label)
        
        self.current_price_label = QLabel("현재가: ")
        stock_info_layout.addWidget(self.current_price_label)
        
        stock_info_layout.addStretch(1)
        layout.addLayout(stock_info_layout)
        
        group.setLayout(layout)
        return group
    
    def create_strategy_tab(self):
        """전략 설정 탭 생성"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 전략 선택 그룹
        strategy_group = QGroupBox("전략 선택")
        strategy_layout = QFormLayout()
        
        # 전략 선택 콤보박스
        self.strategy_combo = QComboBox()
        self.strategy_combo.addItem("볼린저 밴드 전략")
        self.strategy_combo.addItem("이동평균 전략")
        self.strategy_combo.addItem("RSI 전략")
        self.strategy_combo.addItem("MACD 전략")
        self.strategy_combo.addItem("AI 자동매매 전략")
        self.strategy_combo.currentIndexChanged.connect(self.on_strategy_changed)
        strategy_layout.addRow("전략:", self.strategy_combo)
        
        strategy_group.setLayout(strategy_layout)
        layout.addWidget(strategy_group)
        
        # 상단 정보 표시 영역
        info_layout = QHBoxLayout()
        
        # 종목 정보
        stock_group = QGroupBox("종목 정보")
        stock_form = QFormLayout(stock_group)
        
        self.stock_code_label = QLabel("종목 코드: -")
        stock_form.addRow(self.stock_code_label)
        
        self.stock_name_label = QLabel("종목명: -")
        stock_form.addRow(self.stock_name_label)
        
        self.current_price_label = QLabel("현재가: -")
        stock_form.addRow(self.current_price_label)
        
        self.trading_status_label = QLabel("상태: 대기중")
        stock_form.addRow(self.trading_status_label)
        
        info_layout.addWidget(stock_group)
        
        # 계좌 정보
        account_group = QGroupBox("계좌 정보")
        account_form = QFormLayout(account_group)
        
        self.account_combo = QComboBox()
        account_form.addRow("계좌 선택:", self.account_combo)
        
        self.account_balance_label = QLabel("계좌 잔고: -")
        account_form.addRow(self.account_balance_label)
        
        self.available_amount_label = QLabel("주문 가능 금액: -")
        account_form.addRow(self.available_amount_label)
        
        info_layout.addWidget(account_group)
        
        layout.addLayout(info_layout)
        
        # 전략 설정 영역
        strategy_group = QGroupBox("볼린저 밴드 설정")
        strategy_layout = QFormLayout(strategy_group)
        
        # 볼린저 밴드 N값
        self.bollinger_n_spin = QSpinBox()
        self.bollinger_n_spin.setRange(5, 100)
        self.bollinger_n_spin.setValue(20)
        strategy_layout.addRow("이동평균선 기간(N):", self.bollinger_n_spin)
        
        # 볼린저 밴드 K값
        self.bollinger_k_spin = QDoubleSpinBox()
        self.bollinger_k_spin.setRange(0.1, 5.0)
        self.bollinger_k_spin.setSingleStep(0.1)
        self.bollinger_k_spin.setValue(2.0)
        strategy_layout.addRow("표준편차 배수(K):", self.bollinger_k_spin)
        
        # 익절 비율
        self.profit_ratio_spin = QDoubleSpinBox()
        self.profit_ratio_spin.setRange(0.1, 10.0)
        self.profit_ratio_spin.setSingleStep(0.1)
        self.profit_ratio_spin.setValue(2.0)
        self.profit_ratio_spin.setSuffix("%")
        strategy_layout.addRow("익절 비율:", self.profit_ratio_spin)
        
        # 손절 비율
        self.loss_ratio_spin = QDoubleSpinBox()
        self.loss_ratio_spin.setRange(0.1, 10.0)
        self.loss_ratio_spin.setSingleStep(0.1)
        self.loss_ratio_spin.setValue(1.0)
        self.loss_ratio_spin.setSuffix("%")
        strategy_layout.addRow("손절 비율:", self.loss_ratio_spin)
        
        # 매수 금액
        self.investment_amount_edit = QLineEdit()
        self.investment_amount_edit.setPlaceholderText("투자 금액 입력")
        strategy_layout.addRow("투자 금액:", self.investment_amount_edit)
        
        # 전략 테스트 버튼
        test_btn = QPushButton("전략 테스트")
        test_btn.clicked.connect(self.test_strategy)
        strategy_layout.addWidget(test_btn)
        
        layout.addWidget(strategy_group)
        
        return tab
    
    def create_chart_tab(self):
        """차트 탭 생성"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 차트 뷰 생성
        self.chart_view = ChartView(self.kiwoom_api, tab)
        layout.addWidget(self.chart_view)
        
        return tab
    
    def create_history_tab(self):
        """거래 기록 탭 생성"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 거래 기록 테이블
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(7)
        self.history_table.setHorizontalHeaderLabels(["시간", "종목코드", "종목명", "거래유형", "가격", "수량", "금액"])
        
        # 테이블 스타일 설정
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(self.history_table)
        
        return tab
    
    def on_chart_type_changed(self, index):
        """차트 타입 변경 시 호출되는 메서드"""
        # 분봉 선택 시에만 시간 간격 활성화
        if index == 0:  # 분봉
            self.time_interval_combo.setEnabled(True)
        else:
            self.time_interval_combo.setEnabled(False)
    
    def search_stock(self):
        """종목 검색"""
        try:
            code = self.stock_code_edit.text().strip()
            name = self.stock_name_edit.text().strip()
            
            if not code and not name:
                QMessageBox.warning(self, "입력 오류", "종목 코드 또는 종목명을 입력하세요.")
                return
            
            if name and not code:
                # 종목명으로 코드 찾기
                code = self.find_stock_code_by_name(name)
                if not code:
                    QMessageBox.warning(self, "검색 오류", f"'{name}' 종목을 찾을 수 없습니다.")
                    return
                self.stock_code_edit.setText(code)
            
            # 종목 정보 표시
            stock_name = self.kiwoom_api.get_master_code_name(code)
            self.stock_name_edit.setText(stock_name)
            
            # 라벨 업데이트
            self.stock_code_label.setText(f"종목 코드: {code}")
            self.stock_name_label.setText(f"종목명: {stock_name}")
            
            # 차트 뷰에 종목 설정
            self.chart_view.set_stock(code, stock_name)
            
            # 현재가 조회 (계좌 비밀번호 없이 가능)
            self.update_current_price(code)
            
        except Exception as e:
            QMessageBox.warning(self, "오류", f"종목 검색 중 오류 발생: {str(e)}")
    
    def find_stock_code_by_name(self, stock_name):
        """종목명으로 종목코드 찾기"""
        try:
            # 코스피 종목 검색
            kospi_codes = self.kiwoom_api.get_code_list_by_market("0")
            for code in kospi_codes:
                name = self.kiwoom_api.get_master_code_name(code)
                if stock_name in name:
                    return code
            
            # 코스닥 종목 검색
            kosdaq_codes = self.kiwoom_api.get_code_list_by_market("10")
            for code in kosdaq_codes:
                name = self.kiwoom_api.get_master_code_name(code)
                if stock_name in name:
                    return code
                    
            return None
        except Exception as e:
            print(f"종목 코드 검색 중 오류: {e}")
            return None
    
    def update_current_price(self, code):
        """현재가 업데이트"""
        try:
            stock_info = self.kiwoom_api.get_stock_basic_info(code)
            if stock_info and "현재가" in stock_info:
                price = abs(int(stock_info["현재가"]))
                self.current_price_label.setText(f"현재가: {price:,}원")
        except Exception as e:
            print(f"현재가 업데이트 중 오류: {e}")
    
    def fetch_chart_data(self):
        """차트 데이터 조회"""
        try:
            code = self.stock_code_edit.text().strip()
            if not code:
                QMessageBox.warning(self, "입력 오류", "종목 코드를 입력하세요.")
                return
            
            chart_type = self.chart_type_combo.currentText()
            period = self.period_spin.value()
            
            # 차트 데이터 요청
            if chart_type == "분봉":
                time_interval = self.time_interval_combo.currentText()[0]  # "1분" -> "1"
                self.chart_data = self.fetch_minute_chart(code, time_interval, period)
            elif chart_type == "일봉":
                self.chart_data = self.fetch_daily_chart(code, period)
            elif chart_type == "주봉":
                self.chart_data = self.fetch_weekly_chart(code, period)
            elif chart_type == "월봉":
                self.chart_data = self.fetch_monthly_chart(code, period)
            
            # 차트 그리기
            if self.chart_data is not None:
                self.draw_chart()
                QMessageBox.information(self, "데이터 조회 완료", "차트 데이터 조회가 완료되었습니다.")
            
        except Exception as e:
            QMessageBox.warning(self, "오류", f"차트 데이터 조회 중 오류 발생: {str(e)}")
    
    def fetch_minute_chart(self, code, time_interval, period):
        """분봉 차트 데이터 조회"""
        try:
            # API 호출로 분봉 데이터 조회 시도
            # 클래스에 send_minutes_chart_data 메서드가 있는 경우
            if hasattr(self.kiwoom_api, 'send_minutes_chart_data'):
                return self.kiwoom_api.send_minutes_chart_data(code, time_interval)
            
            # 메서드가 없는 경우 예시 데이터 생성
            print(f"분봉 차트 API 메서드가 없어 예시 데이터를 생성합니다.")
            
            # 예시 데이터 생성
            import datetime
            import random
            
            today = datetime.datetime.now()
            data = []
            
            # 현재 가격을 임의로 설정 (실제로는 API에서 가져와야 함)
            current_price = 50000
            
            # period일치 데이터 생성
            for i in range(period * 390 // int(time_interval)):  # 하루 390분 (6시간 30분) 기준
                date = today - datetime.timedelta(minutes=i * int(time_interval))
                
                # 가격 변동 시뮬레이션
                change = random.uniform(-0.005, 0.005)
                current_price = current_price * (1 + change)
                
                # OHLC 생성
                open_price = current_price * (1 + random.uniform(-0.003, 0.003))
                high_price = max(current_price, open_price) * (1 + random.uniform(0, 0.005))
                low_price = min(current_price, open_price) * (1 - random.uniform(0, 0.005))
                close_price = current_price
                
                # 거래량 생성
                volume = int(random.uniform(1000, 10000))
                
                data.append([
                    date.strftime('%Y%m%d%H%M%S'),
                    open_price,
                    high_price,
                    low_price,
                    close_price,
                    volume
                ])
            
            return data
            
        except Exception as e:
            print(f"분봉 데이터 조회 중 오류: {e}")
            return None
    
    def fetch_daily_chart(self, code, days):
        """일봉 차트 데이터 조회"""
        try:
            # 키움 API의 일봉 데이터 조회 메서드 호출
            if hasattr(self.kiwoom_api, 'get_day_chart_data'):
                return self.kiwoom_api.get_day_chart_data(code, days)
            
            # 메서드가 없는 경우 예시 데이터 생성
            print(f"일봉 차트 API 메서드가 없어 예시 데이터를 생성합니다.")
            
            import datetime
            import random
            
            today = datetime.datetime.now()
            data = []
            
            # 현재 가격을 임의로 설정
            current_price = 50000
            
            # days일치 데이터 생성
            for i in range(days):
                date = today - datetime.timedelta(days=i)
                
                # 가격 변동 시뮬레이션
                change = random.uniform(-0.02, 0.02)
                current_price = current_price * (1 + change)
                
                # OHLC 생성
                open_price = current_price * (1 + random.uniform(-0.01, 0.01))
                high_price = max(current_price, open_price) * (1 + random.uniform(0, 0.02))
                low_price = min(current_price, open_price) * (1 - random.uniform(0, 0.02))
                close_price = current_price
                
                # 거래량 생성
                volume = int(random.uniform(10000, 100000))
                
                data.append([
                    date.strftime('%Y%m%d'),
                    open_price,
                    high_price,
                    low_price,
                    close_price,
                    volume
                ])
            
            return data
            
        except Exception as e:
            print(f"일봉 데이터 조회 중 오류: {e}")
            return None
    
    def fetch_weekly_chart(self, code, weeks):
        """주봉 차트 데이터 조회"""
        try:
            # 키움 API의 주봉 데이터 조회 메서드 호출 (있는 경우)
            if hasattr(self.kiwoom_api, 'send_week_chart_data'):
                return self.kiwoom_api.send_week_chart_data(code, weeks)
            
            # 메서드가 없는 경우 예시 데이터 생성
            print(f"주봉 차트 API 메서드가 없어 예시 데이터를 생성합니다.")
            
            import datetime
            import random
            
            today = datetime.datetime.now()
            # 이번 주 월요일로 설정
            today = today - datetime.timedelta(days=today.weekday())
            data = []
            
            # 현재 가격을 임의로 설정
            current_price = 50000
            
            # weeks주치 데이터 생성
            for i in range(weeks):
                date = today - datetime.timedelta(weeks=i)
                
                # 가격 변동 시뮬레이션
                change = random.uniform(-0.03, 0.03)
                current_price = current_price * (1 + change)
                
                # OHLC 생성
                open_price = current_price * (1 + random.uniform(-0.02, 0.02))
                high_price = max(current_price, open_price) * (1 + random.uniform(0, 0.03))
                low_price = min(current_price, open_price) * (1 - random.uniform(0, 0.03))
                close_price = current_price
                
                # 거래량 생성
                volume = int(random.uniform(50000, 500000))
                
                data.append([
                    date.strftime('%Y%m%d'),
                    open_price,
                    high_price,
                    low_price,
                    close_price,
                    volume
                ])
            
            return data
            
        except Exception as e:
            print(f"주봉 데이터 조회 중 오류: {e}")
            return None
    
    def fetch_monthly_chart(self, code, months):
        """월봉 차트 데이터 조회"""
        try:
            # 키움 API의 월봉 데이터 조회 메서드 호출 (있는 경우)
            # 아직 API에 구현되지 않았다면 예시 데이터 생성
            print(f"월봉 차트 API 메서드가 없어 예시 데이터를 생성합니다.")
            
            import datetime
            import random
            
            today = datetime.datetime.now()
            # 이번 달 1일로 설정
            today = today.replace(day=1)
            data = []
            
            # 현재 가격을 임의로 설정
            current_price = 50000
            
            # months개월치 데이터 생성
            for i in range(months):
                # i개월 전 날짜 계산
                year = today.year
                month = today.month - i
                
                # 월이 음수가 되면 연도 조정
                while month <= 0:
                    year -= 1
                    month += 12
                
                date = datetime.datetime(year, month, 1)
                
                # 가격 변동 시뮬레이션
                change = random.uniform(-0.05, 0.05)
                current_price = current_price * (1 + change)
                
                # OHLC 생성
                open_price = current_price * (1 + random.uniform(-0.03, 0.03))
                high_price = max(current_price, open_price) * (1 + random.uniform(0, 0.05))
                low_price = min(current_price, open_price) * (1 - random.uniform(0, 0.05))
                close_price = current_price
                
                # 거래량 생성
                volume = int(random.uniform(200000, 2000000))
                
                data.append([
                    date.strftime('%Y%m%d'),
                    open_price,
                    high_price,
                    low_price,
                    close_price,
                    volume
                ])
            
            return data
            
        except Exception as e:
            print(f"월봉 데이터 조회 중 오류: {e}")
            return None
    
    def draw_chart(self):
        """차트 그리기"""
        if self.chart_data is None:
            return
        
        try:
            # 데이터프레임 생성
            columns = ['날짜', '시가', '고가', '저가', '종가', '거래량']
            df = pd.DataFrame(self.chart_data, columns=columns)
            
            # 날짜 데이터 변환
            df['날짜'] = pd.to_datetime(df['날짜'])
            
            # 날짜를 인덱스로 설정
            df.set_index('날짜', inplace=True)
            
            # 역순 정렬 (최근 데이터가 앞에 오도록)
            df = df.sort_index()
            
            # 볼린저 밴드 계산
            n = self.bollinger_n_spin.value()
            k = self.bollinger_k_spin.value()
            
            df['MA'] = df['종가'].rolling(window=n).mean()
            df['STD'] = df['종가'].rolling(window=n).std()
            df['Upper'] = df['MA'] + (df['STD'] * k)
            df['Lower'] = df['MA'] - (df['STD'] * k)
            
            # 차트 초기화
            self.chart_view.axes.clear()
            
            # 서브플롯 생성 (가격 차트와 거래량 차트 분리)
            if self.show_volume_check.isChecked():
                # 2개의 서브플롯 구성
                grid_spec = self.chart_view.figure.add_gridspec(2, 1, height_ratios=[3, 1])
                price_ax = self.chart_view.figure.add_subplot(grid_spec[0])
                volume_ax = self.chart_view.figure.add_subplot(grid_spec[1], sharex=price_ax)
                
                # 거래량 차트 그리기
                volume_ax.bar(df.index, df['거래량'], color='gray', alpha=0.5)
                volume_ax.set_ylabel('거래량')
                volume_ax.grid(True, alpha=0.3)
                
                # x축 레이블 표시 설정
                price_ax.get_xaxis().set_visible(False)
                
                # 현재 축을 price_ax로 설정
                self.chart_view.axes = price_ax
            
            # 캔들스틱 차트 그리기 (일봉/주봉/월봉인 경우)
            chart_type = self.chart_type_combo.currentText()
            if chart_type in ["일봉", "주봉", "월봉"]:
                # 종가 선 그래프로 표시
                self.chart_view.axes.plot(df.index, df['종가'], label='종가')
                
                # 시가, 고가, 저가, 종가 표시 (봉차트 스타일)
                for idx in range(len(df)):
                    date = df.index[idx]
                    open_price = df['시가'].iloc[idx]
                    close_price = df['종가'].iloc[idx]
                    high_price = df['고가'].iloc[idx]
                    low_price = df['저가'].iloc[idx]
                    
                    # 음봉/양봉 색상 설정
                    color = 'red' if close_price >= open_price else 'blue'
                    
                    # 봉 그리기 (시가~종가)
                    self.chart_view.axes.plot(
                        [date, date], 
                        [open_price, close_price], 
                        color=color, 
                        linewidth=3
                    )
                    
                    # 꼬리 그리기 (고가~저가)
                    self.chart_view.axes.plot(
                        [date, date], 
                        [low_price, high_price], 
                        color=color, 
                        linewidth=1
                    )
            else:
                # 분봉 등 기타 차트는 종가 선 그래프로 표시
                self.chart_view.axes.plot(df.index, df['종가'], label='종가')
            
            # 이동평균선 추가
            if self.show_ma_check.isChecked():
                self.chart_view.axes.plot(df.index, df['MA'], 'r--', label=f'MA({n})')
            
            # 볼린저 밴드 추가
            if self.show_bollinger_check.isChecked():
                self.chart_view.axes.plot(df.index, df['Upper'], 'g--', label=f'상단 밴드 ({k}σ)')
                self.chart_view.axes.plot(df.index, df['Lower'], 'g--', label=f'하단 밴드 ({k}σ)')
                
                # 밴드 사이 영역 색상 표시
                self.chart_view.axes.fill_between(
                    df.index, df['Upper'], df['Lower'], 
                    color='gray', alpha=0.2
                )
            
            # 차트 스타일 설정
            self.chart_view.axes.set_title(f'{self.stock_name_edit.text()} ({self.stock_code_edit.text()}) 차트')
            self.chart_view.axes.set_ylabel('가격')
            self.chart_view.axes.legend()
            self.chart_view.axes.grid(True, alpha=0.3)
            
            # x축 레이블 회전
            for label in self.chart_view.axes.get_xticklabels():
                label.set_rotation(45)
            
            # 차트 레이아웃 조정
            self.chart_view.figure.tight_layout()
            
            # 차트 업데이트
            self.chart_view.draw()
            
        except Exception as e:
            print(f"차트 그리기 중 오류: {e}")
            import traceback
            traceback.print_exc()
    
    def refresh_chart(self):
        """차트 새로고침"""
        if self.chart_data is not None:
            self.draw_chart()
    
    def test_strategy(self):
        """전략 테스트"""
        try:
            if self.chart_data is None:
                QMessageBox.warning(self, "데이터 없음", "먼저 차트 데이터를 조회하세요.")
                return
            
            n = self.bollinger_n_spin.value()
            k = self.bollinger_k_spin.value()
            profit_ratio = self.profit_ratio_spin.value() / 100 + 1  # 2.0% -> 1.02
            loss_ratio = 1 - self.loss_ratio_spin.value() / 100  # 1.0% -> 0.99
            
            # 전략 테스트 수행 (실제 구현은 백테스팅 모듈과 연동)
            QMessageBox.information(
                self, 
                "전략 테스트", 
                f"볼린저 밴드 전략 테스트\n"
                f"- MA 기간: {n}\n"
                f"- 표준편차 배수: {k}\n"
                f"- 익절 비율: {self.profit_ratio_spin.value()}%\n"
                f"- 손절 비율: {self.loss_ratio_spin.value()}%\n"
                f"\n전략 테스트 기능은 아직 개발 중입니다."
            )
            
        except Exception as e:
            QMessageBox.warning(self, "오류", f"전략 테스트 중 오류 발생: {str(e)}")
    
    def start_auto_trading(self):
        """자동매매 시작"""
        if not self.current_code:
            QMessageBox.warning(self, "경고", "종목을 먼저 선택해주세요.")
            return
        
        # 계좌 비밀번호 확인
        if not self.check_account_password():
            return
        
        # 전략 설정 가져오기
        strategy_name = self.strategy_combo.currentText()
        
        # 전략 객체 생성
        strategy = None
        
        if strategy_name == "볼린저 밴드 전략":
            from src.strategies.bollinger_strategy import BollingerStrategy
            
            # 파라미터 설정
            params = {
                'n': self.bollinger_n_spin.value(),
                'k': self.bollinger_k_spin.value(),
                'profit_ratio': self.profit_ratio_spin.value(),
                'loss_ratio': self.loss_ratio_spin.value()
            }
            
            strategy = BollingerStrategy(params)
            
        elif strategy_name == "AI 자동매매 전략":
            from src.strategies.ai_strategy import AIStrategy
            
            # 파라미터 설정
            params = {
                'model_type': 'random_forest' if self.model_type_combo.currentText() == "Random Forest" else 'linear',
                'prediction_days': self.prediction_days_spin.value(),
                'profit_ratio': self.profit_ratio_spin.value(),
                'loss_ratio': self.loss_ratio_spin.value(),
                'confidence_threshold': self.confidence_threshold_spin.value()
            }
            
            strategy = AIStrategy(params)
            
            # 모델 로드 시도
            if not strategy.load_model(self.current_code):
                # 모델이 없으면 학습 시도
                if QMessageBox.question(self, "모델 없음", 
                                      "해당 종목에 대한 AI 모델이 없습니다. 지금 학습하시겠습니까?",
                                      QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                    self.train_ai_model()
                    # 다시 로드 시도
                    if not strategy.load_model(self.current_code):
                        QMessageBox.warning(self, "경고", "모델 로드에 실패했습니다. 자동매매를 시작할 수 없습니다.")
                        return
                else:
                    QMessageBox.warning(self, "경고", "AI 모델 없이 자동매매를 시작할 수 없습니다.")
                    return
        
        # 다른 전략들에 대한 처리...
        elif strategy_name == "이동평균 전략":
            # 이동평균 전략 구현
            QMessageBox.information(self, "알림", "이동평균 전략은 아직 구현되지 않았습니다.")
            return
        elif strategy_name == "RSI 전략":
            # RSI 전략 구현
            QMessageBox.information(self, "알림", "RSI 전략은 아직 구현되지 않았습니다.")
            return
        elif strategy_name == "MACD 전략":
            # MACD 전략 구현
            QMessageBox.information(self, "알림", "MACD 전략은 아직 구현되지 않았습니다.")
            return
        
        if strategy is None:
            QMessageBox.warning(self, "경고", "전략을 선택해주세요.")
            return
        
        try:
            code = self.stock_code_edit.text().strip()
            if not code:
                QMessageBox.warning(self, "입력 오류", "종목 코드를 입력하세요.")
                return
            
            if not self.account_combo.currentText():
                QMessageBox.warning(self, "입력 오류", "계좌를 선택하세요.")
                return
            
            investment_amount = self.investment_amount_edit.text().strip()
            if not investment_amount:
                QMessageBox.warning(self, "입력 오류", "투자 금액을 입력하세요.")
                return
            
            try:
                investment_amount = int(investment_amount.replace(',', ''))
            except ValueError:
                QMessageBox.warning(self, "입력 오류", "유효한 투자 금액을 입력하세요.")
                return
            
            # 자동매매 설정
            strategy_settings = {
                "item_code": code,
                "account": self.account_combo.currentText(),
                "chart_type": self.chart_type_combo.currentText(),
                "time_type": "minute" if self.chart_type_combo.currentText() == "분봉" else "day",
                "profit_ratio": self.profit_ratio_spin.value() / 100 + 1,
                "loss_ratio": 1 - self.loss_ratio_spin.value() / 100,
                "bollinger_n": self.bollinger_n_spin.value(),
                "bollinger_k": self.bollinger_k_spin.value(),
                "balance": investment_amount
            }
            
            # 자동매매 시작 요청 (실제 구현은 API와 연동)
            QMessageBox.information(
                self, 
                "자동매매 시작", 
                f"자동매매를 시작합니다.\n"
                f"- 종목: {self.stock_name_label.text()[5:]}\n"
                f"- 계좌: {strategy_settings['account']}\n"
                f"- 투자 금액: {investment_amount:,}원"
            )
            
            # 버튼 상태 변경
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.trading_status_label.setText("상태: 자동매매 진행중")
            
        except Exception as e:
            QMessageBox.warning(self, "오류", f"자동매매 시작 중 오류 발생: {str(e)}")
    
    def stop_auto_trading(self):
        """자동매매 중지"""
        try:
            # 자동매매 중지 요청 (실제 구현은 API와 연동)
            QMessageBox.information(self, "자동매매 중지", "자동매매를 중지합니다.")
            
            # 버튼 상태 변경
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.trading_status_label.setText("상태: 대기중")
            
        except Exception as e:
            QMessageBox.warning(self, "오류", f"자동매매 중지 중 오류 발생: {str(e)}")
    
    def refresh_account_info(self):
        """계좌 정보 갱신"""
        try:
            account_no = self.account_combo.currentText()
            if not account_no:
                QMessageBox.warning(self, "오류", "계좌를 선택하세요.")
                return
            
            # 부모 윈도우(MainWindow)의 get_account_password 메서드 사용
            account_password = None
            if hasattr(self.parent, 'get_account_password'):
                account_password = self.parent.get_account_password()
            else:
                # 부모 윈도우에 get_account_password 메서드가 없는 경우 대화상자 직접 표시
                password_dialog = AccountPasswordDialog(self)
                if password_dialog.exec_() != QDialog.Accepted:
                    return
                account_password = password_dialog.get_password()
            
            if not account_password:
                return
            
            if not account_password or len(account_password) != 4:
                QMessageBox.warning(self, "오류", "유효한 계좌 비밀번호(4자리)를 입력하세요.")
                return
            
            # 주문 가능금액 조회
            deposit_info = self.kiwoom_api.get_deposit_info(account_no, account_password)
            if deposit_info and '주문가능금액' in deposit_info:
                self.available_amount_label.setText(
                    f"주문 가능금액: {int(deposit_info['주문가능금액']):,}원"
                )
            
            # 계좌 평가 정보 조회
            account_eval = self.kiwoom_api.get_account_evaluation(account_no, account_password)
            if account_eval and '총평가금액' in account_eval:
                self.account_balance_label.setText(
                    f"계좌 잔고: {int(account_eval['총평가금액']):,}원"
                )
            
            QMessageBox.information(self, "조회 완료", "계좌 정보가 갱신되었습니다.")
            
        except Exception as e:
            QMessageBox.warning(self, "오류", f"계좌 정보 조회 중 오류 발생: {str(e)}")
    
    def on_strategy_changed(self, index):
        """전략 변경 시 호출되는 함수"""
        strategy_name = self.strategy_combo.currentText()
        
        # 전략별 파라미터 위젯 업데이트
        if strategy_name == "볼린저 밴드 전략":
            self.show_bollinger_params()
        elif strategy_name == "이동평균 전략":
            self.show_moving_average_params()
        elif strategy_name == "RSI 전략":
            self.show_rsi_params()
        elif strategy_name == "MACD 전략":
            self.show_macd_params()
        elif strategy_name == "AI 자동매매 전략":
            self.show_ai_params()
            
    def show_ai_params(self):
        """AI 자동매매 전략 파라미터 표시"""
        # 기존 파라미터 위젯 제거
        self.clear_param_widgets()
        
        # AI 전략 파라미터 그룹
        param_group = QGroupBox("AI 자동매매 파라미터")
        param_layout = QFormLayout()
        
        # 모델 타입 선택
        self.model_type_combo = QComboBox()
        self.model_type_combo.addItem("Random Forest")
        self.model_type_combo.addItem("Linear Regression")
        param_layout.addRow("모델 타입:", self.model_type_combo)
        
        # 예측 기간 설정
        self.prediction_days_spin = QSpinBox()
        self.prediction_days_spin.setRange(1, 30)
        self.prediction_days_spin.setValue(5)
        param_layout.addRow("예측 기간(일):", self.prediction_days_spin)
        
        # 신뢰도 임계값 설정
        self.confidence_threshold_spin = QDoubleSpinBox()
        self.confidence_threshold_spin.setRange(0.1, 10.0)
        self.confidence_threshold_spin.setSingleStep(0.1)
        self.confidence_threshold_spin.setValue(1.0)
        self.confidence_threshold_spin.setSuffix("%")
        param_layout.addRow("신뢰도 임계값:", self.confidence_threshold_spin)
        
        # 익절/손절 설정
        self.profit_ratio_spin = QDoubleSpinBox()
        self.profit_ratio_spin.setRange(0.1, 20.0)
        self.profit_ratio_spin.setSingleStep(0.1)
        self.profit_ratio_spin.setValue(3.0)
        self.profit_ratio_spin.setSuffix("%")
        param_layout.addRow("익절 비율:", self.profit_ratio_spin)
        
        self.loss_ratio_spin = QDoubleSpinBox()
        self.loss_ratio_spin.setRange(0.1, 20.0)
        self.loss_ratio_spin.setSingleStep(0.1)
        self.loss_ratio_spin.setValue(2.0)
        self.loss_ratio_spin.setSuffix("%")
        param_layout.addRow("손절 비율:", self.loss_ratio_spin)
        
        # 모델 학습 버튼
        self.train_model_button = QPushButton("모델 학습")
        self.train_model_button.clicked.connect(self.train_ai_model)
        param_layout.addRow("", self.train_model_button)
        
        param_group.setLayout(param_layout)
        self.param_layout.addWidget(param_group)
    
    def train_ai_model(self):
        """AI 모델 학습"""
        if not self.current_code:
            QMessageBox.warning(self, "경고", "종목을 먼저 선택해주세요.")
            return
        
        # 차트 데이터 가져오기
        if self.chart_data is None or len(self.chart_data) < 60:
            # 데이터 가져오기
            self.fetch_chart_data()
            
            if self.chart_data is None or len(self.chart_data) < 60:
                QMessageBox.warning(self, "경고", "학습에 필요한 충분한 데이터가 없습니다. (최소 60개 이상 필요)")
                return
        
        try:
            # AI 전략 생성
            from src.strategies.ai_strategy import AIStrategy
            
            # 파라미터 설정
            params = {
                'model_type': 'random_forest' if self.model_type_combo.currentText() == "Random Forest" else 'linear',
                'prediction_days': self.prediction_days_spin.value(),
                'profit_ratio': self.profit_ratio_spin.value(),
                'loss_ratio': self.loss_ratio_spin.value(),
                'confidence_threshold': self.confidence_threshold_spin.value()
            }
            
            # 전략 생성
            strategy = AIStrategy(params)
            
            # 모델 학습
            result = strategy.train_model(self.chart_data)
            
            if result:
                # 모델 저장
                if strategy.save_model(self.current_code):
                    QMessageBox.information(self, "알림", f"모델 학습 완료\n\n"
                                          f"RMSE: {result['rmse']:.4f}\n"
                                          f"R2: {result['r2']:.4f}\n"
                                          f"데이터 크기: {result['data_size']}\n"
                                          f"예측 기간: {result['prediction_days']}일")
                else:
                    QMessageBox.warning(self, "경고", "모델 저장 중 오류가 발생했습니다.")
            else:
                QMessageBox.warning(self, "경고", "모델 학습 중 오류가 발생했습니다.")
                
        except Exception as e:
            QMessageBox.critical(self, "오류", f"모델 학습 중 오류 발생: {str(e)}")
            
    def check_account_password(self):
        """계좌 비밀번호 확인"""
        account_no = self.account_combo.currentText()
        if not account_no:
            QMessageBox.warning(self, "오류", "계좌를 선택하세요.")
            return False
        
        # 부모 윈도우(MainWindow)의 get_account_password 메서드 사용
        account_password = None
        if hasattr(self.parent, 'get_account_password'):
            account_password = self.parent.get_account_password()
        else:
            # 부모 윈도우에 get_account_password 메서드가 없는 경우 대화상자 직접 표시
            password_dialog = AccountPasswordDialog(self)
            if password_dialog.exec_() != QDialog.Accepted:
                return False
            account_password = password_dialog.get_password()
        
        if not account_password:
            return False
        
        if not account_password or len(account_password) != 4:
            QMessageBox.warning(self, "오류", "유효한 계좌 비밀번호(4자리)를 입력하세요.")
            return False
        
        return True 