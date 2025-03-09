"""
Kiwoom API Base Module - 키움증권 API 기본 연결 및 이벤트 처리
"""

import os
import sys
import logging
from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtCore import QEventLoop

logger = logging.getLogger(__name__)

class KiwoomBase:
    """키움 API 기본 클래스"""
    
    def __init__(self):
        """초기화"""
        self.ocx = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self._event_loop = None
        
        # 이벤트 연결
        self.connect_events()
    
    def connect_events(self):
        """이벤트 연결"""
        # 로그인 이벤트
        self.ocx.OnEventConnect.connect(self._on_event_connect)
        
        # TR 수신 이벤트
        self.ocx.OnReceiveTrData.connect(self._on_receive_tr_data)
        
        # 실시간 이벤트
        self.ocx.OnReceiveRealData.connect(self._on_receive_real_data)
        
        # 조회 에러 이벤트
        self.ocx.OnReceiveMsg.connect(self._on_receive_msg)
    
    def comm_connect(self):
        """
        로그인 윈도우를 실행하고 로그인을 시도합니다.
        
        Returns:
            bool: 로그인 성공 여부
        """
        self.ocx.dynamicCall("CommConnect()")
        
        # 이벤트 루프 생성
        self._event_loop = QEventLoop()
        self._event_loop.exec_()
        
        # 연결 상태 확인
        return self.get_connect_state()
    
    def get_connect_state(self):
        """
        현재 접속 상태를 반환합니다.
        
        Returns:
            bool: 연결 여부 (True: 연결됨, False: 연결안됨)
        """
        return self.ocx.dynamicCall("GetConnectState()") == 1
    
    def get_login_info(self, tag):
        """
        로그인한 사용자 정보를 반환합니다.
        
        Args:
            tag: 요청할 정보 (ACCOUNT_CNT, ACCNO, USER_ID, USER_NAME, GetServerGubun)
        
        Returns:
            str: 요청한 정보
        """
        return self.ocx.dynamicCall("GetLoginInfo(QString)", tag)
    
    def set_input_value(self, id, value):
        """
        TR 입력값을 설정합니다.
        
        Args:
            id: TR 입력 아이디
            value: 입력값
        """
        self.ocx.dynamicCall("SetInputValue(QString, QString)", id, value)
    
    def comm_rq_data(self, rqname, trcode, next, screen_no):
        """
        TR을 요청합니다.
        
        Args:
            rqname: 요청명
            trcode: TR 코드
            next: 연속조회 여부 (0:조회, 2:연속)
            screen_no: 화면번호
        
        Returns:
            int: 요청 결과 (0:성공, -200:시간제한, -201:중복제한)
        """
        return self.ocx.dynamicCall(
            "CommRqData(QString, QString, int, QString)",
            rqname, trcode, next, screen_no
        )
    
    def get_repeat_cnt(self, trcode, rqname):
        """
        수신된 데이터의 반복 개수를 반환합니다.
        
        Args:
            trcode: TR 코드
            rqname: 요청명
        
        Returns:
            int: 데이터 반복 개수
        """
        return self.ocx.dynamicCall(
            "GetRepeatCnt(QString, QString)",
            trcode, rqname
        )
    
    def get_comm_data(self, trcode, rqname, index, item):
        """
        수신된 데이터를 반환합니다.
        
        Args:
            trcode: TR 코드
            rqname: 요청명
            index: 반복 인덱스
            item: 아이템명
        
        Returns:
            str: 수신 데이터
        """
        return self.ocx.dynamicCall(
            "GetCommData(QString, QString, int, QString)",
            trcode, rqname, index, item
        ).strip()
    
    def _on_event_connect(self, err_code):
        """
        로그인 이벤트 처리
        
        Args:
            err_code: 에러 코드 (0:성공, 그 외:실패)
        """
        try:
            if err_code == 0:
                logger.info("로그인 성공")
            else:
                logger.error(f"로그인 실패: {err_code}")
        
        except Exception as e:
            logger.exception("로그인 이벤트 처리 중 오류 발생")
        
        finally:
            # 이벤트 루프 종료
            if self._event_loop is not None:
                self._event_loop.exit()
    
    def _on_receive_tr_data(self, screen_no, rqname, trcode, record_name, next, unused1, unused2, unused3, unused4):
        """TR 수신 이벤트 처리 - 자식 클래스에서 구현"""
        pass
    
    def _on_receive_real_data(self, code, real_type, real_data):
        """실시간 데이터 수신 이벤트 처리 - 자식 클래스에서 구현"""
        pass
    
    def _on_receive_msg(self, screen_no, rqname, trcode, msg):
        """
        메시지 수신 이벤트 처리
        
        Args:
            screen_no: 화면번호
            rqname: 요청명
            trcode: TR 코드
            msg: 메시지
        """
        logger.info(f"메시지 수신: {msg} (화면번호: {screen_no}, TR: {trcode}, 요청: {rqname})")

class KiwoomAPI(KiwoomBase):
    """키움 API 클래스 - 실제 트레이딩에 사용되는 메서드들 구현"""
    
    def __init__(self):
        """초기화"""
        super().__init__()
        self.account_number = None
        self.account_count = 0
        self.account_list = []
        self.deposit = 0
        self.user_id = None
        self.user_name = None
        self.server_type = None  # 1: 모의서버, 나머지: 실서버
        
    def initialize(self):
        """
        키움 API 초기화 및 로그인
        Returns:
            bool: 초기화 성공 여부
        """
        try:
            # 로그인 상태 확인
            logger.info("로그인 상태 확인...")
            if not self.get_connect_state():
                logger.error("로그인되어 있지 않습니다.")
                return False
            
            # 사용자 정보 얻기
            self.user_id = self.get_login_info("USER_ID")
            self.user_name = self.get_login_info("USER_NAME")
            self.server_type = self.get_login_info("GetServerGubun")
            
            # 계좌 정보 얻기
            self.account_count = int(self.get_login_info("ACCOUNT_CNT"))
            self.account_list = self.get_login_info("ACCNO").split(';')[:-1]
            if self.account_list:
                self.account_number = self.account_list[0]  # 첫 번째 계좌를 기본값으로 설정
            
            logger.info(f"로그인 성공 - {self.user_name}({self.user_id})")
            logger.info(f"서버 타입: {'모의 투자' if self.server_type == '1' else '실거래'}")
            logger.info(f"계좌 수: {self.account_count}")
            logger.info(f"계좌 목록: {', '.join(self.account_list)}")
            
            return True
            
        except Exception as e:
            logger.exception("초기화 중 오류 발생")
            return False
    
    def set_account_password(self, password, use_auto=False):
        """
        계좌 비밀번호 설정
        Args:
            password (str): 계좌 비밀번호
            use_auto (bool): 자동 로그인 사용 여부
        """
        try:
            if use_auto:
                self.ocx.dynamicCall("KOA_Functions(QString, QString)", "ShowAccountWindow", "")
            else:
                self.ocx.dynamicCall("SetKHOpenAPILogic(QString, QString)", "SetAccountPassword", password)
            logger.info("계좌 비밀번호 설정 완료")
        except Exception as e:
            logger.exception("계좌 비밀번호 설정 중 오류 발생")
    
    def get_master_code_name(self, code):
        """
        종목코드의 한글명을 반환합니다.
        Args:
            code (str): 종목코드
        Returns:
            str: 종목명
        """
        return self.ocx.dynamicCall("GetMasterCodeName(QString)", code)
    
    def get_current_price(self, code):
        """
        종목의 현재가를 조회합니다.
        Args:
            code (str): 종목코드
        Returns:
            int: 현재가 (오류 시 None)
        """
        try:
            self.set_input_value("종목코드", code)
            
            # CommRqData 호출
            result = self.comm_rq_data("opt10001_req", "opt10001", 0, "0101")
            if result != 0:
                logger.error(f"현재가 조회 요청 실패: {result}")
                return None
            
            # 이벤트 루프 생성
            self._event_loop = QEventLoop()
            self._event_loop.exec_()
            
            # 현재가 반환
            price = self.get_comm_data("opt10001", "opt10001_req", 0, "현재가")
            return abs(int(price))  # 음수로 반환되는 경우가 있어 절대값 처리
            
        except Exception as e:
            logger.exception(f"현재가 조회 중 오류 발생: {code}")
            return None
    
    def _on_receive_tr_data(self, screen_no, rqname, trcode, record_name, next, unused1, unused2, unused3, unused4):
        """TR 수신 이벤트 처리"""
        try:
            if self._event_loop is not None:
                self._event_loop.exit()
        except Exception as e:
            logger.exception("TR 데이터 수신 처리 중 오류 발생") 