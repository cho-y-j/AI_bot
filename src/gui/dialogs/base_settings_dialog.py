"""
공통 설정 다이얼로그 베이스 클래스
"""
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QSettings

class BaseSettingsDialog(QDialog):
    def __init__(self, title="설정", size=(400, 300), parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(*size)
        
        # 설정 매니저 초기화
        self.settings = QSettings('MyCompany', 'MyTrader')
        
        # UI 컴포넌트
        self.openai_key_edit = None
        self.telegram_token_edit = None
        self.use_api_check = None
    
    def create_api_settings_group(self):
        """API 설정 그룹 생성"""
        api_group = QGroupBox("API 설정")
        api_layout = QFormLayout()
        
        # OpenAI API 키 입력
        self.openai_key_edit = QLineEdit()
        self.openai_key_edit.setEchoMode(QLineEdit.Password)
        api_layout.addRow("OpenAI API 키:", self.openai_key_edit)
        
        # 텔레그램 토큰 입력
        self.telegram_token_edit = QLineEdit()
        self.telegram_token_edit.setEchoMode(QLineEdit.Password)
        api_layout.addRow("텔레그램 토큰:", self.telegram_token_edit)
        
        # API 사용 여부 체크박스
        self.use_api_check = QCheckBox("API 사용")
        api_layout.addRow("", self.use_api_check)
        
        api_group.setLayout(api_layout)
        return api_group
    
    def load_settings(self):
        """저장된 설정 로드"""
        try:
            if self.openai_key_edit:
                # OpenAI API 키 로드
                saved_openai_key = self.settings.value("openai_api_key", "")
                if saved_openai_key:
                    self.openai_key_edit.setText(saved_openai_key)
            
            if self.telegram_token_edit:
                # 텔레그램 토큰 로드
                saved_telegram_token = self.settings.value("telegram_token", "")
                if saved_telegram_token:
                    self.telegram_token_edit.setText(saved_telegram_token)
            
            if self.use_api_check:
                # API 사용 여부 로드
                use_api = self.settings.value("use_api", False, bool)
                self.use_api_check.setChecked(use_api)
            
            print("설정 로드 완료")
        except Exception as e:
            print(f"설정 로드 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
    
    def save_settings(self):
        """설정 저장"""
        try:
            if self.openai_key_edit:
                # OpenAI API 키 저장
                openai_key = self.openai_key_edit.text()
                if openai_key:
                    self.settings.setValue("openai_api_key", openai_key)
            
            if self.telegram_token_edit:
                # 텔레그램 토큰 저장
                telegram_token = self.telegram_token_edit.text()
                if telegram_token:
                    self.settings.setValue("telegram_token", telegram_token)
            
            if self.use_api_check:
                # API 사용 여부 저장
                use_api = self.use_api_check.isChecked()
                self.settings.setValue("use_api", use_api)
            
            # 성공 메시지 표시
            QMessageBox.information(self, "알림", "설정이 저장되었습니다.")
            
        except Exception as e:
            print(f"설정 저장 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "오류", f"설정 저장 중 오류가 발생했습니다.\n{str(e)}")