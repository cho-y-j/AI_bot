"""
호가창 패널 모듈
"""
import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView,
    QTabWidget, QGridLayout, QPushButton, QFrame,
    QRadioButton, QButtonGroup, QLineEdit, QCompleter,
    QDialog, QDialogButtonBox, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QStringListModel
from PyQt5.QtGui import QColor, QFont

# 로깅 설정
logger = logging.getLogger(__name__)

class StockSearchDialog(QDialog):
    """종목 검색 다이얼로그"""
    def __init__(self, parent=None, kiwoom=None):
        super().__init__(parent)
        self.kiwoom = kiwoom
        self.selected_code = None
        self.selected_name = None
        self.init_ui()
        
    def init_ui(self):
        """UI 초기화"""
        self.setWindowTitle("종목 검색")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # 검색어 입력
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("종목코드 또는 종목명 입력")
        search_btn = QPushButton("검색")
        
        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(search_btn)
        
        layout.addLayout(search_layout)
        
        # 검색 결과 테이블
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(3)
        self.result_table.setHorizontalHeaderLabels(["종목코드", "종목명", "시장"])
        self.result_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.result_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(self.result_table)
        
        # 확인/취소 버튼
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self
        )
        layout.addWidget(buttons)
        
        # 이벤트 연결
        search_btn.clicked.connect(self.search_stock)
        self.search_edit.returnPressed.connect(self.search_stock)
        self.result_table.cellDoubleClicked.connect(self.select_stock)
        buttons.accepted.connect(self.accept_stock)
        buttons.rejected.connect(self.reject)
        
    def search_stock(self):
        """종목 검색"""
        if not self.kiwoom:
            logger.warning("키움 API가 초기화되지 않았습니다.")
            QMessageBox.warning(self, "오류", "키움 API가 초기화되지 않았습니다.")
            return
            
        keyword = self.search_edit.text().strip()
        if not keyword:
            return
            
        try:
            # 종목 검색
            stocks = []
            
            if keyword.isdigit():
                # 종목코드로 검색
                name = self.kiwoom.get_master_code_name(keyword)
                if name:
                    stocks.append({
                        '종목코드': keyword,
                        '종목명': name,
                        '시장구분': '코스피' if keyword in self.kiwoom.get_code_list_by_market('0') else '코스닥'
                    })
            else:
                # 종목명으로 검색
                kospi_codes = self.kiwoom.get_code_list_by_market('0')
                kosdaq_codes = self.kiwoom.get_code_list_by_market('10')
                
                for code in kospi_codes + kosdaq_codes:
                    name = self.kiwoom.get_master_code_name(code)
                    if name and keyword.upper() in name.upper():
                        stocks.append({
                            '종목코드': code,
                            '종목명': name,
                            '시장구분': '코스피' if code in kospi_codes else '코스닥'
                        })
            
            # 검색 결과 표시
            self.result_table.setRowCount(0)
            
            if stocks:
                for stock in stocks:
                    row = self.result_table.rowCount()
                    self.result_table.insertRow(row)
                    
                    code_item = QTableWidgetItem(stock['종목코드'])
                    name_item = QTableWidgetItem(stock['종목명'])
                    market_item = QTableWidgetItem(stock['시장구분'])
                    
                    self.result_table.setItem(row, 0, code_item)
                    self.result_table.setItem(row, 1, name_item)
                    self.result_table.setItem(row, 2, market_item)
            else:
                QMessageBox.information(self, "검색 결과", "검색 결과가 없습니다.")
                
        except Exception as e:
            logger.error(f"종목 검색 중 오류 발생: {e}")
            QMessageBox.warning(self, "오류", f"종목 검색 중 오류 발생: {e}")
    
    def select_stock(self, row, col):
        """종목 선택"""
        self.selected_code = self.result_table.item(row, 0).text()
        self.selected_name = self.result_table.item(row, 1).text()
        self.accept()
    
    def accept_stock(self):
        """종목 선택 확인"""
        current_row = self.result_table.currentRow()
        if current_row >= 0:
            self.selected_code = self.result_table.item(current_row, 0).text()
            self.selected_name = self.result_table.item(current_row, 1).text()
            self.accept()
        else:
            QMessageBox.warning(self, "알림", "종목을 선택해주세요.")
    
    def get_selected_stock(self):
        """선택된 종목 정보 반환"""
        return self.selected_code, self.selected_name

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
        
        # 실시간 데이터 요청 상태
        self.real_time_subscribed = False
        
        # 종목 검색을 위한 자동완성 데이터
        self.stock_list = []
        self.load_stock_list()
        
        # 실시간 데이터 FID
        self.real_type = {
            '주식시세': {
                "10": "현재가",
                "11": "전일대비",
                "12": "등락율",
                "27": "매도호가",
                "28": "매수호가",
                "13": "누적거래량",
                "14": "누적거래대금",
                "16": "시가",
                "17": "고가",
                "18": "저가",
                "25": "전일대비기호",
                "26": "전일거래량대비",
            },
            '주식호가잔량': {
                "121": "매도호가1",
                "122": "매도호가2",
                "123": "매도호가3",
                "124": "매도호가4",
                "125": "매도호가5",
                "126": "매도호가6",
                "127": "매도호가7",
                "128": "매도호가8",
                "129": "매도호가9",
                "130": "매도호가10",
                "131": "매도호가수량1",
                "132": "매도호가수량2",
                "133": "매도호가수량3",
                "134": "매도호가수량4",
                "135": "매도호가수량5",
                "136": "매도호가수량6",
                "137": "매도호가수량7",
                "138": "매도호가수량8",
                "139": "매도호가수량9",
                "140": "매도호가수량10",
                "141": "매수호가1",
                "142": "매수호가2",
                "143": "매수호가3",
                "144": "매수호가4",
                "145": "매수호가5",
                "146": "매수호가6",
                "147": "매수호가7",
                "148": "매수호가8",
                "149": "매수호가9",
                "150": "매수호가10",
                "151": "매수호가수량1",
                "152": "매수호가수량2",
                "153": "매수호가수량3",
                "154": "매수호가수량4",
                "155": "매수호가수량5",
                "156": "매수호가수량6",
                "157": "매수호가수량7",
                "158": "매수호가수량8",
                "159": "매수호가수량9",
                "160": "매수호가수량10",
            }
        }
        
        # UI 초기화
        self.init_ui()
    
    def init_ui(self):
        """UI 초기화"""
        main_layout = QVBoxLayout()
        
        # 종목 검색 영역
        self.init_search_area()
        main_layout.addLayout(self.search_layout)
        
        # 종목 정보 영역
        self.init_stock_info_area()
        main_layout.addWidget(self.stock_info_frame)
        
        # 호가 영역
        hoga_layout = QVBoxLayout()
        
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
        
        hoga_layout.addLayout(hoga_radio_layout)
        
        # 호가 테이블
        self.init_hoga_table()
        hoga_layout.addWidget(self.hoga_table)
        
        main_layout.addLayout(hoga_layout)
        
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
    
    def init_search_area(self):
        """종목 검색 영역 초기화"""
        self.search_layout = QHBoxLayout()
        
        # 종목 코드 입력
        self.code_edit = QLineEdit()
        self.code_edit.setPlaceholderText("종목코드")
        self.code_edit.setMaximumWidth(100)
        self.code_edit.returnPressed.connect(self.on_code_entered)
        
        # 종목명 입력
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("종목명")
        self.name_edit.setMinimumWidth(150)
        self.name_edit.textChanged.connect(self.on_name_text_changed)
        
        # 자동완성 설정
        self.completer = QCompleter()
        self.completer.setFilterMode(Qt.MatchContains)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer_model = QStringListModel()
        self.completer.setModel(self.completer_model)
        self.completer.activated.connect(self.on_completer_activated)
        self.name_edit.setCompleter(self.completer)
        
        # 검색 버튼
        search_btn = QPushButton("검색")
        search_btn.clicked.connect(self.on_search_clicked)
        
        self.search_layout.addWidget(self.code_edit)
        self.search_layout.addWidget(self.name_edit)
        self.search_layout.addWidget(search_btn)
    
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
    
    def load_stock_list(self):
        """종목 리스트 로드"""
        try:
            if self.kiwoom:
                self.stock_list = []  # 리스트 초기화
                
                # 코스피 종목 로드
                kospi_codes = self.kiwoom.get_code_list_by_market('0')
                for code in kospi_codes:
                    name = self.kiwoom.get_master_code_name(code)
                    if name:
                        self.stock_list.append(f"{name}({code})")
                
                # 코스닥 종목 로드
                kosdaq_codes = self.kiwoom.get_code_list_by_market('10')
                for code in kosdaq_codes:
                    name = self.kiwoom.get_master_code_name(code)
                    if name:
                        self.stock_list.append(f"{name}({code})")
                
                # 자동완성 데이터 설정
                self.completer_model.setStringList(self.stock_list)
                logger.info(f"종목 리스트 로드 완료: {len(self.stock_list)}개")
        except Exception as e:
            self.log_message(f"종목 리스트 로드 중 오류 발생: {str(e)}")
    
    def on_name_text_changed(self, text):
        """종목명 입력 시 자동완성"""
        if not text.strip():
            return
            
        try:
            # 종목 검색
            stocks = self.kiwoom.search_stock(text)
            if stocks:
                # 검색 결과를 자동완성 목록에 추가
                items = [f"{stock['종목명']}({stock['종목코드']})" for stock in stocks]
                self.completer_model.setStringList(items)
                self.completer.complete()
        except Exception as e:
            self.log_message(f"종목 검색 중 오류 발생: {str(e)}")
    
    def on_completer_activated(self, text):
        """자동완성에서 종목 선택 시 처리"""
        if text:
            start_idx = text.find("(")
            end_idx = text.find(")")
            if start_idx > 0 and end_idx > start_idx:
                code = text[start_idx + 1:end_idx]
                name = text[:start_idx]
                self.set_stock(code, name)
    
    def on_code_entered(self):
        """종목 코드 입력 시 처리"""
        code = self.code_edit.text().strip()
        if code and self.kiwoom:
            try:
                name = self.kiwoom.get_master_code_name(code)
                if name:
                    self.set_stock(code, name)
                else:
                    self.log_message(f"종목을 찾을 수 없습니다: {code}")
            except Exception as e:
                self.log_message(f"종목 검색 중 오류 발생: {str(e)}")
    
    def on_search_clicked(self):
        """검색 버튼 클릭 시 처리"""
        text = self.name_edit.text().strip()
        if text and self.kiwoom:
            try:
                stocks = self.kiwoom.search_stock(text)
                if stocks:
                    # 검색 결과를 자동완성 목록에 추가
                    items = [f"{stock['종목명']}({stock['종목코드']})" for stock in stocks]
                    self.completer_model.setStringList(items)
                    self.completer.complete()
                else:
                    self.log_message(f"종목을 찾을 수 없습니다: {text}")
            except Exception as e:
                self.log_message(f"종목 검색 중 오류 발생: {str(e)}")
    
    def set_stock(self, code, name=None):
        """종목 설정"""
        try:
            # 이전 종목 실시간 데이터 해제
            self.unregister_real_time()
            
            self.stock_code = code
            self.stock_name = name or self.kiwoom.get_master_code_name(code)
            
            # 종목 정보 업데이트
            self.stock_name_label.setText(f"{self.stock_name} ({code})")
            
            # 기본 정보 조회
            stock_info = self.kiwoom.get_stock_basic_info(code)
            if stock_info:
                current_price = abs(int(stock_info['현재가']))
                diff = int(stock_info['전일대비'])
                diff_rate = float(stock_info['등락율'])
                volume = int(stock_info['거래량'])
                value = int(stock_info['거래대금'])
                
                # 현재가 표시
                self.current_price_label.setText(f"{current_price:,}")
                
                # 등락률 표시
                if diff > 0:
                    self.current_price_label.setStyleSheet("color: red;")
                    self.change_rate_label.setStyleSheet("color: red;")
                    diff_text = f"▲ {diff:,} ({diff_rate:.2f}%)"
                elif diff < 0:
                    self.current_price_label.setStyleSheet("color: blue;")
                    self.change_rate_label.setStyleSheet("color: blue;")
                    diff_text = f"▼ {abs(diff):,} ({diff_rate:.2f}%)"
                else:
                    self.current_price_label.setStyleSheet("")
                    self.change_rate_label.setStyleSheet("")
                    diff_text = f"- {diff:,} ({diff_rate:.2f}%)"
                
                self.change_rate_label.setText(diff_text)
                self.volume_label.setText(f"거래량: {volume:,}")
                self.trading_value_label.setText(f"거래대금: {value/1000000:.0f}백만")
            
            # 호가 정보 조회
            hoga_info = self.kiwoom.get_stock_hoga(code)
            if hoga_info:
                self.update_hoga_info(code, hoga_info)
            
            # 데이터 갱신
            self.refresh_data()
            
            # 실시간 데이터 등록
            self.register_real_time()
            
            # 검색창 초기화
            self.code_edit.clear()
            self.name_edit.clear()
            
        except Exception as e:
            self.log_message(f"종목 설정 중 오류 발생: {str(e)}")
    
    def update_hoga_info(self, stock_code, hoga_info=None):
        """호가 정보 업데이트"""
        try:
            if not self.kiwoom or not stock_code:
                return
            
            if not hoga_info:
                hoga_info = self.kiwoom.get_stock_hoga(stock_code)
            
            if not hoga_info:
                return
                
            hoga_count = 5 if self.current_hoga_type == 5 else 10
            
            # 호가 데이터 업데이트
            for i in range(hoga_count):
                # 매도호가
                sell_price = abs(int(hoga_info.get(f'매도호가{i+1}', 0)))
                sell_volume = int(hoga_info.get(f'매도호가수량{i+1}', 0))
                
                # 매수호가
                buy_price = abs(int(hoga_info.get(f'매수호가{i+1}', 0)))
                buy_volume = int(hoga_info.get(f'매수호가수량{i+1}', 0))
                
                # 매도호가 표시 (상위)
                if sell_price > 0:
                    sell_item = QTableWidgetItem(f"{sell_volume:,}")
                    price_item = QTableWidgetItem(f"{sell_price:,}")
                    self.hoga_table.setItem(hoga_count-1-i, 0, sell_item)
                    self.hoga_table.setItem(hoga_count-1-i, 1, price_item)
                    
                    sell_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    
                    sell_item.setBackground(QColor(220, 240, 255))
                    price_item.setBackground(QColor(220, 240, 255))
                
                # 매수호가 표시 (하위)
                if buy_price > 0:
                    buy_item = QTableWidgetItem(f"{buy_volume:,}")
                    price_item = QTableWidgetItem(f"{buy_price:,}")
                    self.hoga_table.setItem(hoga_count+i, 0, buy_item)
                    self.hoga_table.setItem(hoga_count+i, 1, price_item)
                    
                    buy_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    
                    buy_item.setBackground(QColor(255, 230, 230))
                    price_item.setBackground(QColor(255, 230, 230))
            
            # 현재가 강조 표시
            current_price = abs(int(hoga_info.get('현재가', 0)))
            if current_price > 0:
                current_item = QTableWidgetItem(f"{current_price:,}")
                current_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                current_item.setBackground(QColor(255, 255, 200))
                self.hoga_table.setItem(hoga_count-1, 1, current_item)
            
        except Exception as e:
            self.log_message(f"호가 정보 업데이트 중 오류 발생: {str(e)}")
    
    def update_daily_data(self):
        """일별 데이터 업데이트"""
        try:
            if not self.kiwoom or not self.stock_code:
                return
            
            # 일별 데이터 요청
            self.kiwoom.set_input_value("종목코드", self.stock_code)
            self.kiwoom.set_input_value("기준일자", "")
            self.kiwoom.set_input_value("수정주가구분", "1")
            self.kiwoom.comm_rq_data("opt10081_req", "opt10081", 0, "0101")
            
            # 데이터 가져오기
            for i in range(20):  # 최근 20일치 데이터
                date = self.kiwoom.get_comm_data("opt10081", "opt10081_req", i, "일자")
                close = self.kiwoom.get_comm_data("opt10081", "opt10081_req", i, "현재가")
                diff = self.kiwoom.get_comm_data("opt10081", "opt10081_req", i, "전일대비")
                rate = self.kiwoom.get_comm_data("opt10081", "opt10081_req", i, "등락율")
                volume = self.kiwoom.get_comm_data("opt10081", "opt10081_req", i, "거래량")
                
                if date and close:
                    # 테이블에 데이터 설정
                    self.daily_table.setItem(i, 0, QTableWidgetItem(date))
                    self.daily_table.setItem(i, 1, QTableWidgetItem(f"{int(close):,}"))
                    self.daily_table.setItem(i, 2, QTableWidgetItem(f"{int(diff):,}"))
                    self.daily_table.setItem(i, 3, QTableWidgetItem(f"{float(rate):.2f}%"))
                    self.daily_table.setItem(i, 4, QTableWidgetItem(f"{int(volume):,}"))
                    
                    # 등락에 따른 색상 설정
                    if float(diff) > 0:
                        self.daily_table.item(i, 1).setForeground(QColor(255, 0, 0))
                        self.daily_table.item(i, 2).setForeground(QColor(255, 0, 0))
                        self.daily_table.item(i, 3).setForeground(QColor(255, 0, 0))
                    elif float(diff) < 0:
                        self.daily_table.item(i, 1).setForeground(QColor(0, 0, 255))
                        self.daily_table.item(i, 2).setForeground(QColor(0, 0, 255))
                        self.daily_table.item(i, 3).setForeground(QColor(0, 0, 255))
            
        except Exception as e:
            self.log_message(f"일별 데이터 업데이트 중 오류 발생: {str(e)}")
    
    def update_investor_data(self):
        """투자자 데이터 업데이트"""
        try:
            if not self.kiwoom or not self.stock_code:
                return
            
            # 투자자 데이터 요청
            self.kiwoom.set_input_value("종목코드", self.stock_code)
            self.kiwoom.set_input_value("시작일자", "")
            self.kiwoom.set_input_value("종료일자", "")
            self.kiwoom.comm_rq_data("opt10059_req", "opt10059", 0, "0101")
            
            # 데이터 가져오기
            for i in range(5):  # 최근 5일치 데이터
                date = self.kiwoom.get_comm_data("opt10059", "opt10059_req", i, "일자")
                foreign = self.kiwoom.get_comm_data("opt10059", "opt10059_req", i, "외국인")
                institution = self.kiwoom.get_comm_data("opt10059", "opt10059_req", i, "기관계")
                pension = self.kiwoom.get_comm_data("opt10059", "opt10059_req", i, "연기금등")
                program = self.kiwoom.get_comm_data("opt10059", "opt10059_req", i, "프로그램")
                finance = self.kiwoom.get_comm_data("opt10059", "opt10059_req", i, "금융투자")
                
                if date:
                    # 테이블에 데이터 설정
                    self.investor_table.setItem(i, 0, QTableWidgetItem(date))
                    self.investor_table.setItem(i, 1, QTableWidgetItem(f"{int(foreign):,}"))
                    self.investor_table.setItem(i, 2, QTableWidgetItem(f"{int(institution):,}"))
                    self.investor_table.setItem(i, 3, QTableWidgetItem(f"{int(pension):,}"))
                    self.investor_table.setItem(i, 4, QTableWidgetItem(f"{int(program):,}"))
                    self.investor_table.setItem(i, 5, QTableWidgetItem(f"{int(finance):,}"))
                    
                    # 순매수/매도에 따른 색상 설정
                    for j in range(1, 6):
                        value = float(self.investor_table.item(i, j).text().replace(",", ""))
                        if value > 0:
                            self.investor_table.item(i, j).setForeground(QColor(255, 0, 0))
                        elif value < 0:
                            self.investor_table.item(i, j).setForeground(QColor(0, 0, 255))
            
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
                # 실시간 시세 등록
                self.kiwoom.subscribe_stock_conclusion(self.stock_code)
                self.kiwoom.subscribe_stock_hoga(self.stock_code)
                
                self.real_time_subscribed = True
                logger.info(f"실시간 데이터 등록 완료: {self.stock_code}")
        except Exception as e:
            self.log_message(f"실시간 데이터 등록 중 오류 발생: {str(e)}")
    
    def unregister_real_time(self):
        """실시간 데이터 해제"""
        try:
            if self.kiwoom and self.real_time_subscribed:
                self.kiwoom.unsubscribe_stock_conclusion(self.stock_code)
                self.kiwoom.unsubscribe_stock_hoga(self.stock_code)
                
                self.real_time_subscribed = False
                logger.info(f"실시간 데이터 해제 완료: {self.stock_code}")
        except Exception as e:
            self.log_message(f"실시간 데이터 해제 중 오류 발생: {str(e)}")
    
    def request_chart(self):
        """차트 요청"""
        if self.stock_code:
            self.chart_requested.emit(self.stock_code)
    
    def closeEvent(self, event):
        """패널 종료 시 처리"""
        self.unregister_real_time()
        event.accept()
    
    def log_message(self, message):
        """로그 메시지 출력"""
        logger.error(message)

    def init_hoga_table(self):
        """호가 테이블 초기화"""
        self.hoga_table = QTableWidget()
        self.hoga_table.setRowCount(20)  # 10호가 기준
        self.hoga_table.setColumnCount(3)
        self.hoga_table.setHorizontalHeaderLabels(["매도잔량", "호가", "매수잔량"])
        
        # 열 너비 설정
        header = self.hoga_table.horizontalHeader()
        for i in range(3):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        
        # 테이블 스타일 설정
        self.hoga_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.hoga_table.verticalHeader().setVisible(False)
        self.hoga_table.setShowGrid(True)
        
        # 기본 아이템 설정
        for i in range(20):
            for j in range(3):
                item = QTableWidgetItem("")
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.hoga_table.setItem(i, j, item)
        
        # 호가 선택 시그널 연결
        self.hoga_radio_group.buttonClicked.connect(self.on_hoga_type_changed)
        
        # 초기 호가 타입 설정
        self.current_hoga_type = 5
        self.update_hoga_display()

    def on_hoga_type_changed(self, button):
        """호가 타입 변경 시 처리"""
        self.current_hoga_type = self.hoga_radio_group.id(button)
        self.update_hoga_display()
        self.refresh_data()

    def update_hoga_display(self):
        """호가창 표시 방식 업데이트"""
        if self.current_hoga_type == 5:
            self.hoga_table.setRowCount(10)  # 5호가
        else:
            self.hoga_table.setRowCount(20)  # 10호가

    def init_daily_tab(self, tab):
        """일별 데이터 탭 초기화"""
        layout = QVBoxLayout()
        
        # 일별 데이터 테이블
        self.daily_table = QTableWidget()
        self.daily_table.setRowCount(20)
        self.daily_table.setColumnCount(5)
        self.daily_table.setHorizontalHeaderLabels(["일자", "종가", "전일대비", "등락률", "거래량"])
        
        # 열 너비 설정
        header = self.daily_table.horizontalHeader()
        for i in range(5):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        
        # 테이블 스타일 설정
        self.daily_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.daily_table.verticalHeader().setVisible(False)
        self.daily_table.setShowGrid(True)
        
        layout.addWidget(self.daily_table)
        tab.setLayout(layout)

    def init_investor_tab(self, tab):
        """투자자 데이터 탭 초기화"""
        layout = QVBoxLayout()
        
        # 투자자 데이터 테이블
        self.investor_table = QTableWidget()
        self.investor_table.setRowCount(5)
        self.investor_table.setColumnCount(6)
        self.investor_table.setHorizontalHeaderLabels(["일자", "외국인", "기관계", "연기금등", "프로그램", "금융투자"])
        
        # 열 너비 설정
        header = self.investor_table.horizontalHeader()
        for i in range(6):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        
        # 테이블 스타일 설정
        self.investor_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.investor_table.verticalHeader().setVisible(False)
        self.investor_table.setShowGrid(True)
        
        layout.addWidget(self.investor_table)
        tab.setLayout(layout)

    def on_real_data(self, sCode, sRealType, sRealData):
        """실시간 데이터 수신"""
        try:
            if sCode != self.stock_code:
                return
                
            if sRealType == "주식시세":
                # 현재가 업데이트
                current_price = abs(int(self.kiwoom.get_comm_real_data(sCode, 10)))  # 현재가
                diff = int(self.kiwoom.get_comm_real_data(sCode, 11))  # 전일대비
                diff_rate = float(self.kiwoom.get_comm_real_data(sCode, 12))  # 등락율
                volume = int(self.kiwoom.get_comm_real_data(sCode, 13))  # 누적거래량
                value = int(self.kiwoom.get_comm_real_data(sCode, 14))  # 누적거래대금
                
                # 현재가 표시
                self.current_price_label.setText(f"{current_price:,}")
                if diff > 0:
                    self.current_price_label.setStyleSheet("color: red;")
                    self.change_rate_label.setStyleSheet("color: red;")
                    diff_text = f"▲ {diff:,} ({diff_rate:.2f}%)"
                elif diff < 0:
                    self.current_price_label.setStyleSheet("color: blue;")
                    self.change_rate_label.setStyleSheet("color: blue;")
                    diff_text = f"▼ {abs(diff):,} ({diff_rate:.2f}%)"
                else:
                    self.current_price_label.setStyleSheet("")
                    self.change_rate_label.setStyleSheet("")
                    diff_text = f"- {diff:,} ({diff_rate:.2f}%)"
                
                self.change_rate_label.setText(diff_text)
                self.volume_label.setText(f"거래량: {volume:,}")
                self.trading_value_label.setText(f"거래대금: {value/1000000:.0f}백만")
                
            elif sRealType == "주식호가잔량":
                # 호가 데이터 업데이트
                for i in range(10):
                    # 매도호가
                    sell_price = abs(int(self.kiwoom.get_comm_real_data(sCode, 121+i)))  # 매도호가
                    sell_volume = int(self.kiwoom.get_comm_real_data(sCode, 131+i))  # 매도호가수량
                    
                    # 매수호가
                    buy_price = abs(int(self.kiwoom.get_comm_real_data(sCode, 141+i)))  # 매수호가
                    buy_volume = int(self.kiwoom.get_comm_real_data(sCode, 151+i))  # 매수호가수량
                    
                    # 호가창 업데이트
                    if sell_price > 0:
                        self.hoga_table.item(i, 0).setText(f"{sell_volume:,}")
                        self.hoga_table.item(i, 1).setText(f"{sell_price:,}")
                    
                    if buy_price > 0:
                        self.hoga_table.item(19-i, 2).setText(f"{buy_volume:,}")
                        self.hoga_table.item(19-i, 1).setText(f"{buy_price:,}")
                
        except Exception as e:
            self.log_message(f"실시간 데이터 처리 중 오류 발생: {str(e)}") 