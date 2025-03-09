"""
로그 패널 모듈
"""
import logging
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTextEdit, QComboBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QTextCharFormat, QBrush

# 로깅 설정
logger = logging.getLogger(__name__)

class LogPanel(QWidget):
    """로그 패널 클래스"""
    
    # 로그 레벨별 색상 정의
    LEVEL_COLORS = {
        "정보": QColor(0, 0, 0),        # 검정
        "경고": QColor(255, 128, 0),    # 주황
        "오류": QColor(255, 0, 0),      # 빨강
        "디버그": QColor(128, 128, 128), # 회색
        "성공": QColor(0, 128, 0)       # 초록
    }
    
    def __init__(self, parent=None):
        """
        초기화
        
        Args:
            parent: 부모 위젯
        """
        super().__init__(parent)
        
        # UI 초기화
        self.init_ui()
        
        # 로그 핸들러 설정
        self.setup_logger()
    
    def init_ui(self):
        """UI 초기화"""
        # 메인 레이아웃
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # 상단 컨트롤 영역
        control_layout = QHBoxLayout()
        
        # 로그 레벨 선택
        control_layout.addWidget(QLabel("로그 레벨:"))
        self.level_combo = QComboBox()
        self.level_combo.addItems(["전체"] + list(self.LEVEL_COLORS.keys()))
        self.level_combo.currentTextChanged.connect(self.filter_logs)
        control_layout.addWidget(self.level_combo)
        
        control_layout.addStretch()
        
        # 지우기 버튼
        self.clear_btn = QPushButton("지우기")
        self.clear_btn.clicked.connect(self.clear_logs)
        control_layout.addWidget(self.clear_btn)
        
        main_layout.addLayout(control_layout)
        
        # 로그 표시 영역
        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setLineWrapMode(QTextEdit.NoWrap)
        main_layout.addWidget(self.log_edit)
        
        # 로그 저장
        self.logs = []
    
    def setup_logger(self):
        """로거 설정"""
        class QTextEditHandler(logging.Handler):
            def __init__(self, widget):
                super().__init__()
                self.widget = widget
            
            def emit(self, record):
                msg = self.format(record)
                self.widget.append_log(msg, record.levelname)
        
        # 핸들러 생성 및 포매터 설정
        handler = QTextEditHandler(self)
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        handler.setFormatter(formatter)
        
        # 루트 로거에 핸들러 추가
        logging.getLogger().addHandler(handler)
    
    def append_log(self, message, level="정보"):
        """
        로그 추가
        
        Args:
            message: 로그 메시지
            level: 로그 레벨 (정보, 경고, 오류, 디버그, 성공)
        """
        try:
            # 로그 데이터 저장
            log_data = {
                "timestamp": datetime.now(),
                "message": message,
                "level": level
            }
            self.logs.append(log_data)
            
            # 현재 필터 레벨 확인
            current_level = self.level_combo.currentText()
            if current_level == "전체" or current_level == level:
                self._display_log(log_data)
        
        except Exception as e:
            logger.error(f"로그 추가 중 오류 발생: {e}")
    
    def _display_log(self, log_data):
        """
        로그 표시
        
        Args:
            log_data: 로그 데이터 딕셔너리
        """
        try:
            # 텍스트 포맷 설정
            format = QTextCharFormat()
            color = self.LEVEL_COLORS.get(log_data["level"], QColor(0, 0, 0))
            format.setForeground(QBrush(color))
            
            # 커서 이동 및 포맷 설정
            cursor = self.log_edit.textCursor()
            cursor.movePosition(cursor.End)
            cursor.insertText(f"[{log_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}] ")
            
            # 레벨 표시
            format.setFontWeight(700)  # Bold
            cursor.insertText(f"[{log_data['level']}] ", format)
            
            # 메시지 표시
            format.setFontWeight(400)  # Normal
            cursor.insertText(f"{log_data['message']}\n", format)
            
            # 스크롤을 항상 아래로
            scrollbar = self.log_edit.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
        
        except Exception as e:
            logger.error(f"로그 표시 중 오류 발생: {e}")
    
    def filter_logs(self, level):
        """
        로그 필터링
        
        Args:
            level: 필터링할 로그 레벨
        """
        try:
            # 텍스트 에디터 초기화
            self.log_edit.clear()
            
            # 선택된 레벨에 맞는 로그만 표시
            for log in self.logs:
                if level == "전체" or log["level"] == level:
                    self._display_log(log)
        
        except Exception as e:
            logger.error(f"로그 필터링 중 오류 발생: {e}")
    
    def clear_logs(self):
        """로그 지우기"""
        self.logs.clear()
        self.log_edit.clear()
    
    def get_logs(self):
        """
        저장된 로그 반환
        
        Returns:
            list: 로그 데이터 리스트
        """
        return self.logs.copy() 