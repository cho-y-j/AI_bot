"""
메인 윈도우 모듈
"""
import os
import sys
import logging
import json
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QSplitter, QStatusBar, QAction, QDialog, 
    QMessageBox, QApplication, QPushButton, QToolBar, QMenu,
    QDockWidget, QTabWidget, QInputDialog, QSizePolicy
)
from PyQt5.QtCore import Qt, QSettings, pyqtSlot, QSize, QTimer, QTime
from PyQt5.QtGui import QIcon
from .panels.simple_chart_panel import SimpleChartPanel

logger = logging.getLogger(__name__)

class SettingsDialog(QDialog):
    """설정 다이얼로그"""
    
    def __init__(self, parent=None):
        """
        초기화
        
        Args:
            parent: 부모 위젯
        """
        super().__init__(parent)
        self.parent = parent
        self.settings = parent.settings if parent else QSettings()
        
        # UI 초기화
        self.init_ui()
        
        # 설정값 로드
        self.load_settings()
    
    def init_ui(self):
        """UI 초기화"""
        # 윈도우 설정
        self.setWindowTitle("설정")
        self.setGeometry(300, 300, 400, 300)
        
        # 메인 레이아웃
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # 여기에 설정 UI 추가
        
        # 버튼 레이아웃
        button_layout = QHBoxLayout()
        
        # 확인 버튼
        ok_button = QPushButton("확인")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)
        
        # 취소 버튼
        cancel_button = QPushButton("취소")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        main_layout.addLayout(button_layout)
    
    def load_settings(self):
        """설정값 로드"""
        # 여기에 설정값 로드 로직 추가
        pass
    
    def save_settings(self):
        """설정값 저장"""
        # 여기에 설정값 저장 로직 추가
        pass
    
    def accept(self):
        """확인 버튼 클릭 시"""
        self.save_settings()
        super().accept()

class AccountDialog(QDialog):
    """계좌 정보 다이얼로그"""
    
    def __init__(self, parent=None):
        """
        초기화
        
        Args:
            parent: 부모 위젯
        """
        super().__init__(parent)
        self.parent = parent
        self.kiwoom = parent.kiwoom if parent else None
        
        # UI 초기화
        self.init_ui()
        
        # 계좌 정보 로드
        self.load_account_info()
    
    def init_ui(self):
        """UI 초기화"""
        # 윈도우 설정
        self.setWindowTitle("계좌 정보")
        self.setGeometry(300, 300, 400, 300)
        
        # 메인 레이아웃
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # 계좌 정보 표시
        self.account_label = QLabel("계좌번호: ")
        main_layout.addWidget(self.account_label)
        
        self.balance_label = QLabel("예수금: ")
        main_layout.addWidget(self.balance_label)
        
        self.total_buy_label = QLabel("총매입금액: ")
        main_layout.addWidget(self.total_buy_label)
        
        self.total_eval_label = QLabel("총평가금액: ")
        main_layout.addWidget(self.total_eval_label)
        
        self.total_profit_label = QLabel("총평가손익: ")
        main_layout.addWidget(self.total_profit_label)
        
        # 버튼 레이아웃
        button_layout = QHBoxLayout()
        
        # 확인 버튼
        ok_button = QPushButton("확인")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)
        
        main_layout.addLayout(button_layout)
    
    def load_account_info(self):
        """계좌 정보 로드"""
        if self.kiwoom and self.kiwoom.get_connect_state():
            # 여기에 계좌 정보 로드 로직 추가
            pass

class MainWindow(QMainWindow):
    """메인 윈도우 클래스"""
    
    def __init__(self, kiwoom=None):
        """
        초기화
        
        Args:
            kiwoom: 키움 API 객체
        """
        super().__init__()
        self.kiwoom = kiwoom
        
        # 설정 로드
        self.settings = QSettings('MyCompany', 'MyTrader')
        
        # 대시보드 관련 변수
        self.current_dashboard = "기본 대시보드"
        self.dashboards = {}
        
        # 패널 저장 변수
        self.panels = {}
        
        # 열린 패널 콤보박스 초기화
        self.open_panels_combo = None
        
        try:
            # 메뉴바 생성
            self.create_menu_bar()
            
            # 툴바 생성
            self.create_toolbar()
            
            # UI 초기화
            self.init_ui()
            
            # 대시보드 로드
            self.load_dashboards()
            
            # 로그인 확인
            if self.kiwoom:
                self.check_login()
        except Exception as e:
            logger.error(f"초기화 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
        
    def create_menu_bar(self):
        """메뉴바 생성"""
        menubar = self.menuBar()
    
        # 파일 메뉴
        file_menu = menubar.addMenu("파일")
        
        # 설정 메뉴
        settings_action = QAction("설정", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self.show_settings_dialog)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        # 종료 메뉴
        exit_action = QAction("종료", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 1. 기본 메뉴
        basic_menu = menubar.addMenu("기본 메뉴")
        
        # 차트 보기
        chart_action = QAction("차트 보기", self)
        chart_action.triggered.connect(lambda: self.show_panel("chart"))
        basic_menu.addAction(chart_action)
        
        # 현재가 조회
        current_price_action = QAction("현재가 조회", self)
        current_price_action.triggered.connect(lambda: self.show_panel("current_price"))
        basic_menu.addAction(current_price_action)
        
        # 보유종목
        holdings_action = QAction("보유종목", self)
        holdings_action.triggered.connect(lambda: self.show_panel("holdings"))
        basic_menu.addAction(holdings_action)
        
        # 관심종목
        favorites_action = QAction("관심종목", self)
        favorites_action.triggered.connect(lambda: self.show_panel("favorites"))
        basic_menu.addAction(favorites_action)
        
        # 계좌 보기
        account_action = QAction("계좌 보기", self)
        account_action.triggered.connect(lambda: self.show_panel("account"))
        basic_menu.addAction(account_action)
        
        # 실시간 매매현황
        realtime_trading_action = QAction("실시간 매매현황", self)
        realtime_trading_action.triggered.connect(lambda: self.show_panel("realtime_trading"))
        basic_menu.addAction(realtime_trading_action)
        
        # 거래순위 및 실시간검색어
        ranking_action = QAction("거래순위 및 실시간검색어", self)
        ranking_action.triggered.connect(lambda: self.show_panel("ranking"))
        basic_menu.addAction(ranking_action)
        
        # 거래 내역
        transaction_action = QAction("거래 내역", self)
        transaction_action.triggered.connect(lambda: self.show_panel("transaction"))
        basic_menu.addAction(transaction_action)
        
        # 수익률 분석
        profit_analysis_action = QAction("수익률 분석", self)
        profit_analysis_action.triggered.connect(lambda: self.show_panel("profit_analysis"))
        basic_menu.addAction(profit_analysis_action)
        
        # 로그
        log_action = QAction("로그", self)
        log_action.triggered.connect(lambda: self.show_panel("log"))
        basic_menu.addAction(log_action)
        
        # 2. AI 조건 매매
        ai_condition_menu = menubar.addMenu("AI 조건 매매")
        
        # AI 조건 거래
        ai_condition_trading_action = QAction("AI 조건 거래", self)
        ai_condition_trading_action.triggered.connect(lambda: self.show_panel("ai_condition_trading"))
        ai_condition_menu.addAction(ai_condition_trading_action)
        
        # 자동 거래 설정
        auto_trading_settings_action = QAction("자동 거래 설정", self)
        auto_trading_settings_action.triggered.connect(lambda: self.show_panel("auto_trading_settings"))
        ai_condition_menu.addAction(auto_trading_settings_action)
        
        # 3. AI 자동매매
        ai_auto_menu = menubar.addMenu("AI 자동매매")
        
        # AI 자동거래
        ai_auto_trading_action = QAction("AI 자동거래", self)
        ai_auto_trading_action.triggered.connect(lambda: self.show_panel("ai_auto_trading"))
        ai_auto_menu.addAction(ai_auto_trading_action)
        
        # 설정
        ai_auto_settings_action = QAction("설정", self)
        ai_auto_settings_action.triggered.connect(lambda: self.show_panel("ai_auto_settings"))
        ai_auto_menu.addAction(ai_auto_settings_action)
        
        # 4. AI 검색
        ai_search_menu = menubar.addMenu("AI 검색")
        
        # 실시간 검색 결과
        realtime_search_action = QAction("실시간 검색 결과", self)
        realtime_search_action.triggered.connect(lambda: self.show_panel("realtime_search"))
        ai_search_menu.addAction(realtime_search_action)
        
        # 검색 설정
        search_settings_action = QAction("검색 설정", self)
        search_settings_action.triggered.connect(lambda: self.show_panel("search_settings"))
        ai_search_menu.addAction(search_settings_action)
        
        # 5. AI 종목 분석
        ai_analysis_menu = menubar.addMenu("AI 종목 분석")
        
        # AI 뉴스검색
        ai_news_action = QAction("AI 뉴스검색", self)
        ai_news_action.triggered.connect(lambda: self.show_panel("ai_news"))
        ai_analysis_menu.addAction(ai_news_action)
        
        # AI 종목 분석
        ai_stock_analysis_action = QAction("AI 종목 분석", self)
        ai_stock_analysis_action.triggered.connect(lambda: self.show_panel("ai_stock_analysis"))
        ai_analysis_menu.addAction(ai_stock_analysis_action)
        
        # 6. 설정
        settings_menu = menubar.addMenu("설정")
        
        # 비밀번호 관리
        password_action = QAction("비밀번호 관리", self)
        password_action.triggered.connect(lambda: self.show_panel("password_management"))
        settings_menu.addAction(password_action)
        
        # 알림 설정
        notification_action = QAction("알림 설정", self)
        notification_action.triggered.connect(lambda: self.show_panel("notification_settings"))
        settings_menu.addAction(notification_action)
        
        # 대시보드 메뉴
        dashboard_menu = menubar.addMenu("대시보드")
        
        # 대시보드 저장
        save_dashboard_action = QAction("현재 대시보드 저장", self)
        save_dashboard_action.triggered.connect(self.save_current_dashboard)
        dashboard_menu.addAction(save_dashboard_action)
        
        # 대시보드 다른 이름으로 저장
        save_as_dashboard_action = QAction("대시보드 다른 이름으로 저장", self)
        save_as_dashboard_action.triggered.connect(self.save_dashboard_as)
        dashboard_menu.addAction(save_as_dashboard_action)
        
        dashboard_menu.addSeparator()
        
        # 대시보드 관리
        manage_dashboard_action = QAction("대시보드 관리", self)
        manage_dashboard_action.triggered.connect(self.manage_dashboards)
        dashboard_menu.addAction(manage_dashboard_action)
    
    def create_toolbar(self):
        """툴바 생성"""
        # 메인 툴바
        main_toolbar = QToolBar("메인 툴바")
        main_toolbar.setObjectName("main_toolbar")
        main_toolbar.setMovable(False)
        self.addToolBar(main_toolbar)
        
        # 대시보드 선택 콤보박스
        self.dashboard_combo = QComboBox()
        self.dashboard_combo.setMinimumWidth(150)
        self.dashboard_combo.currentTextChanged.connect(self.on_dashboard_changed)
        main_toolbar.addWidget(QLabel("대시보드: "))
        main_toolbar.addWidget(self.dashboard_combo)
        
        # 대시보드 저장 버튼
        save_dashboard_btn = QPushButton("저장")
        save_dashboard_btn.clicked.connect(self.save_current_dashboard)
        main_toolbar.addWidget(save_dashboard_btn)
        
        main_toolbar.addSeparator()
        
        # 현재 열려있는 패널 목록
        main_toolbar.addWidget(QLabel("열린 패널: "))
        self.open_panels_combo = QComboBox()
        self.open_panels_combo.setMinimumWidth(150)
        self.open_panels_combo.currentTextChanged.connect(self.on_panel_selected)
        main_toolbar.addWidget(self.open_panels_combo)
        
        # 패널 닫기 버튼
        close_panel_btn = QPushButton("패널 닫기")
        close_panel_btn.clicked.connect(self.close_selected_panel)
        main_toolbar.addWidget(close_panel_btn)
        
        main_toolbar.addSeparator()
        
        # 차트 버튼
        chart_action = QAction("차트", self)
        chart_action.triggered.connect(lambda: self.show_panel("chart"))
        main_toolbar.addAction(chart_action)
        
        # 현재가 버튼
        current_price_action = QAction("현재가", self)
        current_price_action.triggered.connect(lambda: self.show_panel("current_price"))
        main_toolbar.addAction(current_price_action)
        
        # 보유종목 버튼
        holdings_action = QAction("보유종목", self)
        holdings_action.triggered.connect(lambda: self.show_panel("holdings"))
        main_toolbar.addAction(holdings_action)
        
        # 관심종목 버튼
        favorites_action = QAction("관심종목", self)
        favorites_action.triggered.connect(lambda: self.show_panel("favorites"))
        main_toolbar.addAction(favorites_action)
        
        try:
            # 스페이서 추가 (우측 정렬을 위해)
            spacer = QWidget()
            spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            main_toolbar.addWidget(spacer)
            
            # 현재 시간 표시
            self.time_label = QLabel()
            self.time_label.setMinimumWidth(80)
            main_toolbar.addWidget(self.time_label)
            
            # 시간 업데이트 타이머
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_time)
            self.timer.start(1000)  # 1초마다 업데이트
            self.update_time()  # 초기 시간 설정
            
            # 로그인 상태 표시
            self.login_status_label = QLabel()
            self.login_status_label.setMinimumWidth(100)
            if self.kiwoom and self.kiwoom.get_connect_state():
                self.login_status_label.setText("로그인 됨")
                self.login_status_label.setStyleSheet("color: green;")
            else:
                self.login_status_label.setText("로그인 필요")
                self.login_status_label.setStyleSheet("color: red;")
            main_toolbar.addWidget(self.login_status_label)
            
            # 나가기 버튼
            exit_btn = QPushButton("나가기")
            exit_btn.clicked.connect(self.close)
            main_toolbar.addWidget(exit_btn)
        except Exception as e:
            logger.error(f"우측 툴바 생성 중 오류 발생: {e}")
    
    def init_ui(self):
        """UI 초기화"""
        # 윈도우 설정
        self.setWindowTitle("트레이딩봇")
        self.setGeometry(100, 100, 1512, 900)
        
        # 중앙 위젯
        self.central_widget = QTabWidget()
        self.setCentralWidget(self.central_widget)
        
        # 상태바
        self.statusBar().showMessage("준비됨")
        
        # 도킹 가능하도록 설정
        self.setDockNestingEnabled(True)
        self.setCorner(Qt.TopLeftCorner, Qt.LeftDockWidgetArea)
        self.setCorner(Qt.TopRightCorner, Qt.RightDockWidgetArea)
        self.setCorner(Qt.BottomLeftCorner, Qt.LeftDockWidgetArea)
        self.setCorner(Qt.BottomRightCorner, Qt.RightDockWidgetArea)
        
        # 도킹 힌트 비활성화 (자유로운 배치를 위해)
        self.setDockOptions(QMainWindow.AnimatedDocks | QMainWindow.AllowNestedDocks | QMainWindow.AllowTabbedDocks)
        
        # 차트 패널 추가 (샘플)
        chart_dock = self.add_chart_panel()
        
        # 열린 패널 목록 업데이트
        self.update_open_panels()
    
    def add_chart_panel(self):
        """차트 패널 추가 (샘플)"""
        # 차트 패널 생성
        chart_panel = SimpleChartPanel(self, self.kiwoom)
        
        # 패널 크기 정책 설정
        chart_panel.setMinimumSize(400, 300)
        chart_panel.setMaximumWidth(800)
        
        # 도킹 위젯으로 추가
        chart_dock = QDockWidget("차트", self)
        chart_dock.setObjectName("chart_dock")
        chart_dock.setWidget(chart_panel)
        
        # 자유로운 배치를 위한 설정
        chart_dock.setAllowedAreas(Qt.NoDockWidgetArea)  # 도킹 영역 제한
        chart_dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetClosable)
        chart_dock.setFloating(True)  # 부유 상태로 시작
        
        # 도킹 위젯 추가
        self.addDockWidget(Qt.RightDockWidgetArea, chart_dock)
        
        # 패널 저장
        self.panels["chart"] = chart_dock
        
        # 샘플 종목 설정
        chart_panel.set_stock("005930", "삼성전자")
        
        # 열린 패널 목록 업데이트
        self.update_open_panels()
        
        return chart_dock
    
    def show_panel(self, panel_name):
        """패널 표시"""
        if panel_name in self.panels:
            # 이미 있는 패널이면 표시
            self.panels[panel_name].show()
            self.panels[panel_name].raise_()
            self.update_open_panels()
        else:
            # 없는 패널이면 생성
            if panel_name == "chart":
                # 차트 패널 생성
                dock = self.add_chart_panel()
                dock.show()
            elif panel_name == "current_price":
                # 현재가 패널 생성 (임시)
                self.create_empty_panel(panel_name, "현재가", Qt.RightDockWidgetArea)
            elif panel_name == "holdings":
                # 보유종목 패널 생성 (임시)
                self.create_empty_panel(panel_name, "보유종목", Qt.LeftDockWidgetArea)
            elif panel_name == "favorites":
                # 관심종목 패널 생성 (임시)
                self.create_empty_panel(panel_name, "관심종목", Qt.LeftDockWidgetArea)
            elif panel_name == "account":
                # 계좌 패널 생성 (임시)
                self.create_empty_panel(panel_name, "계좌", Qt.LeftDockWidgetArea)
            elif panel_name == "realtime_trading":
                # 실시간 매매현황 패널 생성 (임시)
                self.create_empty_panel(panel_name, "실시간 매매현황", Qt.BottomDockWidgetArea)
            elif panel_name == "ranking":
                # 거래순위 패널 생성 (임시)
                self.create_empty_panel(panel_name, "거래순위 및 실시간검색어", Qt.BottomDockWidgetArea)
            elif panel_name == "transaction":
                # 거래내역 패널 생성 (임시)
                self.create_empty_panel(panel_name, "거래내역", Qt.BottomDockWidgetArea)
            elif panel_name == "profit_analysis":
                # 수익률 분석 패널 생성 (임시)
                self.create_empty_panel(panel_name, "수익률 분석", Qt.RightDockWidgetArea)
            elif panel_name == "log":
                # 로그 패널 생성 (임시)
                self.create_empty_panel(panel_name, "로그", Qt.BottomDockWidgetArea)
            elif panel_name == "ai_condition_trading":
                # AI 조건 거래 패널 생성 (임시)
                self.create_empty_panel(panel_name, "AI 조건 거래", Qt.RightDockWidgetArea)
            elif panel_name == "auto_trading_settings":
                # 자동 거래 설정 패널 생성 (임시)
                self.create_empty_panel(panel_name, "자동 거래 설정", Qt.RightDockWidgetArea)
            elif panel_name == "ai_auto_trading":
                # AI 자동거래 패널 생성 (임시)
                self.create_empty_panel(panel_name, "AI 자동거래", Qt.RightDockWidgetArea)
            elif panel_name == "ai_auto_settings":
                # AI 자동거래 설정 패널 생성 (임시)
                self.create_empty_panel(panel_name, "AI 자동거래 설정", Qt.RightDockWidgetArea)
            elif panel_name == "realtime_search":
                # 실시간 검색 결과 패널 생성 (임시)
                self.create_empty_panel(panel_name, "실시간 검색 결과", Qt.RightDockWidgetArea)
            elif panel_name == "search_settings":
                # 검색 설정 패널 생성 (임시)
                self.create_empty_panel(panel_name, "검색 설정", Qt.RightDockWidgetArea)
            elif panel_name == "ai_news":
                # AI 뉴스검색 패널 생성 (임시)
                self.create_empty_panel(panel_name, "AI 뉴스검색", Qt.RightDockWidgetArea)
            elif panel_name == "ai_stock_analysis":
                # AI 종목 분석 패널 생성 (임시)
                self.create_empty_panel(panel_name, "AI 종목 분석", Qt.RightDockWidgetArea)
            elif panel_name == "password_management":
                # 비밀번호 관리 패널 생성 (임시)
                self.create_empty_panel(panel_name, "비밀번호 관리", Qt.RightDockWidgetArea)
            elif panel_name == "notification_settings":
                # 알림 설정 패널 생성 (임시)
                self.create_empty_panel(panel_name, "알림 설정", Qt.RightDockWidgetArea)
            else:
                # 없는 패널이면 메시지 표시
                QMessageBox.information(self, "알림", f"{panel_name} 패널은 아직 구현되지 않았습니다.")
    
    def create_empty_panel(self, panel_name, title, area=Qt.RightDockWidgetArea):
        """빈 패널 생성 (임시)"""
        # 임시 위젯 생성
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 패널 제목 라벨
        label = QLabel(f"{title} 패널 (개발 중)")
        label.setStyleSheet("font-size: 16pt; color: gray;")
        layout.addWidget(label)
        
        # 도킹 위젯으로 추가
        dock = QDockWidget(title, self)
        dock.setObjectName(f"{panel_name}_dock")
        dock.setWidget(widget)
        
        # 자유로운 배치를 위한 설정
        dock.setAllowedAreas(Qt.NoDockWidgetArea)  # 도킹 영역 제한
        dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetClosable)
        dock.setFloating(True)  # 부유 상태로 시작
        
        # 크기 설정
        widget.setMinimumSize(300, 200)
        
        # 도킹 위젯 추가 (영역 지정 없이)
        self.addDockWidget(area, dock)
        
        # 패널 저장
        self.panels[panel_name] = dock
        
        # 열린 패널 목록 업데이트
        self.update_open_panels()
        
        return dock
    
    def load_dashboards(self):
        """저장된 대시보드 로드"""
        # 저장된 대시보드 목록 로드
        dashboard_list = self.settings.value("dashboards/list", [])
        
        # 기본 대시보드 추가
        if "기본 대시보드" not in dashboard_list:
            dashboard_list.append("기본 대시보드")
        
        # 콤보박스에 추가
        self.dashboard_combo.clear()
        self.dashboard_combo.addItems(dashboard_list)
        
        # 마지막 사용 대시보드 선택
        last_dashboard = self.settings.value("dashboards/last", "기본 대시보드")
        if last_dashboard in dashboard_list:
            self.dashboard_combo.setCurrentText(last_dashboard)
            self.load_dashboard(last_dashboard)
        else:
            self.dashboard_combo.setCurrentText("기본 대시보드")
            
            # 기본 대시보드 로드 (모든 패널 숨기기)
            for panel in self.panels.values():
                panel.hide()
            
            # 기본 패널만 표시
            if "chart" in self.panels:
                self.panels["chart"].show()
            
            self.current_dashboard = "기본 대시보드"
            
            # 열린 패널 목록 업데이트
            self.update_open_panels()
    
    def load_dashboard(self, name):
        """대시보드 로드"""
        self.current_dashboard = name
        
        # 먼저 모든 패널 숨기기
        for panel in self.panels.values():
            panel.hide()
        
        # 대시보드 설정 로드
        dashboard_state = self.settings.value(f"dashboards/{name}/state")
        if dashboard_state:
            self.restoreState(dashboard_state)
        
        # 대시보드 패널 표시 상태 로드
        panels_state = self.settings.value(f"dashboards/{name}/panels", {})
        for panel_name, visible in panels_state.items():
            if panel_name in self.panels and visible:
                self.panels[panel_name].show()
        
        # 열린 패널 목록 업데이트
        self.update_open_panels()
    
    def save_dashboard(self, name):
        """대시보드 저장"""
        # 대시보드 목록 업데이트
        dashboard_list = self.settings.value("dashboards/list", [])
        if name not in dashboard_list:
            dashboard_list.append(name)
            self.settings.setValue("dashboards/list", dashboard_list)
            self.dashboard_combo.addItem(name)
        
        # 현재 상태 저장
        self.settings.setValue(f"dashboards/{name}/state", self.saveState())
        
        # 패널 표시 상태 저장 (열려있는 패널만)
        panels_state = {}
        for panel_name, panel in self.panels.items():
            # 열려있는 패널만 True로 저장
            panels_state[panel_name] = panel.isVisible()
        
        self.settings.setValue(f"dashboards/{name}/panels", panels_state)
        
        # 마지막 사용 대시보드 저장
        self.settings.setValue("dashboards/last", name)
        
        # 메시지 표시
        self.statusBar().showMessage(f"대시보드 '{name}' 저장 완료")
    
    def save_current_dashboard(self):
        """현재 대시보드 저장"""
        self.save_dashboard(self.current_dashboard)
    
    def save_dashboard_as(self):
        """대시보드 다른 이름으로 저장"""
        name, ok = QInputDialog.getText(self, "대시보드 저장", "대시보드 이름:")
        if ok and name:
            self.current_dashboard = name
            self.dashboard_combo.setCurrentText(name)
            self.save_dashboard(name)
    
    def manage_dashboards(self):
        """대시보드 관리"""
        # 대시보드 관리 다이얼로그 표시 (미구현)
        QMessageBox.information(self, "알림", "대시보드 관리 기능은 아직 구현되지 않았습니다.")
    
    def on_dashboard_changed(self, name):
        """대시보드 변경 이벤트"""
        if name and name != self.current_dashboard:
            self.load_dashboard(name)
    
    def check_login(self):
        """로그인 상태 확인"""
        try:
            if not self.kiwoom.get_connect_state():
                QMessageBox.warning(self, "로그인 필요", "키움증권 로그인이 필요합니다.")
                return
            
            # 계좌 목록 설정
            accounts = self.kiwoom.get_login_info("ACCNO").split(';')
            accounts = [acc for acc in accounts if acc.strip()]
            
            if accounts:
                # 상태바에 계좌 정보 표시
                self.statusBar().showMessage(f"로그인 성공 - 계좌: {accounts[0]}")
                logger.info(f"계좌 목록 로드 완료: {len(accounts)}개")
            else:
                logger.warning("사용 가능한 계좌가 없습니다.")
        
        except Exception as e:
            logger.error(f"로그인 상태 확인 중 오류 발생: {e}")
    
    def closeEvent(self, event):
        """
        윈도우 종료 이벤트
        
        Args:
            event: 이벤트 객체
        """
        # 현재 대시보드 저장
        self.save_current_dashboard()
        
        # 윈도우 상태 저장
        self.settings.setValue('window/geometry', self.saveGeometry())
        self.settings.setValue('window/state', self.saveState())
        
        # 이벤트 수락
        event.accept()

    def show_settings_dialog(self):
        """설정 다이얼로그 표시"""
        QMessageBox.information(self, "알림", "설정 기능은 아직 구현되지 않았습니다.")
    
    def show_login_dialog(self):
        """로그인 다이얼로그 표시"""
        if self.kiwoom:
            if not self.kiwoom.get_connect_state():
                self.kiwoom.comm_connect()
            else:
                QMessageBox.information(self, "알림", "이미 로그인되어 있습니다.")
    
    def show_account_dialog(self):
        """계좌 정보 다이얼로그 표시"""
        QMessageBox.information(self, "알림", "계좌 정보 기능은 아직 구현되지 않았습니다.")
    
    def update_time(self):
        """현재 시간 업데이트"""
        current_time = QTime.currentTime()
        self.time_label.setText(current_time.toString("HH:mm:ss"))
    
    def update_open_panels(self):
        """열린 패널 목록 업데이트"""
        if self.open_panels_combo is None:
            return
            
        self.open_panels_combo.clear()
        
        # 열린 패널만 추가
        open_panels = []
        for name, panel in self.panels.items():
            if panel.isVisible():
                open_panels.append(name)
        
        self.open_panels_combo.addItems(open_panels)
    
    def on_panel_selected(self, panel_name):
        """패널 선택 이벤트"""
        if panel_name in self.panels:
            self.panels[panel_name].raise_()
    
    def close_selected_panel(self):
        """선택된 패널 닫기"""
        panel_name = self.open_panels_combo.currentText()
        if panel_name in self.panels:
            self.panels[panel_name].hide()
            self.update_open_panels() 