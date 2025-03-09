"""
설정 다이얼로그
"""
from PyQt5.QtWidgets import *
from .base_settings_dialog import BaseSettingsDialog

class SettingsDialog(BaseSettingsDialog):
    def __init__(self, parent=None):
        super().__init__(title="설정", size=(400, 300), parent=parent)
        
        # UI 초기화
        self.init_ui()
        
        # 저장된 설정 로드
        self.load_settings()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # API 설정 그룹 추가
        layout.addWidget(self.create_api_settings_group())
        
        # 버튼 그룹
        button_layout = QHBoxLayout()
        
        # 저장 버튼
        self.save_btn = QPushButton("저장")
        self.save_btn.clicked.connect(self.on_save)
        button_layout.addWidget(self.save_btn)
        
        # 취소 버튼
        self.cancel_btn = QPushButton("취소")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def on_save(self):
        """저장 버튼 클릭 시 호출"""
        self.save_settings()
        self.accept() 