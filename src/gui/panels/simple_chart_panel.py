"""
간소화된 차트 패널 모듈
"""
import logging
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import pandas_ta as ta
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QComboBox, QCheckBox, QGroupBox,
    QSpinBox, QSplitter, QFrame, QScrollBar
)
from PyQt5.QtCore import Qt, pyqtSignal, QRectF
from PyQt5.QtGui import QColor, QPen, QBrush
import pyqtgraph as pg

logger = logging.getLogger(__name__)

class CandlestickItem(pg.GraphicsObject):
    """캔들스틱 아이템 클래스"""
    def __init__(self):
        pg.GraphicsObject.__init__(self)
        self.data = []
        self.picture = None
        self.generatePicture()
    
    def setData(self, data):
        self.data = data
        self.generatePicture()
        self.informViewBoundsChanged()
    
    def generatePicture(self):
        from PyQt5.QtGui import QPicture, QPainter
        
        if not self.data:
            return
        
        self.picture = QPicture()
        p = QPainter(self.picture)
        
        w = 0.4  # 캔들 너비
        for item in self.data:
            t = item['time']
            open_price = item['open']
            high = item['high']
            low = item['low']
            close = item['close']
            
            # 상승/하락 여부에 따라 색상 설정
            if close > open_price:
                # 상승 (빨간색)
                p.setPen(pg.mkPen('r'))
                p.setBrush(pg.mkBrush('r'))
            else:
                # 하락 (파란색)
                p.setPen(pg.mkPen('b'))
                p.setBrush(pg.mkBrush('b'))
            
            # 캔들 몸통 그리기
            p.drawRect(QRectF(t - w, open_price, w * 2, close - open_price))
            
            # 위 꼬리 그리기
            p.drawLine(t, high, t, max(open_price, close))
            
            # 아래 꼬리 그리기
            p.drawLine(t, low, t, min(open_price, close))
        
        p.end()
    
    def paint(self, p, *args):
        if self.picture is not None:
            p.drawPicture(0, 0, self.picture)
    
    def boundingRect(self):
        if self.picture is None:
            return QRectF(0, 0, 0, 0)
        return QRectF(self.picture.boundingRect())

class VolumeItem(pg.BarGraphItem):
    """거래량 아이템 클래스"""
    def __init__(self):
        pg.BarGraphItem.__init__(self, x=[], height=[], width=0.8)
        
    def setData(self, data):
        """데이터 설정"""
        if not data:
            return
            
        x = []
        heights = []
        brushes = []
        
        for item in data:
            t = item['time']
            open_price = item['open']
            close = item['close']
            volume = item['volume']
            
            x.append(t)
            heights.append(volume)
            
            # 상승/하락 여부에 따라 색상 설정
            if close > open_price:
                # 상승 (빨간색)
                brushes.append(pg.mkBrush('r'))
            else:
                # 하락 (파란색)
                brushes.append(pg.mkBrush('b'))
        
        self.setOpts(x=x, height=heights, width=0.8, brushes=brushes)

class SimpleChartPanel(QWidget):
    """간소화된 차트 패널 클래스"""
    
    # 시그널 정의
    stock_selected = pyqtSignal(str, str)  # 종목 선택 시그널 (종목코드, 종목명)
    
    def __init__(self, parent=None, kiwoom=None):
        super().__init__(parent)
        self.kiwoom = kiwoom
        self.parent = parent
        
        # 차트 데이터
        self.code = None
        self.name = None
        self.dates = []
        self.opens = []
        self.highs = []
        self.lows = []
        self.closes = []
        self.volumes = []
        
        # 이동평균선 설정
        self.ma5_enabled = True
        self.ma10_enabled = True
        self.ma20_enabled = True
        self.ma60_enabled = True
        self.ma120_enabled = True
        
        # 이동평균선 데이터
        self.ma5 = []
        self.ma10 = []
        self.ma20 = []
        self.ma60 = []
        self.ma120 = []
        
        # 거래량 설정
        self.volume_enabled = True
        
        # 현재가 정보
        self.current_price = 0
        self.prev_close = 0
        self.price_change = 0
        self.price_change_percent = 0
        
        # 스크롤 설정
        self.scroll_position = 0
        self.view_range = 100  # 한 번에 표시할 데이터 개수
        
        # UI 초기화
        self.init_ui()
    
    def init_ui(self):
        """UI 초기화"""
        # 메인 레이아웃
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 상단 컨트롤 영역
        control_layout = QHBoxLayout()
        
        # 종목 선택 콤보박스
        self.stock_combo = QComboBox()
        self.stock_combo.setEditable(True)
        self.stock_combo.setMinimumWidth(150)
        control_layout.addWidget(QLabel("종목:"))
        control_layout.addWidget(self.stock_combo)
        
        # 차트 타입 선택
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems(["일봉", "주봉", "월봉", "분봉"])
        control_layout.addWidget(QLabel("차트:"))
        control_layout.addWidget(self.chart_type_combo)
        
        # 기간 선택
        self.period_combo = QComboBox()
        self.period_combo.addItems(["1개월", "3개월", "6개월", "1년", "3년", "전체"])
        control_layout.addWidget(QLabel("기간:"))
        control_layout.addWidget(self.period_combo)
        
        # 새로고침 버튼
        self.refresh_btn = QPushButton("새로고침")
        self.refresh_btn.clicked.connect(self.update_chart)
        control_layout.addWidget(self.refresh_btn)
        
        control_layout.addStretch()
        
        # 현재가 정보 표시
        self.price_info_layout = QHBoxLayout()
        self.current_price_label = QLabel("현재가: -")
        self.current_price_label.setStyleSheet("font-weight: bold;")
        self.price_change_label = QLabel("전일대비: -")
        
        self.price_info_layout.addWidget(self.current_price_label)
        self.price_info_layout.addWidget(self.price_change_label)
        self.price_info_layout.addStretch()
        
        # 레이아웃 추가
        main_layout.addLayout(control_layout)
        main_layout.addLayout(self.price_info_layout)
        
        # 차트 영역 레이아웃
        chart_layout = QVBoxLayout()
        chart_layout.setContentsMargins(0, 0, 0, 0)
        chart_layout.setSpacing(0)
        
        # 메인 차트 위젯 (캔들스틱 + 이동평균선)
        self.price_chart_widget = pg.PlotWidget()
        self.price_chart_widget.setBackground('w')  # 흰색 배경
        self.price_chart_widget.showGrid(x=True, y=True)
        self.price_chart_widget.setLabel('left', '가격')
        
        # Y축 설정 (오른쪽에도 표시)
        self.price_chart_widget.getAxis('right').setStyle(showValues=True)
        self.price_chart_widget.showAxis('right')
        
        # 캔들스틱 아이템
        self.candle_item = CandlestickItem()
        self.price_chart_widget.addItem(self.candle_item)
        
        # 이동평균선 아이템
        self.ma5_item = pg.PlotDataItem(pen=pg.mkPen('r', width=2))
        self.ma10_item = pg.PlotDataItem(pen=pg.mkPen('g', width=2))
        self.ma20_item = pg.PlotDataItem(pen=pg.mkPen('b', width=2))
        self.ma60_item = pg.PlotDataItem(pen=pg.mkPen('y', width=2))
        self.ma120_item = pg.PlotDataItem(pen=pg.mkPen('m', width=2))
        
        self.price_chart_widget.addItem(self.ma5_item)
        self.price_chart_widget.addItem(self.ma10_item)
        self.price_chart_widget.addItem(self.ma20_item)
        self.price_chart_widget.addItem(self.ma60_item)
        self.price_chart_widget.addItem(self.ma120_item)
        
        # 거래량 차트 위젯
        self.volume_chart_widget = pg.PlotWidget()
        self.volume_chart_widget.setBackground('w')  # 흰색 배경
        self.volume_chart_widget.showGrid(x=True, y=True)
        self.volume_chart_widget.setLabel('left', '거래량')
        self.volume_chart_widget.setMaximumHeight(150)  # 거래량 차트 높이 제한
        
        # 거래량 아이템
        self.volume_item = VolumeItem()
        self.volume_chart_widget.addItem(self.volume_item)
        
        # 두 차트 X축 연결
        self.price_chart_widget.setXLink(self.volume_chart_widget)
        
        # 차트를 레이아웃에 추가
        chart_layout.addWidget(self.price_chart_widget, 7)  # 70% 비율
        chart_layout.addWidget(self.volume_chart_widget, 3)  # 30% 비율
        
        # 스크롤바 추가
        self.scroll_bar = QScrollBar(Qt.Horizontal)
        self.scroll_bar.setMinimum(0)
        self.scroll_bar.setMaximum(0)  # 초기값, 데이터 로드 후 업데이트
        self.scroll_bar.valueChanged.connect(self.on_scroll_changed)
        
        # 전체 레이아웃에 차트 영역과 스크롤바 추가
        main_layout.addLayout(chart_layout)
        main_layout.addWidget(self.scroll_bar)
        
        # 하단 컨트롤 영역
        bottom_layout = QHBoxLayout()
        
        # 이동평균선 체크박스
        ma_group = QGroupBox("이동평균선")
        ma_layout = QHBoxLayout()
        
        self.ma5_check = QCheckBox("5일")
        self.ma5_check.setChecked(self.ma5_enabled)
        self.ma5_check.stateChanged.connect(self.update_moving_average)
        ma_layout.addWidget(self.ma5_check)
        
        self.ma10_check = QCheckBox("10일")
        self.ma10_check.setChecked(self.ma10_enabled)
        self.ma10_check.stateChanged.connect(self.update_moving_average)
        ma_layout.addWidget(self.ma10_check)
        
        self.ma20_check = QCheckBox("20일")
        self.ma20_check.setChecked(self.ma20_enabled)
        self.ma20_check.stateChanged.connect(self.update_moving_average)
        ma_layout.addWidget(self.ma20_check)
        
        self.ma60_check = QCheckBox("60일")
        self.ma60_check.setChecked(self.ma60_enabled)
        self.ma60_check.stateChanged.connect(self.update_moving_average)
        ma_layout.addWidget(self.ma60_check)
        
        self.ma120_check = QCheckBox("120일")
        self.ma120_check.setChecked(self.ma120_enabled)
        self.ma120_check.stateChanged.connect(self.update_moving_average)
        ma_layout.addWidget(self.ma120_check)
        
        ma_group.setLayout(ma_layout)
        bottom_layout.addWidget(ma_group)
        
        # 거래량 표시 체크박스
        self.volume_check = QCheckBox("거래량")
        self.volume_check.setChecked(self.volume_enabled)
        self.volume_check.stateChanged.connect(self.update_volume_visibility)
        bottom_layout.addWidget(self.volume_check)
        
        main_layout.addLayout(bottom_layout)
        
        # 이벤트 연결
        self.stock_combo.currentIndexChanged.connect(self.on_stock_changed)
        self.chart_type_combo.currentIndexChanged.connect(self.update_chart)
        self.period_combo.currentIndexChanged.connect(self.update_chart)
    
    def set_stock(self, code, name):
        """종목 설정"""
        self.code = code
        self.name = name
        
        # 콤보박스 업데이트
        self.stock_combo.setCurrentText(f"{name}({code})")
        
        # 차트 업데이트
        self.update_chart()
    
    def on_stock_changed(self):
        """종목 변경 이벤트"""
        text = self.stock_combo.currentText()
        if "(" in text and ")" in text:
            name = text.split("(")[0]
            code = text.split("(")[1].split(")")[0]
            self.set_stock(code, name)
            self.stock_selected.emit(code, name)
    
    def update_chart(self):
        """차트 업데이트"""
        if not self.code:
            return
        
        # 임시 데이터 생성 (실제로는 키움 API에서 데이터를 가져와야 함)
        self.generate_sample_data()
        
        # 이동평균선 계산
        self.calculate_moving_average()
        
        # 스크롤바 범위 설정
        data_len = len(self.closes)
        if data_len > self.view_range:
            self.scroll_bar.setMaximum(data_len - self.view_range)
            self.scroll_bar.setPageStep(self.view_range // 2)
        else:
            self.scroll_bar.setMaximum(0)
        
        # 스크롤 위치 초기화 (가장 최근 데이터 표시)
        if data_len > self.view_range:
            self.scroll_position = data_len - self.view_range
            self.scroll_bar.setValue(self.scroll_position)
        else:
            self.scroll_position = 0
            self.scroll_bar.setValue(0)
        
        # 차트 그리기
        self.draw_chart()
        
        # 현재가 정보 업데이트
        if self.closes:
            current_price = self.closes[-1]
            prev_close = self.closes[-2] if len(self.closes) > 1 else current_price
            self.update_current_price_info(current_price, prev_close)
    
    def on_scroll_changed(self, value):
        """스크롤바 값 변경 이벤트"""
        self.scroll_position = value
        self.draw_chart()
    
    def generate_sample_data(self):
        """샘플 데이터 생성 (테스트용)"""
        import random
        
        # 날짜 생성
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        dates = []
        current_date = start_date
        
        # 초기 가격
        price = 10000
        
        # 데이터 초기화
        self.dates = []
        self.opens = []
        self.highs = []
        self.lows = []
        self.closes = []
        self.volumes = []
        
        # 데이터 생성
        while current_date <= end_date:
            if current_date.weekday() < 5:  # 주말 제외
                dates.append(current_date)
                
                # 시가
                open_price = price * (1 + random.uniform(-0.02, 0.02))
                
                # 고가, 저가
                high_price = open_price * (1 + random.uniform(0, 0.05))
                low_price = open_price * (1 - random.uniform(0, 0.05))
                
                # 종가
                close_price = random.uniform(low_price, high_price)
                
                # 거래량
                volume = random.randint(10000, 1000000)
                
                # 데이터 추가
                self.dates.append(current_date)
                self.opens.append(open_price)
                self.highs.append(high_price)
                self.lows.append(low_price)
                self.closes.append(close_price)
                self.volumes.append(volume)
                
                # 다음 날의 시작 가격은 오늘의 종가
                price = close_price
            
            current_date += timedelta(days=1)
    
    def calculate_moving_average(self):
        """이동평균선 계산"""
        if not self.closes:
            return
        
        # 종가 데이터를 numpy 배열로 변환
        closes = np.array(self.closes)
        
        # 이동평균선 계산
        if len(closes) >= 5:
            self.ma5 = pd.Series(closes).rolling(window=5).mean().values
        else:
            self.ma5 = []
        
        if len(closes) >= 10:
            self.ma10 = pd.Series(closes).rolling(window=10).mean().values
        else:
            self.ma10 = []
        
        if len(closes) >= 20:
            self.ma20 = pd.Series(closes).rolling(window=20).mean().values
        else:
            self.ma20 = []
        
        if len(closes) >= 60:
            self.ma60 = pd.Series(closes).rolling(window=60).mean().values
        else:
            self.ma60 = []
        
        if len(closes) >= 120:
            self.ma120 = pd.Series(closes).rolling(window=120).mean().values
        else:
            self.ma120 = []
    
    def draw_chart(self):
        """차트 그리기"""
        if not self.closes:
            return
        
        # 스크롤 위치에 따라 표시할 데이터 범위 계산
        data_len = len(self.closes)
        if data_len <= self.view_range:
            start_idx = 0
            end_idx = data_len
        else:
            start_idx = self.scroll_position
            end_idx = min(start_idx + self.view_range, data_len)
        
        # 캔들스틱 데이터 설정
        candle_data = []
        for i in range(start_idx, end_idx):
            candle_data.append({
                'time': i - start_idx,  # X축 위치 조정
                'open': self.opens[i],
                'high': self.highs[i],
                'low': self.lows[i],
                'close': self.closes[i],
                'volume': self.volumes[i]
            })
        
        self.candle_item.setData(candle_data)
        
        # 거래량 데이터 설정
        self.volume_item.setData(candle_data)
        
        # 이동평균선 데이터 설정
        x = list(range(end_idx - start_idx))
        
        if self.ma5_enabled and len(self.ma5) > 0:
            ma5_data = self.ma5[start_idx:end_idx]
            self.ma5_item.setData(x, ma5_data)
            self.ma5_item.show()
        else:
            self.ma5_item.hide()
        
        if self.ma10_enabled and len(self.ma10) > 0:
            ma10_data = self.ma10[start_idx:end_idx]
            self.ma10_item.setData(x, ma10_data)
            self.ma10_item.show()
        else:
            self.ma10_item.hide()
        
        if self.ma20_enabled and len(self.ma20) > 0:
            ma20_data = self.ma20[start_idx:end_idx]
            self.ma20_item.setData(x, ma20_data)
            self.ma20_item.show()
        else:
            self.ma20_item.hide()
        
        if self.ma60_enabled and len(self.ma60) > 0:
            ma60_data = self.ma60[start_idx:end_idx]
            self.ma60_item.setData(x, ma60_data)
            self.ma60_item.show()
        else:
            self.ma60_item.hide()
        
        if self.ma120_enabled and len(self.ma120) > 0:
            ma120_data = self.ma120[start_idx:end_idx]
            self.ma120_item.setData(x, ma120_data)
            self.ma120_item.show()
        else:
            self.ma120_item.hide()
        
        # 차트 범위 설정
        slice_lows = self.lows[start_idx:end_idx]
        slice_highs = self.highs[start_idx:end_idx]
        
        # Y축 범위 설정
        min_y = min(slice_lows) * 0.995
        max_y = max(slice_highs) * 1.005
        self.price_chart_widget.setYRange(min_y, max_y)
        
        # X축 범위 설정
        self.price_chart_widget.setXRange(0, len(x) - 1)
        
        # 거래량 차트 범위 설정
        slice_volumes = self.volumes[start_idx:end_idx]
        if slice_volumes:
            max_volume = max(slice_volumes) * 1.1
            self.volume_chart_widget.setYRange(0, max_volume)
            self.volume_chart_widget.setXRange(0, len(x) - 1)
    
    def update_moving_average(self):
        """이동평균선 업데이트"""
        self.ma5_enabled = self.ma5_check.isChecked()
        self.ma10_enabled = self.ma10_check.isChecked()
        self.ma20_enabled = self.ma20_check.isChecked()
        self.ma60_enabled = self.ma60_check.isChecked()
        self.ma120_enabled = self.ma120_check.isChecked()
        
        self.draw_chart()
    
    def update_volume_visibility(self):
        """거래량 표시 여부 업데이트"""
        self.volume_enabled = self.volume_check.isChecked()
        self.volume_chart_widget.setVisible(self.volume_enabled)
        self.draw_chart()
    
    def update_current_price_info(self, current_price, previous_close):
        """현재가 정보 업데이트"""
        self.current_price = current_price
        self.prev_close = previous_close
        
        # 변화량 계산
        self.price_change = current_price - previous_close
        if previous_close > 0:
            self.price_change_percent = (self.price_change / previous_close) * 100
        else:
            self.price_change_percent = 0
        
        # 라벨 텍스트 업데이트
        self.current_price_label.setText(f"현재가: {current_price:,.0f}")
        
        # 변화량에 따라 색상 설정
        if self.price_change > 0:
            change_text = f"전일대비: ▲ {self.price_change:,.0f} ({self.price_change_percent:.2f}%)"
            self.price_change_label.setStyleSheet("color: red;")
        elif self.price_change < 0:
            change_text = f"전일대비: ▼ {abs(self.price_change):,.0f} ({self.price_change_percent:.2f}%)"
            self.price_change_label.setStyleSheet("color: blue;")
        else:
            change_text = f"전일대비: 0 (0.00%)"
            self.price_change_label.setStyleSheet("color: black;")
        
        self.price_change_label.setText(change_text)
    
    def update_real_data(self, data):
        """실시간 데이터 업데이트"""
        if not data or not self.code:
            return
        
        # 현재가 추출
        current_price = data.get('현재가', 0)
        if isinstance(current_price, str):
            current_price = int(current_price.replace(',', ''))
        
        # 실시간 데이터 업데이트
        if self.closes:
            self.closes[-1] = current_price
            self.highs[-1] = max(self.highs[-1], current_price)
            self.lows[-1] = min(self.lows[-1], current_price)
            
            # 거래량 업데이트
            volume = data.get('거래량', 0)
            if isinstance(volume, str):
                volume = int(volume.replace(',', ''))
            
            if volume > 0:
                self.volumes[-1] = volume
        
        # 이동평균선 재계산
        self.calculate_moving_average()
        
        # 차트 업데이트
        self.draw_chart()
        
        # 현재가 정보 업데이트
        self.update_current_price_info(current_price, self.prev_close) 