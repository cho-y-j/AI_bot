from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import Qt, QTimer

class LoadingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("초기화 중...")
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        self.setFixedSize(300, 100)
        
        layout = QVBoxLayout()
        
        self.status_label = QLabel("프로그램 초기화 중...")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # 무한 로딩 표시
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)
    
    def set_status(self, message):
        """상태 메시지 업데이트"""
        self.status_label.setText(message) 