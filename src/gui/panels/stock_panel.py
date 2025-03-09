"""
종목 정보 패널
"""
import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QGridLayout, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt, pyqtSignal

logger = logging.getLogger(__name__)

class StockPanel(QWidget):
    """종목 정보 패널 클래스"""
    
    # 시그널 정의
    stock_selected = pyqtSignal(str, str)  # 종목 선택 시그널 (종목코드, 종목명)
    
    def __init__(self, parent=None, kiwoom=None):
        super().__init__(parent)
        self.kiwoom = kiwoom
        
        # 현재 선택된 종목 정보
        self.current_stock = None
        
        # UI 초기화
        self.init_ui()
    
    def init_ui(self):
        """UI 초기화"""
        # 메인 레이아웃
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # 검색 영역
        search_layout = QHBoxLayout()
        
        # 종목 검색
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("종목명 또는 종목코드 입력")
        self.search_btn = QPushButton("검색")
        self.search_btn.setFixedWidth(60)
        
        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(self.search_btn)
        
        main_layout.addLayout(search_layout)
        
        # 종목 정보 그리드
        info_layout = QGridLayout()
        
        # 종목코드
        self.code_label = QLabel("종목코드:")
        self.code_value = QLabel("-")
        info_layout.addWidget(self.code_label, 0, 0)
        info_layout.addWidget(self.code_value, 0, 1)
        
        # 종목명
        self.name_label = QLabel("종목명:")
        self.name_value = QLabel("-")
        info_layout.addWidget(self.name_label, 0, 2)
        info_layout.addWidget(self.name_value, 0, 3)
        
        # 현재가
        self.current_price_label = QLabel("현재가:")
        self.current_price_value = QLabel("-")
        self.current_price_value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        info_layout.addWidget(self.current_price_label, 1, 0)
        info_layout.addWidget(self.current_price_value, 1, 1)
        
        # 전일대비
        self.price_diff_label = QLabel("전일대비:")
        self.price_diff_value = QLabel("-")
        self.price_diff_value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        info_layout.addWidget(self.price_diff_label, 1, 2)
        info_layout.addWidget(self.price_diff_value, 1, 3)
        
        # 등락률
        self.change_rate_label = QLabel("등락률:")
        self.change_rate_value = QLabel("-")
        self.change_rate_value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        info_layout.addWidget(self.change_rate_label, 2, 0)
        info_layout.addWidget(self.change_rate_value, 2, 1)
        
        # 거래량
        self.volume_label = QLabel("거래량:")
        self.volume_value = QLabel("-")
        self.volume_value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        info_layout.addWidget(self.volume_label, 2, 2)
        info_layout.addWidget(self.volume_value, 2, 3)
        
        main_layout.addLayout(info_layout)
        
        # 구분선
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)
        
        # 호가 테이블
        self.hoga_table = QTableWidget()
        self.hoga_table.setColumnCount(3)
        self.hoga_table.setRowCount(10)  # 매도5호가 + 매수5호가
        self.hoga_table.setHorizontalHeaderLabels(["매도잔량", "호가", "매수잔량"])
        
        # 테이블 설정
        header = self.hoga_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.hoga_table.verticalHeader().setVisible(False)
        
        main_layout.addWidget(self.hoga_table)
        
        # 시그널 연결
        self.search_btn.clicked.connect(self._on_search_clicked)
        self.search_edit.returnPressed.connect(self._on_search_clicked)
    
    def update_stock_info(self, code=None):
        """종목 정보 업데이트"""
        try:
            if not code and self.current_stock:
                code = self.current_stock.get('code')
            
            if not code:
                logger.warning("종목코드가 없습니다.")
                return
            
            if self.kiwoom:
                # 종목 기본 정보 요청
                stock_info = self.kiwoom.get_stock_basic_info(code)
                
                if stock_info:
                    # 종목 정보 업데이트
                    self.current_stock = stock_info
                    
                    # 기본 정보 표시
                    self.code_value.setText(stock_info.get('code', '-'))
                    self.name_value.setText(stock_info.get('name', '-'))
                    
                    # 현재가
                    current_price = stock_info.get('current_price', 0)
                    self.current_price_value.setText(f"{current_price:,}")
                    
                    # 전일대비
                    price_diff = stock_info.get('price_diff', 0)
                    self.price_diff_value.setText(f"{price_diff:,}")
                    
                    # 등락률
                    change_rate = stock_info.get('change_rate', 0)
                    self.change_rate_value.setText(f"{change_rate:.2f}%")
                    
                    # 거래량
                    volume = stock_info.get('volume', 0)
                    self.volume_value.setText(f"{volume:,}")
                    
                    # 가격 변동에 따른 색상 변경
                    self._update_price_color(price_diff)
                    
                    # 호가 정보 업데이트
                    self.update_hoga_info(code)
                    
                    logger.info(f"종목 정보 업데이트 완료: {code}")
                else:
                    logger.warning(f"종목 정보를 가져올 수 없습니다: {code}")
            else:
                logger.warning("키움 API가 초기화되지 않았습니다.")
        
        except Exception as e:
            logger.error(f"종목 정보 업데이트 중 오류 발생: {e}")
    
    def update_hoga_info(self, code):
        """호가 정보 업데이트"""
        try:
            if self.kiwoom:
                # 호가 정보 요청
                hoga_info = self.kiwoom.get_stock_hoga(code)
                
                if hoga_info:
                    # 매도호가
                    for i in range(5):
                        # 매도잔량
                        sell_volume = hoga_info.get(f'매도{5-i}잔량', 0)
                        sell_volume_item = QTableWidgetItem(f"{sell_volume:,}")
                        sell_volume_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                        
                        # 호가
                        price = hoga_info.get(f'매도{5-i}호가', 0)
                        price_item = QTableWidgetItem(f"{price:,}")
                        price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                        
                        self.hoga_table.setItem(i, 0, sell_volume_item)
                        self.hoga_table.setItem(i, 1, price_item)
                        
                        # 매도호가는 파란색
                        sell_volume_item.setForeground(Qt.blue)
                        price_item.setForeground(Qt.blue)
                    
                    # 매수호가
                    for i in range(5):
                        # 호가
                        price = hoga_info.get(f'매수{i+1}호가', 0)
                        price_item = QTableWidgetItem(f"{price:,}")
                        price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                        
                        # 매수잔량
                        buy_volume = hoga_info.get(f'매수{i+1}잔량', 0)
                        buy_volume_item = QTableWidgetItem(f"{buy_volume:,}")
                        buy_volume_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                        
                        self.hoga_table.setItem(i+5, 1, price_item)
                        self.hoga_table.setItem(i+5, 2, buy_volume_item)
                        
                        # 매수호가는 빨간색
                        price_item.setForeground(Qt.red)
                        buy_volume_item.setForeground(Qt.red)
                    
                    logger.info(f"호가 정보 업데이트 완료: {code}")
                else:
                    logger.warning(f"호가 정보를 가져올 수 없습니다: {code}")
        
        except Exception as e:
            logger.error(f"호가 정보 업데이트 중 오류 발생: {e}")
    
    def _update_price_color(self, price_diff):
        """가격 변동에 따른 색상 변경"""
        if price_diff > 0:
            color = "red"
        elif price_diff < 0:
            color = "blue"
        else:
            color = "black"
        
        self.current_price_value.setStyleSheet(f"color: {color};")
        self.price_diff_value.setStyleSheet(f"color: {color};")
        self.change_rate_value.setStyleSheet(f"color: {color};")
    
    def _on_search_clicked(self):
        """검색 버튼 클릭 이벤트 핸들러"""
        search_text = self.search_edit.text().strip()
        if not search_text:
            return
        
        try:
            if self.kiwoom:
                # 종목 검색
                if search_text.isdigit():
                    # 종목코드로 검색
                    code = search_text
                    name = self.kiwoom.get_master_code_name(code)
                else:
                    # 종목명으로 검색
                    code = self.kiwoom.get_stock_code_by_name(search_text)
                    name = search_text
                
                if code:
                    logger.info(f"종목 검색 성공: {name} ({code})")
                    self.stock_selected.emit(code, name)
                    self.update_stock_info(code)
                else:
                    logger.warning(f"종목을 찾을 수 없습니다: {search_text}")
            else:
                logger.warning("키움 API가 초기화되지 않았습니다.")
        
        except Exception as e:
            logger.error(f"종목 검색 중 오류 발생: {e}")
    
    def clear(self):
        """종목 정보 초기화"""
        self.current_stock = None
        self.code_value.setText("-")
        self.name_value.setText("-")
        self.current_price_value.setText("-")
        self.price_diff_value.setText("-")
        self.change_rate_value.setText("-")
        self.volume_value.setText("-")
        
        # 호가 테이블 초기화
        self.hoga_table.clearContents() 