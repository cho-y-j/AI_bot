"""
계좌 정보 패널
"""
import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QPushButton, QGridLayout, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal

logger = logging.getLogger(__name__)

class AccountPanel(QWidget):
    """계좌 정보 패널 클래스"""
    
    # 시그널 정의
    account_changed = pyqtSignal(str)  # 계좌 변경 시그널
    refresh_requested = pyqtSignal()   # 새로고침 요청 시그널
    
    def __init__(self, parent=None, kiwoom=None):
        super().__init__(parent)
        self.kiwoom = kiwoom
        
        # UI 초기화
        self.init_ui()
        
        # 데이터 초기화
        self.update_account_list()
    
    def init_ui(self):
        """UI 초기화"""
        # 메인 레이아웃
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # 상단 영역 (계좌 선택)
        top_layout = QHBoxLayout()
        
        # 계좌 선택 영역
        account_layout = QHBoxLayout()
        account_label = QLabel("계좌:")
        self.account_combo = QComboBox()
        self.account_combo.setFixedWidth(150)
        self.refresh_btn = QPushButton("새로고침")
        self.refresh_btn.setFixedWidth(80)
        
        account_layout.addWidget(account_label)
        account_layout.addWidget(self.account_combo)
        account_layout.addWidget(self.refresh_btn)
        account_layout.addStretch()
        
        top_layout.addLayout(account_layout)
        main_layout.addLayout(top_layout)
        
        # 구분선
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)
        
        # 계좌 정보 그리드
        info_layout = QGridLayout()
        
        # 예수금 정보
        self.deposit_label = QLabel("예수금:")
        self.deposit_value = QLabel("0")
        self.deposit_value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        info_layout.addWidget(self.deposit_label, 0, 0)
        info_layout.addWidget(self.deposit_value, 0, 1)
        
        # 평가금액
        self.eval_balance_label = QLabel("평가금액:")
        self.eval_balance_value = QLabel("0")
        self.eval_balance_value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        info_layout.addWidget(self.eval_balance_label, 0, 2)
        info_layout.addWidget(self.eval_balance_value, 0, 3)
        
        # 매입금액
        self.purchase_amount_label = QLabel("매입금액:")
        self.purchase_amount_value = QLabel("0")
        self.purchase_amount_value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        info_layout.addWidget(self.purchase_amount_label, 1, 0)
        info_layout.addWidget(self.purchase_amount_value, 1, 1)
        
        # 평가손익
        self.profit_loss_label = QLabel("평가손익:")
        self.profit_loss_value = QLabel("0")
        self.profit_loss_value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        info_layout.addWidget(self.profit_loss_label, 1, 2)
        info_layout.addWidget(self.profit_loss_value, 1, 3)
        
        # 수익률
        self.profit_rate_label = QLabel("수익률:")
        self.profit_rate_value = QLabel("0%")
        self.profit_rate_value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        info_layout.addWidget(self.profit_rate_label, 2, 0)
        info_layout.addWidget(self.profit_rate_value, 2, 1)
        
        # 총자산
        self.total_balance_label = QLabel("총자산:")
        self.total_balance_value = QLabel("0")
        self.total_balance_value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        info_layout.addWidget(self.total_balance_label, 2, 2)
        info_layout.addWidget(self.total_balance_value, 2, 3)
        
        main_layout.addLayout(info_layout)
        
        # 시그널 연결
        self.account_combo.currentTextChanged.connect(self._on_account_changed)
        self.refresh_btn.clicked.connect(self._on_refresh_clicked)
    
    def update_account_list(self):
        """계좌 목록 업데이트"""
        try:
            # 기존 목록 초기화
            self.account_combo.clear()
            
            if self.kiwoom:
                # 계좌 목록 가져오기
                accounts = self.kiwoom.get_account_info()
                
                # 계좌 목록이 유효한지 확인
                if accounts and isinstance(accounts, list):
                    # 콤보박스에 계좌 추가
                    for account in accounts:
                        self.account_combo.addItem(account)
                    
                    # 첫 번째 계좌 선택
                    if self.account_combo.count() > 0:
                        self.account_combo.setCurrentIndex(0)
                        logger.info(f"첫 번째 계좌 선택: {self.account_combo.currentText()}")
                else:
                    logger.warning("유효한 계좌 목록을 가져올 수 없습니다.")
            else:
                logger.warning("키움 API가 초기화되지 않았습니다.")
        
        except Exception as e:
            logger.error(f"계좌 목록 업데이트 중 오류 발생: {e}")
    
    def update_account_info(self, account_no=None):
        """계좌 정보 업데이트"""
        try:
            if not account_no:
                account_no = self.account_combo.currentText()
            
            if not account_no:
                logger.warning("선택된 계좌가 없습니다.")
                return
            
            if self.kiwoom:
                # 계좌 정보 요청
                account_info = self.kiwoom.get_account_eval_balance(account_no)
                
                if account_info:
                    # 예수금
                    deposit = account_info.get('예수금', 0)
                    self.deposit_value.setText(f"{deposit:,}")
                    
                    # 평가금액
                    eval_balance = account_info.get('평가금액', 0)
                    self.eval_balance_value.setText(f"{eval_balance:,}")
                    
                    # 매입금액
                    purchase_amount = account_info.get('매입금액', 0)
                    self.purchase_amount_value.setText(f"{purchase_amount:,}")
                    
                    # 평가손익
                    profit_loss = account_info.get('평가손익', 0)
                    self.profit_loss_value.setText(f"{profit_loss:,}")
                    
                    # 수익률
                    profit_rate = account_info.get('수익률', 0)
                    self.profit_rate_value.setText(f"{profit_rate:.2f}%")
                    
                    # 총자산
                    total_balance = account_info.get('총자산', 0)
                    self.total_balance_value.setText(f"{total_balance:,}")
                    
                    # 손익에 따른 색상 변경
                    self._update_profit_loss_color(profit_loss, profit_rate)
                    
                    logger.info(f"계좌 정보 업데이트 완료: {account_no}")
                else:
                    logger.warning(f"계좌 정보를 가져올 수 없습니다: {account_no}")
            else:
                logger.warning("키움 API가 초기화되지 않았습니다.")
        
        except Exception as e:
            logger.error(f"계좌 정보 업데이트 중 오류 발생: {e}")
    
    def _update_profit_loss_color(self, profit_loss, profit_rate):
        """손익에 따른 색상 변경"""
        # 평가손익 색상
        if profit_loss > 0:
            self.profit_loss_value.setStyleSheet("color: red;")
        elif profit_loss < 0:
            self.profit_loss_value.setStyleSheet("color: blue;")
        else:
            self.profit_loss_value.setStyleSheet("")
        
        # 수익률 색상
        if profit_rate > 0:
            self.profit_rate_value.setStyleSheet("color: red;")
        elif profit_rate < 0:
            self.profit_rate_value.setStyleSheet("color: blue;")
        else:
            self.profit_rate_value.setStyleSheet("")
    
    def _on_account_changed(self, account_no):
        """계좌 변경 이벤트 핸들러"""
        logger.info(f"계좌 변경: {account_no}")
        self.account_changed.emit(account_no)
        self.update_account_info(account_no)
    
    def _on_refresh_clicked(self):
        """새로고침 버튼 클릭 이벤트 핸들러"""
        logger.info("계좌 정보 새로고침")
        self.refresh_requested.emit()
        self.update_account_info() 