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
    QSpinBox, QSplitter, QFrame
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
        
        # UI 초기화
        self.init_ui()
    
    def init_ui(self):
        """UI 초기화"""
        # 메인 레이아웃
        main_layout = QVBoxLayout(self)
        
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
        
        main_layout.addLayout(control_layout)
        
        # 차트 영역
        self.chart_widget = pg.PlotWidget()
        self.chart_widget.setBackground('w')  # 흰색 배경
        self.chart_widget.showGrid(x=True, y=True)
        
        # 캔들스틱 아이템
        self.candle_item = CandlestickItem()
        self.chart_widget.addItem(self.candle_item)
        
        # 이동평균선 아이템
        self.ma5_item = pg.PlotDataItem(pen=pg.mkPen('r', width=2))
        self.ma10_item = pg.PlotDataItem(pen=pg.mkPen('g', width=2))
        self.ma20_item = pg.PlotDataItem(pen=pg.mkPen('b', width=2))
        self.ma60_item = pg.PlotDataItem(pen=pg.mkPen('y', width=2))
        self.ma120_item = pg.PlotDataItem(pen=pg.mkPen('m', width=2))
        
        self.chart_widget.addItem(self.ma5_item)
        self.chart_widget.addItem(self.ma10_item)
        self.chart_widget.addItem(self.ma20_item)
        self.chart_widget.addItem(self.ma60_item)
        self.chart_widget.addItem(self.ma120_item)
        
        main_layout.addWidget(self.chart_widget)
        
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
        
        # 차트 그리기
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
        
        # 캔들스틱 데이터 설정
        candle_data = []
        for i in range(len(self.dates)):
            candle_data.append({
                'time': i,
                'open': self.opens[i],
                'high': self.highs[i],
                'low': self.lows[i],
                'close': self.closes[i],
                'volume': self.volumes[i]
            })
        
        self.candle_item.setData(candle_data)
        
        # 이동평균선 데이터 설정
        x = list(range(len(self.dates)))
        
        if self.ma5_enabled and len(self.ma5) > 0:
            self.ma5_item.setData(x, self.ma5)
            self.ma5_item.show()
        else:
            self.ma5_item.hide()
        
        if self.ma10_enabled and len(self.ma10) > 0:
            self.ma10_item.setData(x, self.ma10)
            self.ma10_item.show()
        else:
            self.ma10_item.hide()
        
        if self.ma20_enabled and len(self.ma20) > 0:
            self.ma20_item.setData(x, self.ma20)
            self.ma20_item.show()
        else:
            self.ma20_item.hide()
        
        if self.ma60_enabled and len(self.ma60) > 0:
            self.ma60_item.setData(x, self.ma60)
            self.ma60_item.show()
        else:
            self.ma60_item.hide()
        
        if self.ma120_enabled and len(self.ma120) > 0:
            self.ma120_item.setData(x, self.ma120)
            self.ma120_item.show()
        else:
            self.ma120_item.hide()
        
        # 차트 범위 설정
        self.chart_widget.setXRange(0, len(self.dates) - 1)
        self.chart_widget.setYRange(min(self.lows) * 0.95, max(self.highs) * 1.05)
    
    def update_moving_average(self):
        """이동평균선 업데이트"""
        self.ma5_enabled = self.ma5_check.isChecked()
        self.ma10_enabled = self.ma10_check.isChecked()
        self.ma20_enabled = self.ma20_check.isChecked()
        self.ma60_enabled = self.ma60_check.isChecked()
        self.ma120_enabled = self.ma120_check.isChecked()
        
        self.draw_chart() 