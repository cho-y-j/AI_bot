"""
관심종목 패널 모듈
"""
import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QMenu, QAction, QMessageBox, QDialog, QInputDialog,
    QListWidget, QListWidgetItem, QLineEdit, QDialogButtonBox, QSplitter
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCursor, QIcon, QColor

logger = logging.getLogger(__name__)

class GroupManageDialog(QDialog):
    """관심종목 그룹 관리 다이얼로그"""
    def __init__(self, parent=None, groups=None):
        super().__init__(parent)
        self.groups = groups or []
        self.init_ui()
        
    def init_ui(self):
        """UI 초기화"""
        self.setWindowTitle("관심종목 그룹 관리")
        self.setMinimumWidth(300)
        
        layout = QVBoxLayout(self)
        
        # 그룹 목록
        self.list_widget = QListWidget()
        self.list_widget.addItems(self.groups)
        layout.addWidget(self.list_widget)
        
        # 버튼 그룹
        btn_layout = QHBoxLayout()
        
        add_btn = QPushButton("추가")
        rename_btn = QPushButton("이름변경")
        delete_btn = QPushButton("삭제")
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(rename_btn)
        btn_layout.addWidget(delete_btn)
        
        layout.addLayout(btn_layout)
        
        # 확인/취소 버튼
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self
        )
        layout.addWidget(buttons)
        
        # 이벤트 연결
        add_btn.clicked.connect(self.add_group)
        rename_btn.clicked.connect(self.rename_group)
        delete_btn.clicked.connect(self.delete_group)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
    def add_group(self):
        """그룹 추가"""
        name, ok = QInputDialog.getText(self, "그룹 추가", "그룹 이름:")
        if ok and name:
            if name in self.groups:
                QMessageBox.warning(self, "오류", "이미 존재하는 그룹 이름입니다.")
                return
            self.list_widget.addItem(name)
            self.groups.append(name)
    
    def rename_group(self):
        """그룹 이름 변경"""
        current = self.list_widget.currentItem()
        if not current:
            return
            
        old_name = current.text()
        new_name, ok = QInputDialog.getText(
            self, "그룹 이름 변경", "새 그룹 이름:", 
            text=old_name
        )
        
        if ok and new_name and new_name != old_name:
            if new_name in self.groups:
                QMessageBox.warning(self, "오류", "이미 존재하는 그룹 이름입니다.")
                return
            idx = self.groups.index(old_name)
            self.groups[idx] = new_name
            current.setText(new_name)
    
    def delete_group(self):
        """그룹 삭제"""
        current = self.list_widget.currentItem()
        if not current:
            return
            
        name = current.text()
        if name == "관심종목1":  # 기본 그룹은 삭제 불가
            QMessageBox.warning(self, "오류", "기본 그룹은 삭제할 수 없습니다.")
            return
            
        reply = QMessageBox.question(
            self, "그룹 삭제", 
            f"'{name}' 그룹을 삭제하시겠습니까?\n(그룹 내 종목도 함께 삭제됩니다)",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.groups.remove(name)
            self.list_widget.takeItem(self.list_widget.row(current))
    
    def get_groups(self):
        """변경된 그룹 목록 반환"""
        return self.groups

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
            logger.info(f"종목 검색 시작: {keyword}")
            
            # 종목 검색 (키움 API 사용)
            stocks = self.kiwoom.search_stock(keyword)
            logger.info(f"검색 결과: {len(stocks)}개 종목")
            
            # 테이블 초기화
            self.result_table.setRowCount(0)
            
            if stocks:
                for stock in stocks:
                    row = self.result_table.rowCount()
                    self.result_table.insertRow(row)
                    
                    # 종목코드
                    code_item = QTableWidgetItem(stock['종목코드'])
                    self.result_table.setItem(row, 0, code_item)
                    
                    # 종목명
                    name_item = QTableWidgetItem(stock['종목명'])
                    self.result_table.setItem(row, 1, name_item)
                    
                    # 시장구분
                    market_item = QTableWidgetItem(stock['시장구분'])
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
        
        # 초기 데이터 로드
        self.update_favorites()
    
    def init_ui(self):
        """UI 초기화"""
        # 메인 레이아웃
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 상단 도구 모음
        tool_layout = QHBoxLayout()
        
        # 그룹 선택
        group_layout = QHBoxLayout()
        self.group_combo = QComboBox()
        self.group_combo.addItems(self.groups)
        
        group_btn = QPushButton("그룹관리")
        group_btn.setToolTip("관심종목 그룹 관리")
        
        group_layout.addWidget(QLabel("관심그룹:"))
        group_layout.addWidget(self.group_combo)
        group_layout.addWidget(group_btn)
        
        # 종목 관리 버튼
        add_btn = QPushButton("추가")
        add_btn.setToolTip("종목 추가")
        
        delete_btn = QPushButton("삭제")
        delete_btn.setToolTip("선택 종목 삭제")
        
        # 레이아웃 구성
        tool_layout.addLayout(group_layout)
        tool_layout.addStretch()
        tool_layout.addWidget(add_btn)
        tool_layout.addWidget(delete_btn)
        
        main_layout.addLayout(tool_layout)
        
        # 관심종목 테이블
        self.favorites_table = QTableWidget()
        self.favorites_table.setColumnCount(7)
        self.favorites_table.setHorizontalHeaderLabels([
            "종목코드", "종목명", "현재가", "전일대비", 
            "등락률", "거래량", "거래대금"
        ])
        
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
        logger.info(f"테이블 더블클릭: row={row}, col={col}")
        self._show_chart(row)
    
    def _show_chart(self, row):
        """차트 보기"""
        code = self.favorites_table.item(row, 0).text()
        name = self.favorites_table.item(row, 1).text()
        logger.info(f"차트 요청: {name}({code})")
        self.chart_requested.emit(code)
    
    def _order_stock(self, row, order_type):
        """주문 요청"""
        code = self.favorites_table.item(row, 0).text()
        name = self.favorites_table.item(row, 1).text()
        self.order_requested.emit(code, name)
    
    def _manage_groups(self):
        """그룹 관리"""
        dialog = GroupManageDialog(self, self.groups.copy())
        if dialog.exec_() == QDialog.Accepted:
            new_groups = dialog.get_groups()
            if new_groups != self.groups:
                # 그룹 목록 업데이트
                current = self.group_combo.currentText()
                self.groups = new_groups
                
                self.group_combo.clear()
                self.group_combo.addItems(self.groups)
                
                # 현재 선택된 그룹이 삭제된 경우 첫 번째 그룹 선택
                if current in self.groups:
                    self.group_combo.setCurrentText(current)
                else:
                    self.group_combo.setCurrentText(self.groups[0])
    
    def _add_stock(self):
        """종목 추가"""
        if not self.kiwoom:
            QMessageBox.warning(self, "오류", "키움 API가 초기화되지 않았습니다.")
            return
        
        dialog = StockSearchDialog(self, self.kiwoom)
        if dialog.exec_() == QDialog.Accepted:
            code, name = dialog.get_selected_stock()
            if code and name:
                try:
                    self.kiwoom.add_favorite(self.current_group, code, name)
                    self.update_favorites()
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
    
    def closeEvent(self, event):
        """패널 종료 시 실시간 데이터 해제"""
        try:
            if self.kiwoom:
                self._disable_real_time()
        except Exception as e:
            logger.error(f"실시간 데이터 해제 중 오류 발생: {e}")
        event.accept() 