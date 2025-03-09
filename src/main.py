"""
메인 스크립트
"""
import sys
import logging
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtCore import QEventLoop

from gui.main_window import MainWindow

# 로깅 설정
def setup_logging():
    """로깅 설정"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # 파일 핸들러
    file_handler = logging.FileHandler('trading_bot.log', encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger

class KiwoomAPI:
    """키움 API 클래스"""
    
    def __init__(self):
        """초기화"""
        self.ocx = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        
        # 이벤트 루프 변수
        self.login_event_loop = None
        self.login_status = False
        
        # 이벤트 연결
        self.connect_events()
    
    def connect_events(self):
        """이벤트 연결"""
        # 로그인 이벤트
        self.ocx.OnEventConnect.connect(self._on_login)
        
        # 조회 이벤트
        self.ocx.OnReceiveTrData.connect(self._on_receive_tr_data)
        
        # 실시간 이벤트
        self.ocx.OnReceiveRealData.connect(self._on_receive_real_data)
        
        # 주문 이벤트
        self.ocx.OnReceiveChejanData.connect(self._on_receive_chejan_data)
        
        # 메시지 이벤트
        self.ocx.OnReceiveMsg.connect(self._on_receive_msg)
    
    def _on_login(self, err_code):
        """
        로그인 이벤트 처리
        
        Args:
            err_code: 에러 코드
        """
        if err_code == 0:
            logging.info("로그인 성공")
            self.login_status = True
        else:
            logging.error(f"로그인 실패: {err_code}")
            self.login_status = False
        
        # 로그인 이벤트 루프 종료
        if self.login_event_loop:
            self.login_event_loop.exit()
    
    def _on_receive_tr_data(self, screen_no, rqname, trcode, record_name, prev_next):
        """TR 수신 이벤트 처리"""
        logging.debug(f"TR 수신: {screen_no}, {rqname}, {trcode}")
    
    def _on_receive_real_data(self, code, real_type, real_data):
        """실시간 데이터 수신 이벤트 처리"""
        logging.debug(f"실시간 데이터 수신: {code}, {real_type}")
    
    def _on_receive_chejan_data(self, gubun, item_cnt, fid_list):
        """체결잔고 데이터 수신 이벤트 처리"""
        logging.debug(f"체결잔고 데이터 수신: {gubun}")
    
    def _on_receive_msg(self, screen_no, rqname, trcode, msg):
        """메시지 수신 이벤트 처리"""
        logging.info(f"메시지 수신: {msg}")
    
    def connect(self):
        """서버 연결"""
        if not self.get_connect_state():
            logging.info("로그인 시도...")
            
            # 로그인 이벤트 루프 생성
            self.login_event_loop = QEventLoop()
            
            # 로그인 요청
            self.ocx.dynamicCall("CommConnect()")
            
            # 이벤트 루프 실행 (로그인 완료까지 대기)
            self.login_event_loop.exec_()
            
            return self.login_status
        else:
            logging.info("이미 로그인되어 있습니다.")
            return True
    
    def get_connect_state(self):
        """
        연결 상태 확인
        
        Returns:
            bool: 연결 여부
        """
        return self.ocx.dynamicCall("GetConnectState()") == 1
    
    def get_login_info(self, tag):
        """
        로그인 정보 조회
        
        Args:
            tag: 조회 항목
        
        Returns:
            str: 로그인 정보
        """
        return self.ocx.dynamicCall("GetLoginInfo(QString)", tag)
    
    def get_master_code_name(self, code):
        """
        종목명 조회
        
        Args:
            code: 종목 코드
        
        Returns:
            str: 종목명
        """
        return self.ocx.dynamicCall("GetMasterCodeName(QString)", code)
    
    def get_code_list(self, market):
        """
        종목 코드 리스트 조회
        
        Args:
            market: 시장 구분
        
        Returns:
            list: 종목 코드 리스트
        """
        codes = self.ocx.dynamicCall("GetCodeListByMarket(QString)", market)
        return codes.split(';') if codes else []

def main():
    """메인 함수"""
    # 로깅 설정
    logger = setup_logging()
    logger.info("트레이딩봇 시작...")
    
    try:
        # QApplication 인스턴스 생성
        app = QApplication(sys.argv)
        
        # 잠시 대기 (키움 API 초기화를 위해)
        logger.info("키움 API 초기화 대기 중...")
        app.processEvents()  # 이벤트 처리
        
        # 키움 API 인스턴스 생성
        logger.info("키움 API 초기화 중...")
        kiwoom = KiwoomAPI()
        
        # 서버 연결
        if not kiwoom.connect():
            QMessageBox.critical(None, "오류", "키움 API 연결 실패")
            return 1
        
        # 연결 상태 확인
        if not kiwoom.get_connect_state():
            QMessageBox.critical(None, "오류", "키움 API 초기화 실패")
            return 1
        
        # 메인 윈도우 생성
        window = MainWindow(kiwoom)
        window.show()
        
        # 이벤트 루프 시작
        return app.exec_()
    
    except Exception as e:
        logger.exception("프로그램 실행 중 오류 발생")
        return 1
    
    finally:
        logger.info("프로그램 종료")

if __name__ == "__main__":
    main() 