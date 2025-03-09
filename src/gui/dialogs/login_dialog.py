"""
로그인 다이얼로그
"""
import sys
import time
import logging

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QTime, QTimer, QEventLoop, QSettings
from PyQt5.QAxContainer import QAxWidget
from .base_settings_dialog import BaseSettingsDialog

# 로깅 설정
logger = logging.getLogger(__name__)

class LoginDialog(BaseSettingsDialog):
    def __init__(self, kiwoom):
        super().__init__(title="트레이딩봇 로그인", size=(400, 400))
        
        # 키움 API 변수
        self.kiwoom = kiwoom
        self.connected = False
        
        # QSettings 객체 생성
        self.qsettings = QSettings('MyCompany', 'MyTrader')
        
        # UI 초기화
        self.init_ui()
        
        # 이벤트 핸들러 연결
        self.kiwoom.ocx.OnEventConnect.connect(self._on_event_connect)
        
        # 저장된 설정 로드
        self.load_settings()
        
        # 자동 로그인 체크 시 자동 로그인 시도
        if self.auto_login_check.isChecked():
            QTimer.singleShot(500, self.kiwoom_login)
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 키움증권 로그인 그룹
        kiwoom_group = QGroupBox("키움증권 로그인")
        kiwoom_layout = QVBoxLayout()
        
        # 로그인 상태 표시
        self.status_label = QLabel("로그인이 필요합니다.")
        kiwoom_layout.addWidget(self.status_label)
        
        # 로그인 버튼
        self.login_btn = QPushButton("키움증권 로그인")
        self.login_btn.clicked.connect(self.kiwoom_login)
        kiwoom_layout.addWidget(self.login_btn)
        
        # 자동 로그인 체크박스
        self.auto_login_check = QCheckBox("다음에 자동 로그인")
        self.auto_login_check.setChecked(self.qsettings.value('auto_login', False, bool))
        kiwoom_layout.addWidget(self.auto_login_check)
        
        kiwoom_group.setLayout(kiwoom_layout)
        layout.addWidget(kiwoom_group)
        
        # API 설정 그룹 추가
        layout.addWidget(self.create_api_settings_group())
        
        # 버튼 그룹
        button_layout = QHBoxLayout()
        
        # 저장 버튼
        self.save_btn = QPushButton("설정 저장")
        self.save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_btn)
        
        # 취소 버튼
        self.cancel_btn = QPushButton("취소")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def kiwoom_login(self):
        """키움증권 로그인"""
        try:
            print("로그인 시도...")
            
            # 이미 로그인되어 있는지 확인
            if self.kiwoom.get_connect_state():
                print("이미 로그인되어 있습니다.")
                self.connected = True
                self.status_label.setText("로그인 성공")
                self.accept()
                return
            
            # 로그인 창 표시
            self.kiwoom.ocx.dynamicCall("CommConnect()")
            
            # 로그인 이벤트 대기
            self.status_label.setText("로그인 중...")
            self.login_btn.setEnabled(False)
            
            # 이벤트 루프를 생성하여 로그인 완료를 대기
            login_loop = QEventLoop()
            
            # 30초 타임아웃 설정
            timeout_timer = QTimer()
            timeout_timer.setSingleShot(True)
            timeout_timer.timeout.connect(lambda: self._handle_timeout(login_loop))
            timeout_timer.start(30000)  # 30초
            
            # 로그인 이벤트 루프 실행
            login_loop.exec_()
            
            # 타이머 중지
            timeout_timer.stop()
            
            # 로그인 결과 확인
            if self.connected:
                print("로그인 성공")
                self.status_label.setText("로그인 성공")
                
                # 계좌 정보 업데이트
                accounts = self.kiwoom.get_login_info("ACCNO").split(';')[:-1]
                if accounts:
                    self.status_label.setText(f"로그인 성공 (계좌: {', '.join(accounts)})")
                    print(f"보유 계좌: {accounts}")
                    print(f"보유 계좌 수: {len(accounts)}")
                    print(f"계좌 목록: {accounts}")
                
                # 자동 로그인 설정 저장
                self.qsettings.setValue('auto_login', self.auto_login_check.isChecked())
                
                # 대화상자 수락 (확인 버튼 클릭과 동일)
                self.accept()
            else:
                print("로그인 실패 또는 타임아웃")
                self.status_label.setText("로그인 실패 또는 타임아웃")
                self.login_btn.setEnabled(True)
        
        except Exception as e:
            print(f"로그인 중 오류 발생: {e}")
            self.status_label.setText(f"로그인 오류: {str(e)}")
            self.login_btn.setEnabled(True)
    
    def _handle_timeout(self, login_loop):
        """로그인 타임아웃 처리"""
        print("로그인 타임아웃")
        self.status_label.setText("로그인 시간 초과")
        self.login_btn.setEnabled(True)
        login_loop.quit()
    
    def _on_event_connect(self, err_code):
        """
        로그인 이벤트 핸들러
        :param err_code: 0이면 로그인 성공, 나머지는 실패
        """
        error_messages = {
            "0": "로그인 성공",
            "-100": "사용자 정보교환 실패",
            "-101": "서버접속 실패",
            "-102": "버전처리 실패",
            "-106": "통신 연결 종료"
        }
        
        if err_code == 0:
            print("로그인 이벤트 수신: 성공")
            self.connected = True
            
            # 로그인 성공 시 자동으로 다이얼로그 닫기
            QTimer.singleShot(500, self.accept)
        else:
            error_msg = error_messages.get(str(err_code), f"알 수 없는 오류 (에러 코드: {err_code})")
            print(f"로그인 이벤트 수신: 실패 - {error_msg}")
            self.connected = False
            self.login_btn.setEnabled(True)
            self.status_label.setText(f"로그인 실패: {error_msg}")
    
    def load_settings(self):
        """설정 로드"""
        # OpenAI API 키 로드
        if hasattr(self, 'openai_key_edit'):
            openai_key = self.qsettings.value('openai_api_key', '')
            self.openai_key_edit.setText(openai_key)
        
        # 텔레그램 토큰 로드
        if hasattr(self, 'telegram_token_edit'):
            telegram_token = self.qsettings.value('telegram_token', '')
            self.telegram_token_edit.setText(telegram_token)
        
        # API 사용 여부 로드
        if hasattr(self, 'use_api_check'):
            use_api = self.qsettings.value('use_api', False, bool)
            self.use_api_check.setChecked(use_api)
    
    def save_settings(self):
        """설정 저장"""
        # OpenAI API 키 저장
        if hasattr(self, 'openai_key_edit'):
            openai_key = self.openai_key_edit.text()
            self.qsettings.setValue('openai_api_key', openai_key)
        
        # 텔레그램 토큰 저장
        if hasattr(self, 'telegram_token_edit'):
            telegram_token = self.telegram_token_edit.text()
            self.qsettings.setValue('telegram_token', telegram_token)
        
        # API 사용 여부 저장
        if hasattr(self, 'use_api_check'):
            use_api = self.use_api_check.isChecked()
            self.qsettings.setValue('use_api', use_api)
        
        # 자동 로그인 설정 저장
        self.qsettings.setValue('auto_login', self.auto_login_check.isChecked())
        
        # 성공 메시지 표시
        QMessageBox.information(self, "알림", "설정이 저장되었습니다.")