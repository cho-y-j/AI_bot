"""
트레이딩봇 메인 실행 파일
"""
import os
import sys
import time
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox, QDialog

# 상위 디렉토리를 시스템 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from src.kiwoom.base import KiwoomAPI
from src.gui.dialogs.login_dialog import LoginDialog
from src.gui.main_window import MainWindow

class TradingBot:
    def __init__(self):
        self.kiwoom = KiwoomAPI()
        
    def initialize(self):
        """키움 API 초기화"""
        try:
            # 연결 상태 확인
            if not self.kiwoom.get_connect_state():
                print("키움 API 연결 실패")
                return False
                
            # API 초기화
            return self.kiwoom.initialize()
        except Exception as e:
            print(f"키움 API 초기화 중 오류 발생: {e}")
            return False
    
    def set_account_password(self, password, use_auto=False):
        """계좌 비밀번호 설정"""
        if self.kiwoom:
            try:
                self.kiwoom.set_account_password(password, use_auto)
            except Exception as e:
                print(f"계좌 비밀번호 설정 중 오류: {e}")
    
    def stop(self):
        """프로그램 종료"""
        pass

def main():
    app = QApplication(sys.argv)
    
    try:
        print("트레이딩봇 시작...")
        
        # 트레이딩봇 인스턴스 생성
        trading_bot = TradingBot()
        
        # 로그인 다이얼로그 표시
        print("로그인 다이얼로그 표시...")
        login_dialog = LoginDialog(trading_bot.kiwoom)
        if login_dialog.exec_() != QDialog.Accepted:
            print("로그인이 취소되었습니다.")
            return 0
            
        # 로그인 후 API 초기화
        print("키움 API 초기화 중...")
        if not trading_bot.initialize():
            QMessageBox.critical(None, "오류", "키움 API 초기화 실패")
            return 1
        
        # 메인 윈도우 표시
        print("메인 윈도우 생성 시작...")
        try:
            print("MainWindow 클래스 인스턴스 생성 중...")
            window = MainWindow(trading_bot.kiwoom)
            print("MainWindow 인스턴스 생성 완료")
            
            print("메인 윈도우 show() 메서드 호출...")
            window.show()
            print("메인 윈도우 show() 메서드 호출 완료")
            
            print("메인 이벤트 루프 시작...")
            return app.exec_()
        except Exception as window_error:
            print(f"메인 윈도우 표시 실패: {window_error}")
            print("상세 오류 정보:")
            traceback.print_exc()
            QMessageBox.critical(None, "오류", f"메인 윈도우를 표시할 수 없습니다.\n{str(window_error)}")
            return 1
        
    except Exception as e:
        print(f"오류 발생: {e}")
        print("상세 오류 정보:")
        traceback.print_exc()
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Critical)
        msgBox.setWindowTitle("오류")
        msgBox.setText(f"프로그램 실행 중 오류가 발생했습니다.\n{str(e)}")
        msgBox.exec_()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 