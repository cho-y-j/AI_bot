"""
매도 다이얼로그 모듈
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QComboBox, QMessageBox,
                            QGroupBox, QFormLayout, QSpinBox, QDoubleSpinBox)
from PyQt5.QtCore import Qt, pyqtSignal

class SellDialog(QDialog):
    """매도 주문 다이얼로그"""
    
    def __init__(self, parent, stock_code, stock_name, current_price=0, quantity=0):
        super().__init__(parent)
        self.stock_code = stock_code
        self.stock_name = stock_name
        self.current_price = current_price
        self.available_quantity = quantity
        
        self.init_ui()
        
    def init_ui(self):
        """UI 초기화"""
        self.setWindowTitle("매도 주문")
        self.setMinimumWidth(400)
        
        # 메인 레이아웃
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # 종목 정보 그룹
        info_group = QGroupBox("종목 정보")
        info_layout = QFormLayout()
        info_group.setLayout(info_layout)
        
        # 종목 코드 및 이름
        self.code_label = QLabel(f"{self.stock_code}")
        self.name_label = QLabel(f"{self.stock_name}")
        
        # 현재가
        self.price_label = QLabel(f"{self.current_price:,}원")
        
        # 보유 수량
        self.quantity_label = QLabel(f"{self.available_quantity:,}주")
        
        # 폼에 추가
        info_layout.addRow("종목코드:", self.code_label)
        info_layout.addRow("종목명:", self.name_label)
        info_layout.addRow("현재가:", self.price_label)
        info_layout.addRow("보유수량:", self.quantity_label)
        
        # 주문 정보 그룹
        order_group = QGroupBox("주문 정보")
        order_layout = QFormLayout()
        order_group.setLayout(order_layout)
        
        # 주문 유형
        self.order_type_combo = QComboBox()
        self.order_type_combo.addItem("지정가", 0)
        self.order_type_combo.addItem("시장가", 1)
        self.order_type_combo.currentIndexChanged.connect(self.on_order_type_changed)
        
        # 주문 가격
        self.price_spinbox = QSpinBox()
        self.price_spinbox.setRange(1, 100000000)
        self.price_spinbox.setSingleStep(10)
        self.price_spinbox.setValue(self.current_price)
        self.price_spinbox.setGroupSeparatorShown(True)
        
        # 주문 수량
        self.quantity_spinbox = QSpinBox()
        self.quantity_spinbox.setRange(1, self.available_quantity if self.available_quantity > 0 else 100000)
        self.quantity_spinbox.setValue(1)
        
        # 폼에 추가
        order_layout.addRow("주문유형:", self.order_type_combo)
        order_layout.addRow("주문가격:", self.price_spinbox)
        order_layout.addRow("주문수량:", self.quantity_spinbox)
        
        # 버튼 레이아웃
        button_layout = QHBoxLayout()
        
        # 매도 버튼
        self.sell_button = QPushButton("매도")
        self.sell_button.clicked.connect(self.accept)
        
        # 취소 버튼
        self.cancel_button = QPushButton("취소")
        self.cancel_button.clicked.connect(self.reject)
        
        # 버튼 추가
        button_layout.addWidget(self.sell_button)
        button_layout.addWidget(self.cancel_button)
        
        # 메인 레이아웃에 추가
        main_layout.addWidget(info_group)
        main_layout.addWidget(order_group)
        main_layout.addLayout(button_layout)
        
    def on_order_type_changed(self, index):
        """주문 유형 변경 시 호출"""
        order_type = self.order_type_combo.currentData()
        
        # 시장가 주문인 경우 가격 입력 비활성화
        if order_type == 1:  # 시장가
            self.price_spinbox.setEnabled(False)
        else:  # 지정가
            self.price_spinbox.setEnabled(True)
    
    def get_quantity(self):
        """주문 수량 반환"""
        return self.quantity_spinbox.value()
    
    def get_price(self):
        """주문 가격 반환"""
        return self.price_spinbox.value()
    
    def get_order_type(self):
        """주문 유형 반환"""
        return self.order_type_combo.currentData() 