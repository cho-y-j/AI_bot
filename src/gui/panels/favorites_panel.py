"""
관심종목 패널
"""
import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMenu, QComboBox, QMessageBox,
    QInputDialog
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCursor

logger = logging.getLogger(__name__)

class FavoritesPanel(QWidget):
    """관심종목 패널 클래스"""
    
    # 시그널 정의
    stock_selected = pyqtSignal(str, str)  # 종목 선택 시그널 (종목코드, 종목명)
    chart_requested = pyqtSignal(str)  # 차트 요청 시그널 (종목코드)
    order_requested = pyqtSignal(str, str)  # 주문 요청 시그널 (종목코드, 종목명)
    
    def __init__(self, parent=None, kiwoom=None):
        super().__init__(parent)
        self.kiwoom = kiwoom
        self.current_group = "관심종목"
        
        # UI 초기화
        self.init_ui()
        
        # 실시간 시세 등록 플래그
        self._real_time_enabled = False
    
    def init_ui(self):
        """UI 초기화"""
        # 메인 레이아웃
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # 상단 영역
        top_layout = QHBoxLayout()
        
        # 그룹 선택 콤보박스
        self.group_combo = QComboBox()
        self.group_combo.addItem("관심종목")
        top_layout.addWidget(self.group_combo)
        
        # 그룹 관리 버튼
        group_btn = QPushButton("그룹관리")
        group_btn.setFixedWidth(80)
        top_layout.addWidget(group_btn)
        
        # 새로고침 버튼
        self.refresh_btn = QPushButton("새로고침")
        self.refresh_btn.setFixedWidth(80)
        top_layout.addWidget(self.refresh_btn)
        
        main_layout.addLayout(top_layout)
        
        # 관심종목 테이블
        self.favorites_table = QTableWidget()
        self.favorites_table.setColumnCount(7)
        self.favorites_table.setHorizontalHeaderLabels([
            "종목코드", "종목명", "현재가", "전일대비", 
            "등락률", "거래량", "거래대금"
        ])
        
        # 테이블 설정
        header = self.favorites_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # 종목명 열은 늘어나도록
        self.favorites_table.setEditTriggers(QTableWidget.NoEditTriggers)  # 편집 불가
        self.favorites_table.setSelectionBehavior(QTableWidget.SelectRows)  # 행 단위 선택
        self.favorites_table.setContextMenuPolicy(Qt.CustomContextMenu)  # 우클릭 메뉴 활성화
        
        main_layout.addWidget(self.favorites_table)
        
        # 하단 버튼 영역
        bottom_layout = QHBoxLayout()
        
        # 종목 추가 버튼
        add_btn = QPushButton("종목 추가")
        add_btn.setFixedWidth(100)
        bottom_layout.addWidget(add_btn)
        
        # 선택 종목 삭제 버튼
        delete_btn = QPushButton("선택 삭제")
        delete_btn.setFixedWidth(100)
        bottom_layout.addWidget(delete_btn)
        
        bottom_layout.addStretch()
        
        main_layout.addLayout(bottom_layout)
        
        # 시그널 연결
        self.refresh_btn.clicked.connect(self.update_favorites)
        self.favorites_table.customContextMenuRequested.connect(self._show_context_menu)
        self.favorites_table.cellDoubleClicked.connect(self._on_table_double_clicked)
        group_btn.clicked.connect(self._manage_groups)
        add_btn.clicked.connect(self._add_stock)
        delete_btn.clicked.connect(self._delete_selected)
        self.group_combo.currentTextChanged.connect(self._on_group_changed)
    
    def update_favorites(self):
        """관심종목 정보 업데이트"""
        try:
            if not self.kiwoom:
                logger.warning("키움 API가 초기화되지 않았습니다.")
                return
            
            # 관심종목 조회
            favorites = self.kiwoom.get_favorites(self.current_group)
            
            # 테이블 초기화
            self.favorites_table.setRowCount(0)
            
            if favorites:
                for stock in favorites:
            row = self.favorites_table.rowCount()
            self.favorites_table.insertRow(row)
                    
                    # 종목코드
                    code_item = QTableWidgetItem(stock['종목코드'])
                    self.favorites_table.setItem(row, 0, code_item)
                    
                    # 종목명
                    name_item = QTableWidgetItem(stock['종목명'])
                    self.favorites_table.setItem(row, 1, name_item)
                    
                    # 현재가
                    price = int(stock['현재가'])
                    price_item = QTableWidgetItem(f"{abs(price):,}")
                    price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    if price > 0:
                        price_item.setForeground(Qt.red)
                    elif price < 0:
                        price_item.setForeground(Qt.blue)
                    self.favorites_table.setItem(row, 2, price_item)
            
            # 전일대비
                    change = int(stock['전일대비'])
                    change_item = QTableWidgetItem(f"{abs(change):,}")
                    change_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    if change > 0:
                        change_item.setForeground(Qt.red)
                        change_item.setText(f"+{change_item.text()}")
                    elif change < 0:
                        change_item.setForeground(Qt.blue)
                        change_item.setText(f"-{change_item.text()}")
                    self.favorites_table.setItem(row, 3, change_item)
                    
                    # 등락률
                    rate = float(stock['등락률'])
                    rate_item = QTableWidgetItem(f"{rate:+.2f}%")
            rate_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if rate > 0:
                rate_item.setForeground(Qt.red)
            elif rate < 0:
                rate_item.setForeground(Qt.blue)
                    self.favorites_table.setItem(row, 4, rate_item)
            
            # 거래량
                    volume = int(stock['거래량'])
            volume_item = QTableWidgetItem(f"{volume:,}")
            volume_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    self.favorites_table.setItem(row, 5, volume_item)
                    
                    # 거래대금
                    value = int(stock['거래대금'])
                    value_item = QTableWidgetItem(f"{value:,}")
                    value_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    self.favorites_table.setItem(row, 6, value_item)
                
                logger.info(f"관심종목 업데이트 완료: {len(favorites)}종목")
                
                # 실시간 시세 등록
                if not self._real_time_enabled:
                    self._enable_real_time()
            else:
                logger.info("관심종목이 없습니다.")
        
        except Exception as e:
            logger.error(f"관심종목 업데이트 중 오류 발생: {e}")
    
    def _enable_real_time(self):
        """실시간 시세 등록"""
        try:
            if self.kiwoom and not self._real_time_enabled:
                # 실시간 시세 등록
                codes = []
                for row in range(self.favorites_table.rowCount()):
                    code = self.favorites_table.item(row, 0).text()
                    codes.append(code)
                
                if codes:
                    self.kiwoom.set_real_reg("9999", codes, "10;11;12;15;13;14", "0")
                    self._real_time_enabled = True
                    logger.info("실시간 시세 등록 완료")
        
        except Exception as e:
            logger.error(f"실시간 시세 등록 중 오류 발생: {e}")
    
    def _disable_real_time(self):
        """실시간 시세 해제"""
        try:
            if self.kiwoom and self._real_time_enabled:
                self.kiwoom.set_real_remove("9999", "ALL")
                self._real_time_enabled = False
                logger.info("실시간 시세 해제 완료")
        
        except Exception as e:
            logger.error(f"실시간 시세 해제 중 오류 발생: {e}")
    
    def _show_context_menu(self, pos):
        """우클릭 메뉴 표시"""
        row = self.favorites_table.rowAt(pos.y())
        if row >= 0:
            menu = QMenu(self)
            
            # 매수 주문
            buy_action = menu.addAction("매수")
            buy_action.triggered.connect(lambda: self._order_stock(row, "매수"))
            
            # 매도 주문
            sell_action = menu.addAction("매도")
            sell_action.triggered.connect(lambda: self._order_stock(row, "매도"))
            
            menu.addSeparator()
            
            # 차트 보기
            chart_action = menu.addAction("차트")
            chart_action.triggered.connect(lambda: self._show_chart(row))
            
            # 종목 삭제
            delete_action = menu.addAction("삭제")
            delete_action.triggered.connect(lambda: self._delete_stock(row))
            
            # 메뉴 표시
            menu.exec_(QCursor.pos())
    
    def _on_table_double_clicked(self, row, col):
        """테이블 더블 클릭 이벤트"""
        code = self.favorites_table.item(row, 0).text()
        name = self.favorites_table.item(row, 1).text()
        self.stock_selected.emit(code, name)
    
    def _show_chart(self, row):
        """차트 보기"""
        code = self.favorites_table.item(row, 0).text()
        self.chart_requested.emit(code)
    
    def _order_stock(self, row, order_type):
        """주문 요청"""
        code = self.favorites_table.item(row, 0).text()
        name = self.favorites_table.item(row, 1).text()
        self.order_requested.emit(code, name)
    
    def _manage_groups(self):
        """그룹 관리"""
        if self.kiwoom:
            groups = self.kiwoom.get_favorite_groups()
            # TODO: 그룹 관리 다이얼로그 구현
            pass
    
    def _add_stock(self):
        """종목 추가"""
        if self.kiwoom:
            code, ok = QInputDialog.getText(self, "종목 추가", "종목코드를 입력하세요:")
            if ok and code:
                # 종목코드 유효성 검사
                name = self.kiwoom.get_master_code_name(code)
                if name:
                    # 관심종목 추가
                    self.kiwoom.add_favorite(self.current_group, code)
                    self.update_favorites()
                else:
                    QMessageBox.warning(self, "오류", "유효하지 않은 종목코드입니다.")
    
    def _delete_stock(self, row):
        """종목 삭제"""
        if self.kiwoom:
            code = self.favorites_table.item(row, 0).text()
            name = self.favorites_table.item(row, 1).text()
            
            reply = QMessageBox.question(
                self, "종목 삭제",
                f"{name}을(를) 관심종목에서 삭제하시겠습니까?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.kiwoom.remove_favorite(self.current_group, code)
                self.update_favorites()
    
    def _delete_selected(self):
        """선택된 종목 삭제"""
        if self.kiwoom:
            selected = self.favorites_table.selectedItems()
            if not selected:
                return
            
            rows = set()
            for item in selected:
                rows.add(item.row())
            
            codes = []
            names = []
            for row in rows:
                codes.append(self.favorites_table.item(row, 0).text())
                names.append(self.favorites_table.item(row, 1).text())
            
            if codes:
                reply = QMessageBox.question(
                    self, "종목 삭제",
                    f"선택한 {len(codes)}개 종목을 관심종목에서 삭제하시겠습니까?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    for code in codes:
                        self.kiwoom.remove_favorite(self.current_group, code)
                    self.update_favorites()
    
    def _on_group_changed(self, group):
        """그룹 변경 시 처리"""
        self.current_group = group
        self._disable_real_time()
        self.update_favorites()
    
    def update_real_time(self, code, real_type, data):
        """실시간 데이터 업데이트"""
        try:
            # 해당 종목 행 찾기
            for row in range(self.favorites_table.rowCount()):
                if self.favorites_table.item(row, 0).text() == code:
                    # 현재가
                    if real_type == "현재가":
                        price = int(data['현재가'])
                        price_item = self.favorites_table.item(row, 2)
                        price_item.setText(f"{abs(price):,}")
                        if price > 0:
                            price_item.setForeground(Qt.red)
                        elif price < 0:
                            price_item.setForeground(Qt.blue)
                    
                    # 전일대비
                    elif real_type == "전일대비":
                        change = int(data['전일대비'])
                        change_item = self.favorites_table.item(row, 3)
                        if change > 0:
                            change_item.setText(f"+{abs(change):,}")
                            change_item.setForeground(Qt.red)
                        elif change < 0:
                            change_item.setText(f"-{abs(change):,}")
                            change_item.setForeground(Qt.blue)
                        else:
                            change_item.setText("0")
                            change_item.setForeground(Qt.black)
                    
                    # 등락률
                    elif real_type == "등락률":
                        rate = float(data['등락률'])
                        rate_item = self.favorites_table.item(row, 4)
                        rate_item.setText(f"{rate:+.2f}%")
                        if rate > 0:
                            rate_item.setForeground(Qt.red)
                        elif rate < 0:
                            rate_item.setForeground(Qt.blue)
                        else:
                            rate_item.setForeground(Qt.black)
                    
                    # 거래량
                    elif real_type == "거래량":
                        volume = int(data['거래량'])
                        volume_item = self.favorites_table.item(row, 5)
                        volume_item.setText(f"{volume:,}")
                    
                    # 거래대금
                    elif real_type == "거래대금":
                        value = int(data['거래대금'])
                        value_item = self.favorites_table.item(row, 6)
                        value_item.setText(f"{value:,}")
                    
                    break
        
        except Exception as e:
            logger.error(f"실시간 데이터 업데이트 중 오류 발생: {e}")
    
    def clear(self):
        """패널 초기화"""
        self._disable_real_time()
        self.favorites_table.setRowCount(0)
        self.current_group = "관심종목"
        self.group_combo.setCurrentText(self.current_group) 