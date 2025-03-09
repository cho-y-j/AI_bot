"""
Order Widget Module - 주문 위젯 모듈
"""

import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QComboBox, QPushButton, QSpinBox,
    QGroupBox, QFormLayout
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIntValidator

class OrderWidget(QWidget):
    """주문 위젯 클래스"""
    
    # 시그널 정의
    order_submitted = pyqtSignal(dict)  # 주문 제출 시그널
    
    def __init__(self, parent=None):
        """초기화"""
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        
        self._init_ui()
        
    def _init_ui(self):
        """UI 초기화"""
        # 메인 레이아웃
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 주문 정보 그룹
        order_group = QGroupBox('주문 정보')
        layout.addWidget(order_group)
        
        order_layout = QFormLayout()
        order_group.setLayout(order_layout)
        
        # 종목 정보
        self.code_edit = QLineEdit()
        self.code_edit.setPlaceholderText('종목코드')
        order_layout.addRow('종목코드:', self.code_edit)
        
        self.name_label = QLabel()
        order_layout.addRow('종목명:', self.name_label)
        
        # 주문 유형
        self.order_type_combo = QComboBox()
        self.order_type_combo.addItems(['신규매수', '신규매도'])
        order_layout.addRow('주문유형:', self.order_type_combo)
        
        # 거래구분
        self.trade_type_combo = QComboBox()
        self.trade_type_combo.addItems(['지정가', '시장가', '조건부지정가', '최유리지정가', '최우선지정가'])
        order_layout.addRow('거래구분:', self.trade_type_combo)
        
        # 수량
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 1000000)
        self.quantity_spin.setSingleStep(1)
        order_layout.addRow('수량:', self.quantity_spin)
        
        # 가격
        self.price_edit = QLineEdit()
        self.price_edit.setValidator(QIntValidator())
        self.price_edit.setPlaceholderText('가격')
        order_layout.addRow('가격:', self.price_edit)
        
        # 주문 버튼
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)
        
        self.submit_button = QPushButton('주문')
        self.submit_button.clicked.connect(self._on_submit)
        button_layout.addWidget(self.submit_button)
        
        self.reset_button = QPushButton('초기화')
        self.reset_button.clicked.connect(self._on_reset)
        button_layout.addWidget(self.reset_button)
        
    def set_stock(self, code, name):
        """종목 설정"""
        self.code_edit.setText(code)
        self.name_label.setText(name)
        
    def _on_submit(self):
        """주문 제출 처리"""
        # 주문 정보 수집
        order_info = {
            'code': self.code_edit.text(),
            'order_type': self.order_type_combo.currentText(),
            'trade_type': self.trade_type_combo.currentText(),
            'quantity': self.quantity_spin.value(),
            'price': int(self.price_edit.text()) if self.price_edit.text() else 0
        }
        
        # 유효성 검사
        if not order_info['code']:
            self.logger.warning('종목코드를 입력하세요.')
            return
            
        if order_info['trade_type'] == '지정가' and not order_info['price']:
            self.logger.warning('주문 가격을 입력하세요.')
            return
            
        # 주문 제출 시그널 발생
        self.order_submitted.emit(order_info)
        self.logger.info(f'주문 제출: {order_info}')
        
        # 초기화
        self._on_reset()
        
    def _on_reset(self):
        """초기화 처리"""
        self.code_edit.clear()
        self.name_label.clear()
        self.order_type_combo.setCurrentIndex(0)
        self.trade_type_combo.setCurrentIndex(0)
        self.quantity_spin.setValue(1)
        self.price_edit.clear()
        
# 예정된 기능:
# - 주문 기능
#   - 정정 주문
#   - 취소 주문
#   - 예약 주문
#
# - 주문 설정
#   - 주문 수량 계산기
#   - 주문 가격 계산기
#   - 주문 확인 대화상자
#
# - 주문 제한
#   - 주문 가능 수량 제한
#   - 주문 가격 범위 제한
#   - 주문 시간 제한
#
# - 주문 이력
#   - 주문 내역 조회
#   - 체결 내역 조회
#   - 미체결 내역 조회
#
# - 계좌 정보
#   - 예수금 조회
#   - 주문 가능 금액 조회
#   - 손익 현황 조회 