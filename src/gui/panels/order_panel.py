"""
주문 패널 모듈
"""
import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QComboBox, QSpinBox, QGroupBox,
    QRadioButton, QButtonGroup, QGridLayout,
    QMessageBox, QDoubleSpinBox
)
from PyQt5.QtCore import Qt, pyqtSignal

logger = logging.getLogger(__name__)

class OrderPanel(QWidget):
    """주문 패널 클래스"""
    
    # 시그널 정의
    order_submitted = pyqtSignal(dict)  # 주문 제출 시그널
    
    def __init__(self, parent=None, kiwoom=None):
        """
        초기화
        
        Args:
            parent: 부모 위젯
            kiwoom: 키움 API 객체
        """
        super().__init__(parent)
        self.kiwoom = kiwoom
        self.current_price = 0
        self.current_code = None
        self.current_name = None
        self.account_no = None
        
        # UI 초기화
        self.init_ui()
    
    def init_ui(self):
        """UI 초기화"""
        # 메인 레이아웃
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # 종목 정보 영역
        info_group = QGroupBox("종목 정보")
        info_layout = QGridLayout()
        
        # 종목 정보 라벨
        self.stock_label = QLabel()
        self.stock_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        info_layout.addWidget(self.stock_label, 0, 0, 1, 2)
        
        # 현재가 라벨
        self.price_label = QLabel("현재가:")
        self.price_value = QLabel("0")
        self.price_value.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(self.price_label, 1, 0)
        info_layout.addWidget(self.price_value, 1, 1)
        
        # 전일대비
        self.change_label = QLabel("전일대비:")
        self.change_value = QLabel("0")
        info_layout.addWidget(self.change_label, 2, 0)
        info_layout.addWidget(self.change_value, 2, 1)
        
        # 등락률
        self.rate_label = QLabel("등락률:")
        self.rate_value = QLabel("0.00%")
        info_layout.addWidget(self.rate_label, 3, 0)
        info_layout.addWidget(self.rate_value, 3, 1)
        
        # 거래량
        self.volume_label = QLabel("거래량:")
        self.volume_value = QLabel("0")
        info_layout.addWidget(self.volume_label, 4, 0)
        info_layout.addWidget(self.volume_value, 4, 1)
        
        info_group.setLayout(info_layout)
        main_layout.addWidget(info_group)
        
        # 호가 정보 영역
        hoga_group = QGroupBox("호가 정보")
        hoga_layout = QGridLayout()
        
        # 매도호가
        self.sell_hoga_labels = []
        for i in range(5):
            price_label = QLabel("0")
            volume_label = QLabel("0")
            price_label.setStyleSheet("color: blue;")
            price_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            volume_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            hoga_layout.addWidget(price_label, i, 0)
            hoga_layout.addWidget(volume_label, i, 1)
            self.sell_hoga_labels.append((price_label, volume_label))
        
        # 현재가
        current_price_label = QLabel("현재가")
        current_price_label.setStyleSheet("font-weight: bold;")
        hoga_layout.addWidget(current_price_label, 5, 0, 1, 2, Qt.AlignCenter)
        
        # 매수호가
        self.buy_hoga_labels = []
        for i in range(5):
            price_label = QLabel("0")
            volume_label = QLabel("0")
            price_label.setStyleSheet("color: red;")
            price_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            volume_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            hoga_layout.addWidget(price_label, i+6, 0)
            hoga_layout.addWidget(volume_label, i+6, 1)
            self.buy_hoga_labels.append((price_label, volume_label))
        
        hoga_group.setLayout(hoga_layout)
        main_layout.addWidget(hoga_group)
        
        # 주문 설정 영역
        order_group = QGroupBox("주문 설정")
        order_layout = QGridLayout()
        
        # 주문 유형 선택
        order_type_layout = QHBoxLayout()
        self.buy_radio = QRadioButton("매수")
        self.sell_radio = QRadioButton("매도")
        self.buy_radio.setChecked(True)
        
        self.order_type_group = QButtonGroup()
        self.order_type_group.addButton(self.buy_radio)
        self.order_type_group.addButton(self.sell_radio)
        
        order_type_layout.addWidget(self.buy_radio)
        order_type_layout.addWidget(self.sell_radio)
        order_layout.addLayout(order_type_layout, 0, 0, 1, 2)
        
        # 거래구분 선택
        order_layout.addWidget(QLabel("거래구분:"), 1, 0)
        self.trade_type_combo = QComboBox()
        self.trade_type_combo.addItems(["지정가", "시장가"])
        order_layout.addWidget(self.trade_type_combo, 1, 1)
        
        # 주문가격 입력
        order_layout.addWidget(QLabel("주문가격:"), 2, 0)
        self.price_spin = QSpinBox()
        self.price_spin.setRange(0, 1000000000)
        self.price_spin.setSingleStep(100)
        self.price_spin.setGroupSeparatorShown(True)  # 천단위 구분자 표시
        order_layout.addWidget(self.price_spin, 2, 1)
        
        # 주문수량 입력
        order_layout.addWidget(QLabel("주문수량:"), 3, 0)
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 1000000)
        order_layout.addWidget(self.quantity_spin, 3, 1)
        
        # 주문비율 버튼들
        ratio_layout = QHBoxLayout()
        ratios = ["10%", "25%", "50%", "100%"]
        for ratio in ratios:
            btn = QPushButton(ratio)
            btn.setFixedWidth(50)
            btn.clicked.connect(lambda x, r=ratio: self._set_quantity_ratio(r))
            ratio_layout.addWidget(btn)
        order_layout.addLayout(ratio_layout, 4, 0, 1, 2)
        
        # 자동 취소/정정 설정
        auto_layout = QHBoxLayout()
        
        # 자동 취소 설정
        self.auto_cancel_combo = QComboBox()
        self.auto_cancel_combo.addItems(["자동취소 없음", "60초 후", "120초 후", "180초 후"])
        auto_layout.addWidget(self.auto_cancel_combo)
        
        # 자동 정정 설정
        self.auto_adjust_combo = QComboBox()
        self.auto_adjust_combo.addItems(["자동정정 없음", "1호가", "2호가", "3호가"])
        auto_layout.addWidget(self.auto_adjust_combo)
        
        order_layout.addLayout(auto_layout, 5, 0, 1, 2)
        
        order_group.setLayout(order_layout)
        main_layout.addWidget(order_group)
        
        # 주문 버튼
        self.order_btn = QPushButton("주문")
        self.order_btn.setStyleSheet("font-weight: bold;")
        main_layout.addWidget(self.order_btn)
        
        # 시그널 연결
        self.order_btn.clicked.connect(self.submit_order)
        self.trade_type_combo.currentIndexChanged.connect(self.on_trade_type_changed)
        self.order_type_group.buttonClicked.connect(self.on_order_type_changed)
    
    def set_stock(self, code, name):
        """종목 설정"""
        self.current_code = code
        self.current_name = name
        self.stock_label.setText(f"{name} ({code})")
        
        # 실시간 데이터 등록
        if self.kiwoom:
            self.kiwoom.set_real_reg("1000", code, "10;11;12;15;13;14", "0")
    
    def set_current_price(self, price):
        """현재가 설정"""
        self.current_price = price
        self.price_value.setText(f"{price:,}")
        
        # 주문가격 업데이트
        if self.trade_type_combo.currentText() == "지정가":
            self.price_spin.setValue(price)
    
    def set_account(self, account_no):
        """계좌번호 설정"""
        self.account_no = account_no
    
    def update_stock_info(self, data):
        """종목 정보 업데이트"""
        # 현재가
        price = int(data.get('현재가', 0))
        self.price_value.setText(f"{abs(price):,}")
        
        # 전일대비
        change = int(data.get('전일대비', 0))
        self.change_value.setText(f"{change:+,}")
        if change > 0:
            self.change_value.setStyleSheet("color: red;")
        elif change < 0:
            self.change_value.setStyleSheet("color: blue;")
        else:
            self.change_value.setStyleSheet("")
        
        # 등락률
        rate = float(data.get('등락률', 0))
        self.rate_value.setText(f"{rate:+.2f}%")
        if rate > 0:
            self.rate_value.setStyleSheet("color: red;")
        elif rate < 0:
            self.rate_value.setStyleSheet("color: blue;")
        else:
            self.rate_value.setStyleSheet("")
        
        # 거래량
        volume = int(data.get('거래량', 0))
        self.volume_value.setText(f"{volume:,}")
    
    def update_hoga(self, data):
        """호가 정보 업데이트"""
        # 매도호가
        for i, (price_label, volume_label) in enumerate(self.sell_hoga_labels):
            price = int(data.get(f'매도호가{i+1}', 0))
            volume = int(data.get(f'매도호가수량{i+1}', 0))
            price_label.setText(f"{price:,}")
            volume_label.setText(f"{volume:,}")
        
        # 매수호가
        for i, (price_label, volume_label) in enumerate(self.buy_hoga_labels):
            price = int(data.get(f'매수호가{i+1}', 0))
            volume = int(data.get(f'매수호가수량{i+1}', 0))
            price_label.setText(f"{price:,}")
            volume_label.setText(f"{volume:,}")
    
    def _set_quantity_ratio(self, ratio):
        """주문수량 비율 설정"""
        if not self.current_code:
            return
        
        # 매수 가능 수량 또는 매도 가능 수량 조회
        if self.buy_radio.isChecked():
            max_quantity = self._get_buy_max_quantity()
        else:
            max_quantity = self._get_sell_max_quantity()
        
        # 비율에 따른 수량 계산
        ratio_value = float(ratio.strip('%')) / 100
        quantity = int(max_quantity * ratio_value)
        
        # 수량 설정
        self.quantity_spin.setValue(quantity)
    
    def _get_buy_max_quantity(self):
        """최대 매수 가능 수량 조회"""
        if not self.kiwoom or not self.account_no or not self.current_code:
            return 0
        
        # 매수 가능 금액 조회
        buyable_money = self.kiwoom.get_buy_money(self.account_no)
        
        # 현재가 기준으로 최대 수량 계산
        if self.current_price > 0:
            return buyable_money // self.current_price
        
        return 0
    
    def _get_sell_max_quantity(self):
        """최대 매도 가능 수량 조회"""
        if not self.kiwoom or not self.account_no or not self.current_code:
            return 0
        
        # 보유 수량 조회
        return self.kiwoom.get_stock_quantity(self.account_no, self.current_code)
    
    def on_trade_type_changed(self, index):
        """거래구분 변경 시 처리"""
        is_limit = self.trade_type_combo.currentText() == "지정가"
        self.price_spin.setEnabled(is_limit)
        
        if is_limit:
            self.price_spin.setValue(self.current_price)
        else:
            self.price_spin.setValue(0)
    
    def on_order_type_changed(self, button):
        """주문유형 변경 시 처리"""
        # 매수/매도에 따른 버튼 색상 변경
        if button == self.buy_radio:
            self.order_btn.setStyleSheet("font-weight: bold; color: red;")
        else:
            self.order_btn.setStyleSheet("font-weight: bold; color: blue;")
    
    def submit_order(self):
        """주문 제출"""
        if not self.current_code:
            QMessageBox.warning(self, "주문 오류", "종목이 선택되지 않았습니다.")
            return
        
        if not self.account_no:
            QMessageBox.warning(self, "주문 오류", "계좌가 선택되지 않았습니다.")
            return
        
        try:
            # 주문 정보 생성
            order_type = "매수" if self.buy_radio.isChecked() else "매도"
            trade_type = self.trade_type_combo.currentText()
            quantity = self.quantity_spin.value()
            price = self.price_spin.value()
            
            # 주문 확인 메시지
            msg = f"다음 주문을 제출하시겠습니까?\n\n" \
                  f"종목: {self.current_name}\n" \
                  f"주문: {order_type}\n" \
                  f"구분: {trade_type}\n" \
                  f"수량: {quantity:,}주\n" \
                  f"가격: {price:,}원"
            
            reply = QMessageBox.question(self, "주문 확인", msg,
                                       QMessageBox.Yes | QMessageBox.No,
                                       QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                # 실제 주문 전송
                if trade_type == "시장가":
                    if order_type == "매수":
                        order_no = self.kiwoom.send_market_buy_order(
                            self.current_code, quantity, self.account_no
                        )
                    else:
                        order_no = self.kiwoom.send_market_sell_order(
                            self.current_code, quantity, self.account_no
                        )
                else:
                    if order_type == "매수":
                        order_no = self.kiwoom.send_limit_buy_order(
                            self.current_code, quantity, price, self.account_no
                        )
                    else:
                        order_no = self.kiwoom.send_limit_sell_order(
                            self.current_code, quantity, price, self.account_no
                        )
                
                if order_no:
                    # 주문 모니터링 시작
                    self.kiwoom.monitor_order(order_no)
                    
                    # 자동 취소 설정
                    auto_cancel = self.auto_cancel_combo.currentText()
                    if auto_cancel != "자동취소 없음":
                        timeout = int(auto_cancel.split("초")[0])
                        self.kiwoom.set_auto_cancel(
                            order_no,
                            timeout_seconds=timeout,
                            market_price_threshold=2.0
                        )
                    
                    # 자동 정정 설정
                    auto_adjust = self.auto_adjust_combo.currentText()
                    if auto_adjust != "자동정정 없음":
                        step = int(auto_adjust.split("호가")[0])
                        self.kiwoom.set_auto_modify(
                            order_no,
                            target_price=self.current_price,
                            price_step=step * 100,
                            max_tries=3
                        )
                    
                    # 주문 정보 시그널 발생
                    order_info = {
                        "주문번호": order_no,
                        "종목코드": self.current_code,
                        "종목명": self.current_name,
                        "주문구분": order_type,
                        "거래구분": trade_type,
                        "주문가격": price,
                        "주문수량": quantity
                    }
                    self.order_submitted.emit(order_info)
                    
                    QMessageBox.information(self, "주문 완료", 
                                          f"주문이 정상적으로 접수되었습니다.\n주문번호: {order_no}")
                else:
                    QMessageBox.warning(self, "주문 오류", "주문이 실패했습니다.")
        
        except Exception as e:
            logger.error(f"주문 제출 중 오류 발생: {e}")
            QMessageBox.critical(self, "오류", f"주문 중 오류가 발생했습니다.\n{str(e)}")
    
    def clear(self):
        """패널 초기화"""
        self.current_code = None
        self.current_name = None
        self.current_price = 0
        self.stock_label.setText("")
        self.price_value.setText("0")
        self.change_value.setText("0")
        self.rate_value.setText("0.00%")
        self.volume_value.setText("0")
        self.price_spin.setValue(0)
        self.quantity_spin.setValue(0)
        
        # 호가 초기화
        for price_label, volume_label in self.sell_hoga_labels + self.buy_hoga_labels:
            price_label.setText("0")
            volume_label.setText("0") 