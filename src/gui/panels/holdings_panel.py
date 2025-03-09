"""
보유종목 패널 모듈
"""
import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMenu, QComboBox, QMessageBox,
    QInputDialog
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCursor, QColor

logger = logging.getLogger(__name__)

class HoldingsPanel(QWidget):
    """보유종목 패널 클래스"""
    
    # 시그널 정의
    sell_requested = pyqtSignal(str, str, int)  # 매도 요청 시그널 (종목코드, 종목명, 수량)
    chart_requested = pyqtSignal(str)  # 차트 요청 시그널 (종목코드)
    
    def __init__(self, parent=None, kiwoom=None):
        """
        초기화
        
        Args:
            parent: 부모 위젯
            kiwoom: 키움 API 객체
        """
        super().__init__(parent)
        self.kiwoom = kiwoom
        self.account_no = None
        self._real_time_enabled = False
        
        # UI 초기화
        self.init_ui()
    
    def init_ui(self):
        """UI 초기화"""
        # 메인 레이아웃
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # 상단 영역
        top_layout = QHBoxLayout()
        
        # 계좌 정보 영역
        account_layout = QHBoxLayout()
        
        # 예수금 라벨
        self.deposit_label = QLabel("예수금:")
        self.deposit_value = QLabel("0")
        self.deposit_value.setStyleSheet("font-weight: bold;")
        account_layout.addWidget(self.deposit_label)
        account_layout.addWidget(self.deposit_value)
        
        account_layout.addSpacing(20)
        
        # 총평가금액 라벨
        self.total_label = QLabel("총평가금액:")
        self.total_value = QLabel("0")
        self.total_value.setStyleSheet("font-weight: bold;")
        account_layout.addWidget(self.total_label)
        account_layout.addWidget(self.total_value)
        
        account_layout.addSpacing(20)
        
        # 총평가손익 라벨
        self.profit_label = QLabel("총평가손익:")
        self.profit_value = QLabel("0")
        self.profit_value.setStyleSheet("font-weight: bold;")
        account_layout.addWidget(self.profit_label)
        account_layout.addWidget(self.profit_value)
        
        account_layout.addSpacing(20)
        
        # 수익률 라벨
        self.yield_label = QLabel("수익률:")
        self.yield_value = QLabel("0.00%")
        self.yield_value.setStyleSheet("font-weight: bold;")
        account_layout.addWidget(self.yield_label)
        account_layout.addWidget(self.yield_value)
        
        top_layout.addLayout(account_layout)
        top_layout.addStretch()
        
        # 필터 콤보박스
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["전체", "수익", "손실"])
        self.filter_combo.setFixedWidth(80)
        top_layout.addWidget(self.filter_combo)
        
        # 새로고침 버튼
        self.refresh_btn = QPushButton("새로고침")
        self.refresh_btn.setFixedWidth(80)
        top_layout.addWidget(self.refresh_btn)
        
        main_layout.addLayout(top_layout)
        
        # 보유종목 테이블
        self.holdings_table = QTableWidget()
        self.holdings_table.setColumnCount(9)
        self.holdings_table.setHorizontalHeaderLabels([
            "종목코드", "종목명", "보유수량", "매입가", 
            "현재가", "평가손익", "수익률", "평가금액", "매도"
        ])
        
        # 테이블 설정
        header = self.holdings_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # 종목명 열은 늘어나도록
        self.holdings_table.setEditTriggers(QTableWidget.NoEditTriggers)  # 편집 불가
        self.holdings_table.setSelectionBehavior(QTableWidget.SelectRows)  # 행 단위 선택
        self.holdings_table.setContextMenuPolicy(Qt.CustomContextMenu)  # 우클릭 메뉴 활성화
        
        main_layout.addWidget(self.holdings_table)
        
        # 시그널 연결
        self.refresh_btn.clicked.connect(self.update_holdings)
        self.holdings_table.customContextMenuRequested.connect(self._show_context_menu)
        self.filter_combo.currentTextChanged.connect(self._apply_filter)
    
    def set_account(self, account_no):
        """계좌번호 설정"""
        self.account_no = account_no
        self.update_holdings()
    
    def update_holdings(self):
        """보유종목 정보 업데이트"""
        try:
            if not self.kiwoom or not self.account_no:
                logger.warning("키움 API 또는 계좌가 설정되지 않았습니다.")
                return
            
            # 예수금 조회
            deposit = self.kiwoom.get_deposit(self.account_no)
            self.deposit_value.setText(f"{deposit:,}")
            
            # 보유종목 조회
            holdings = self.kiwoom.get_holdings(self.account_no)
            
            # 테이블 초기화
            self.holdings_table.setRowCount(0)
            
            total_value = 0  # 총평가금액
            total_profit = 0  # 총평가손익
            
            if holdings:
                for stock in holdings:
                    row = self.holdings_table.rowCount()
                    self.holdings_table.insertRow(row)
                    
                    # 종목코드
                    code_item = QTableWidgetItem(stock['종목코드'])
                    self.holdings_table.setItem(row, 0, code_item)
                    
                    # 종목명
                    name_item = QTableWidgetItem(stock['종목명'])
                    self.holdings_table.setItem(row, 1, name_item)
                    
                    # 보유수량
                    quantity = int(stock['보유수량'])
                    quantity_item = QTableWidgetItem(f"{quantity:,}")
                    quantity_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    self.holdings_table.setItem(row, 2, quantity_item)
                    
                    # 매입가
                    buy_price = int(stock['매입가'])
                    buy_price_item = QTableWidgetItem(f"{buy_price:,}")
                    buy_price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    self.holdings_table.setItem(row, 3, buy_price_item)
                    
                    # 현재가
                    current_price = int(stock['현재가'])
                    current_price_item = QTableWidgetItem(f"{current_price:,}")
                    current_price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    self.holdings_table.setItem(row, 4, current_price_item)
                    
                    # 평가손익
                    profit = (current_price - buy_price) * quantity
                    profit_item = QTableWidgetItem(f"{profit:+,}")
                    profit_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    if profit > 0:
                        profit_item.setForeground(QColor('red'))
                    elif profit < 0:
                        profit_item.setForeground(QColor('blue'))
                    self.holdings_table.setItem(row, 5, profit_item)
                    
                    # 수익률
                    rate = (current_price / buy_price - 1) * 100
                    rate_item = QTableWidgetItem(f"{rate:+.2f}%")
                    rate_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    if rate > 0:
                        rate_item.setForeground(QColor('red'))
                    elif rate < 0:
                        rate_item.setForeground(QColor('blue'))
                    self.holdings_table.setItem(row, 6, rate_item)
                    
                    # 평가금액
                    value = current_price * quantity
                    value_item = QTableWidgetItem(f"{value:,}")
                    value_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    self.holdings_table.setItem(row, 7, value_item)
                    
                    # 매도 버튼
                    sell_btn = QPushButton("매도")
                    sell_btn.clicked.connect(lambda x, r=row: self._sell_stock(r))
                    self.holdings_table.setCellWidget(row, 8, sell_btn)
                    
                    # 합계 계산
                    total_value += value
                    total_profit += profit
                
                # 총평가금액 업데이트
                self.total_value.setText(f"{total_value:,}")
                
                # 총평가손익 업데이트
                self.profit_value.setText(f"{total_profit:+,}")
                if total_profit > 0:
                    self.profit_value.setStyleSheet("font-weight: bold; color: red;")
                elif total_profit < 0:
                    self.profit_value.setStyleSheet("font-weight: bold; color: blue;")
                else:
                    self.profit_value.setStyleSheet("font-weight: bold;")
                
                # 수익률 업데이트
                total_buy = total_value - total_profit
                if total_buy > 0:
                    total_yield = (total_value / total_buy - 1) * 100
                    self.yield_value.setText(f"{total_yield:+.2f}%")
                    if total_yield > 0:
                        self.yield_value.setStyleSheet("font-weight: bold; color: red;")
                    elif total_yield < 0:
                        self.yield_value.setStyleSheet("font-weight: bold; color: blue;")
                    else:
                        self.yield_value.setStyleSheet("font-weight: bold;")
                
                # 실시간 시세 등록
                if not self._real_time_enabled:
                    self._enable_real_time()
            
            else:
                logger.info("보유종목이 없습니다.")
                
                # 합계 초기화
                self.total_value.setText("0")
                self.profit_value.setText("0")
                self.yield_value.setText("0.00%")
                self.profit_value.setStyleSheet("font-weight: bold;")
                self.yield_value.setStyleSheet("font-weight: bold;")
        
        except Exception as e:
            logger.error(f"보유종목 업데이트 중 오류 발생: {e}")
    
    def _enable_real_time(self):
        """실시간 시세 등록"""
        try:
            if self.kiwoom and not self._real_time_enabled:
                # 실시간 시세 등록
                codes = []
                for row in range(self.holdings_table.rowCount()):
                    code = self.holdings_table.item(row, 0).text()
                    codes.append(code)
                
                if codes:
                    self.kiwoom.set_real_reg("2000", codes, "10", "0")
                    self._real_time_enabled = True
                    logger.info("실시간 시세 등록 완료")
        
        except Exception as e:
            logger.error(f"실시간 시세 등록 중 오류 발생: {e}")
    
    def _disable_real_time(self):
        """실시간 시세 해제"""
        try:
            if self.kiwoom and self._real_time_enabled:
                self.kiwoom.set_real_remove("2000", "ALL")
                self._real_time_enabled = False
                logger.info("실시간 시세 해제 완료")
            
        except Exception as e:
            logger.error(f"실시간 시세 해제 중 오류 발생: {e}")
    
    def update_real_time(self, code, price):
        """실시간 현재가 업데이트"""
        try:
            # 해당 종목 행 찾기
            for row in range(self.holdings_table.rowCount()):
                if self.holdings_table.item(row, 0).text() == code:
                    # 현재가 업데이트
                    current_price_item = self.holdings_table.item(row, 4)
                    current_price_item.setText(f"{price:,}")
                    
                    # 보유수량
                    quantity = int(self.holdings_table.item(row, 2).text().replace(',', ''))
                    
                    # 매입가
                    buy_price = int(self.holdings_table.item(row, 3).text().replace(',', ''))
                    
                    # 평가손익 계산
                    profit = (price - buy_price) * quantity
                    profit_item = self.holdings_table.item(row, 5)
                    profit_item.setText(f"{profit:+,}")
                    if profit > 0:
                        profit_item.setForeground(QColor('red'))
                    elif profit < 0:
                        profit_item.setForeground(QColor('blue'))
                    else:
                        profit_item.setForeground(QColor('black'))
                    
                    # 수익률 계산
                    rate = (price / buy_price - 1) * 100
                    rate_item = self.holdings_table.item(row, 6)
                    rate_item.setText(f"{rate:+.2f}%")
                    if rate > 0:
                        rate_item.setForeground(QColor('red'))
                    elif rate < 0:
                        rate_item.setForeground(QColor('blue'))
                    else:
                        rate_item.setForeground(QColor('black'))
                    
                    # 평가금액 계산
                    value = price * quantity
                    value_item = self.holdings_table.item(row, 7)
                    value_item.setText(f"{value:,}")
                    
                    # 합계 재계산
                    self._update_total()
                    break
        
        except Exception as e:
            logger.error(f"실시간 데이터 업데이트 중 오류 발생: {e}")
    
    def _update_total(self):
        """합계 정보 업데이트"""
        try:
            total_value = 0
            total_profit = 0
            
            for row in range(self.holdings_table.rowCount()):
                # 평가금액
                value = int(self.holdings_table.item(row, 7).text().replace(',', ''))
                total_value += value
                
                # 평가손익
                profit = int(self.holdings_table.item(row, 5).text().replace('+', '').replace(',', ''))
                total_profit += profit
            
            # 총평가금액 업데이트
            self.total_value.setText(f"{total_value:,}")
            
            # 총평가손익 업데이트
            self.profit_value.setText(f"{total_profit:+,}")
            if total_profit > 0:
                self.profit_value.setStyleSheet("font-weight: bold; color: red;")
            elif total_profit < 0:
                self.profit_value.setStyleSheet("font-weight: bold; color: blue;")
            else:
                self.profit_value.setStyleSheet("font-weight: bold;")
            
            # 수익률 업데이트
            total_buy = total_value - total_profit
            if total_buy > 0:
                total_yield = (total_value / total_buy - 1) * 100
                self.yield_value.setText(f"{total_yield:+.2f}%")
                if total_yield > 0:
                    self.yield_value.setStyleSheet("font-weight: bold; color: red;")
                elif total_yield < 0:
                    self.yield_value.setStyleSheet("font-weight: bold; color: blue;")
                else:
                    self.yield_value.setStyleSheet("font-weight: bold;")
        
        except Exception as e:
            logger.error(f"합계 정보 업데이트 중 오류 발생: {e}")
    
    def _show_context_menu(self, pos):
        """우클릭 메뉴 표시"""
        row = self.holdings_table.rowAt(pos.y())
        if row >= 0:
            menu = QMenu(self)
            
            # 매도 메뉴
            sell_action = menu.addAction("매도")
            sell_action.triggered.connect(lambda: self._sell_stock(row))
            
            menu.addSeparator()
            
            # 차트 보기
            chart_action = menu.addAction("차트")
            chart_action.triggered.connect(lambda: self._show_chart(row))
            
            # 메뉴 표시
            menu.exec_(QCursor.pos())
    
    def _sell_stock(self, row):
        """매도 주문"""
        try:
            code = self.holdings_table.item(row, 0).text()
            name = self.holdings_table.item(row, 1).text()
            quantity = int(self.holdings_table.item(row, 2).text().replace(',', ''))
            
            # 매도 수량 입력 대화상자
            sell_quantity, ok = QInputDialog.getInt(
                self, "매도 수량", f"{name} 매도 수량을 입력하세요:",
                value=quantity, min=1, max=quantity
            )
            
            if ok:
                # 매도 요청 시그널 발생
                self.sell_requested.emit(code, name, sell_quantity)
        
        except Exception as e:
            logger.error(f"매도 주문 중 오류 발생: {e}")
    
    def _show_chart(self, row):
        """차트 보기"""
        code = self.holdings_table.item(row, 0).text()
        self.chart_requested.emit(code)
    
    def _apply_filter(self, filter_type):
        """필터 적용"""
        try:
            for row in range(self.holdings_table.rowCount()):
                rate = float(self.holdings_table.item(row, 6).text().strip('%'))
                visible = True
                
                if filter_type == "수익" and rate <= 0:
                    visible = False
                elif filter_type == "손실" and rate >= 0:
                    visible = False
                
                self.holdings_table.setRowHidden(row, not visible)
        
        except Exception as e:
            logger.error(f"필터 적용 중 오류 발생: {e}")
    
    def clear(self):
        """패널 초기화"""
        self._disable_real_time()
        self.holdings_table.setRowCount(0)
        self.deposit_value.setText("0")
        self.total_value.setText("0")
        self.profit_value.setText("0")
        self.yield_value.setText("0.00%")
        self.profit_value.setStyleSheet("font-weight: bold;")
        self.yield_value.setStyleSheet("font-weight: bold;")
        self.filter_combo.setCurrentText("전체") 