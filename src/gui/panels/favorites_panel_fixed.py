"""
관심종목 패널 모듈
"""
import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QMenu, QAction, QMessageBox, QDialog, QInputDialog
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
        self.parent = parent
        
        # 관심종목 그룹
        self.groups = ["관심종목1", "관심종목2", "관심종목3"]
        self.current_group = self.groups[0]
        
        # 실시간 조회 종목 목록
        self.real_time_codes = []
        
        # UI 초기화
        self.init_ui()
    
    def init_ui(self):
        """UI 초기화"""
        # 메인 레이아웃
        main_layout = QVBoxLayout(self)
        
        # 상단 그룹 콤보박스
        group_layout = QHBoxLayout()
        self.group_combo = QComboBox()
        self.group_combo.addItems(self.groups)
        
        # 그룹 관리, 종목 추가/삭제 버튼
        group_btn = QPushButton("그룹관리")
        add_btn = QPushButton("추가")
        delete_btn = QPushButton("삭제")
        
        group_layout.addWidget(QLabel("관심그룹:"))
        group_layout.addWidget(self.group_combo)
        group_layout.addWidget(group_btn)
        group_layout.addStretch()
        group_layout.addWidget(add_btn)
        group_layout.addWidget(delete_btn)
        
        main_layout.addLayout(group_layout)
        
        # 관심종목 테이블
        self.favorites_table = QTableWidget()
        self.favorites_table.setColumnCount(7)
        self.favorites_table.setHorizontalHeaderLabels(["종목코드", "종목명", "현재가", "전일대비", "등락률", "거래량", "거래대금"])
        
        # 테이블 설정
        self.favorites_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.favorites_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.favorites_table.setAlternatingRowColors(True)
        self.favorites_table.verticalHeader().setVisible(False)
        self.favorites_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.favorites_table.setContextMenuPolicy(Qt.CustomContextMenu)
        
        main_layout.addWidget(self.favorites_table)
        
        # 이벤트 연결
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
                    current_price = int(stock.get('현재가', 0))
                    current_price_item = QTableWidgetItem(f"{current_price:,}")
                    current_price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    
                    # 가격 상승/하락에 따라 색상 설정
                    diff = int(stock.get('전일대비', 0))
                    if diff > 0:
                        current_price_item.setForeground(Qt.red)
                    elif diff < 0:
                        current_price_item.setForeground(Qt.blue)
                    
                    self.favorites_table.setItem(row, 2, current_price_item)
                    
                    # 전일대비
                    diff_item = QTableWidgetItem(f"{diff:,}")
                    diff_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    
                    if diff > 0:
                        diff_item.setText(f"+{diff:,}")
                        diff_item.setForeground(Qt.red)
                    elif diff < 0:
                        diff_item.setForeground(Qt.blue)
                    
                    self.favorites_table.setItem(row, 3, diff_item)
                    
                    # 등락률
                    diff_percent = float(stock.get('등락률', 0))
                    diff_percent_item = QTableWidgetItem(f"{diff_percent:.2f}%")
                    diff_percent_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    
                    if diff_percent > 0:
                        diff_percent_item.setText(f"+{diff_percent:.2f}%")
                        diff_percent_item.setForeground(Qt.red)
                    elif diff_percent < 0:
                        diff_percent_item.setForeground(Qt.blue)
                    
                    self.favorites_table.setItem(row, 4, diff_percent_item)
                    
                    # 거래량
                    volume = int(stock.get('거래량', 0))
                    volume_item = QTableWidgetItem(f"{volume:,}")
                    volume_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    self.favorites_table.setItem(row, 5, volume_item)
                    
                    # 거래대금
                    amount = int(stock.get('거래대금', 0))
                    amount_item = QTableWidgetItem(f"{amount:,}")
                    amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    self.favorites_table.setItem(row, 6, amount_item)
            
            # 실시간 등록
            self._enable_real_time()
            
        except Exception as e:
            logger.error(f"관심종목 업데이트 중 오류 발생: {e}")
    
    def _enable_real_time(self):
        """실시간 시세 등록"""
        if not self.kiwoom:
            return
        
        # 기존 실시간 해제
        self._disable_real_time()
        
        # 현재 관심종목 추출
        self.real_time_codes = []
        for row in range(self.favorites_table.rowCount()):
            code = self.favorites_table.item(row, 0).text()
            self.real_time_codes.append(code)
        
        # 실시간 시세 등록
        if self.real_time_codes:
            self.kiwoom.set_real_time_data(self.real_time_codes, ["주식시세", "주식체결"])
    
    def _disable_real_time(self):
        """실시간 시세 해제"""
        if not self.kiwoom or not self.real_time_codes:
            return
        
        # 기존 실시간 해제
        self.kiwoom.disset_real_time_data(self.real_time_codes)
        self.real_time_codes = []
    
    def _show_context_menu(self, pos):
        """컨텍스트 메뉴 표시"""
        row = self.favorites_table.currentRow()
        if row < 0:
            return
        
        menu = QMenu(self)
        
        chart_action = QAction("차트보기", self)
        buy_action = QAction("매수주문", self)
        sell_action = QAction("매도주문", self)
        delete_action = QAction("삭제", self)
        
        menu.addAction(chart_action)
        menu.addSeparator()
        menu.addAction(buy_action)
        menu.addAction(sell_action)
        menu.addSeparator()
        menu.addAction(delete_action)
        
        # 이벤트 연결
        chart_action.triggered.connect(lambda: self._show_chart(row))
        buy_action.triggered.connect(lambda: self._order_stock(row, "매수"))
        sell_action.triggered.connect(lambda: self._order_stock(row, "매도"))
        delete_action.triggered.connect(lambda: self._delete_stock(row))
        
        # 팝업 메뉴 표시
        menu.exec_(QCursor.pos())
    
    def _on_table_double_clicked(self, row, col):
        """테이블 더블클릭 이벤트"""
        self._show_chart(row)
    
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
        # 그룹 관리 대화상자 표시
        pass
    
    def _add_stock(self):
        """종목 추가"""
        if not self.kiwoom:
            QMessageBox.warning(self, "오류", "키움 API가 초기화되지 않았습니다.")
            return
        
        # 종목 검색 대화상자 표시
        code, ok = QInputDialog.getText(self, "종목 추가", "종목코드 입력:")
        if ok and code:
            try:
                name = self.kiwoom.get_stock_name(code)
                if name:
                    self.kiwoom.add_favorite(self.current_group, code, name)
                    self.update_favorites()
                else:
                    QMessageBox.warning(self, "오류", "유효하지 않은 종목코드입니다.")
            except Exception as e:
                QMessageBox.warning(self, "오류", f"종목 추가 중 오류 발생: {e}")
    
    def _delete_stock(self, row):
        """종목 삭제"""
        if not self.kiwoom:
            return
        
        code = self.favorites_table.item(row, 0).text()
        name = self.favorites_table.item(row, 1).text()
        
        reply = QMessageBox.question(
            self, 
            "관심종목 삭제", 
            f"{name}({code})을 관심종목에서 삭제하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.kiwoom.remove_favorite(self.current_group, code)
                self.update_favorites()
            except Exception as e:
                QMessageBox.warning(self, "오류", f"종목 삭제 중 오류 발생: {e}")
    
    def _delete_selected(self):
        """선택된 종목 삭제"""
        rows = set()
        for item in self.favorites_table.selectedItems():
            rows.add(item.row())
        
        if not rows:
            return
        
        codes = []
        names = []
        for row in rows:
            code = self.favorites_table.item(row, 0).text()
            name = self.favorites_table.item(row, 1).text()
            codes.append(code)
            names.append(name)
        
        # 삭제 확인
        if len(codes) == 1:
            message = f"{names[0]}({codes[0]})을 관심종목에서 삭제하시겠습니까?"
        else:
            message = f"선택한 {len(codes)}개 종목을 관심종목에서 삭제하시겠습니까?"
        
        reply = QMessageBox.question(
            self, 
            "관심종목 삭제", 
            message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                for code in codes:
                    self.kiwoom.remove_favorite(self.current_group, code)
                self.update_favorites()
            except Exception as e:
                QMessageBox.warning(self, "오류", f"종목 삭제 중 오류 발생: {e}")
    
    def _on_group_changed(self, group):
        """그룹 변경 이벤트"""
        self.current_group = group
        self.update_favorites()
    
    def update_real_time(self, code, real_type, data):
        """실시간 데이터 업데이트"""
        if not self.kiwoom or not code or not data:
            return
        
        # 해당 종목 찾기
        for row in range(self.favorites_table.rowCount()):
            item_code = self.favorites_table.item(row, 0).text()
            if item_code == code:
                # 현재가
                if '현재가' in data:
                    current_price = abs(int(data['현재가']))
                    current_price_item = QTableWidgetItem(f"{current_price:,}")
                    current_price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    
                    # 전일대비
                    diff = 0
                    if '전일대비' in data:
                        diff = int(data['전일대비'])
                    
                    if diff > 0:
                        current_price_item.setForeground(Qt.red)
                    elif diff < 0:
                        current_price_item.setForeground(Qt.blue)
                    
                    self.favorites_table.setItem(row, 2, current_price_item)
                    
                    # 전일대비
                    diff_item = QTableWidgetItem(f"{diff:,}")
                    diff_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    
                    if diff > 0:
                        diff_item.setText(f"+{diff:,}")
                        diff_item.setForeground(Qt.red)
                    elif diff < 0:
                        diff_item.setForeground(Qt.blue)
                    
                    self.favorites_table.setItem(row, 3, diff_item)
                    
                    # 등락률
                    diff_percent = 0
                    if '등락율' in data:
                        diff_percent = float(data['등락율'])
                    
                    diff_percent_item = QTableWidgetItem(f"{diff_percent:.2f}%")
                    diff_percent_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    
                    if diff_percent > 0:
                        diff_percent_item.setText(f"+{diff_percent:.2f}%")
                        diff_percent_item.setForeground(Qt.red)
                    elif diff_percent < 0:
                        diff_percent_item.setForeground(Qt.blue)
                    
                    self.favorites_table.setItem(row, 4, diff_percent_item)
                
                # 거래량
                if '거래량' in data:
                    volume = int(data['거래량'])
                    volume_item = QTableWidgetItem(f"{volume:,}")
                    volume_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    self.favorites_table.setItem(row, 5, volume_item)
                
                # 거래대금
                if '거래대금' in data:
                    amount = int(data['거래대금'])
                    amount_item = QTableWidgetItem(f"{amount:,}")
                    amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    self.favorites_table.setItem(row, 6, amount_item)
                
                break
    
    def clear(self):
        """패널 정리"""
        # 실시간 시세 해제
        self._disable_real_time()
        
        # 테이블 초기화
        self.favorites_table.setRowCount(0) 