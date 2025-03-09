"""
Kiwoom API Account Module - 키움증권 API 계좌 관련 기능
"""
import logging
from PyQt5.QtCore import QEventLoop
from .base import KiwoomBase

logger = logging.getLogger(__name__)

class KiwoomAccount(KiwoomBase):
    """키움 API 계좌 관련 클래스"""
    
    def __init__(self):
        """초기화"""
        super().__init__()
        self._account_list = []
        self._deposit = 0
        self._account_data = {}
    
    def get_account_list(self):
        """
        보유 계좌 목록을 반환합니다.
        
        Returns:
            list: 계좌번호 리스트
        """
        if not self.get_connect_state():
            logger.error("키움 API 연결 상태가 아닙니다.")
            return []
        
        account_list = self.get_login_info("ACCNO")
        self._account_list = account_list.split(';')[:-1]
        return self._account_list
    
    def get_account_info(self, account_no):
        """
        계좌 정보를 조회합니다.
        
        Args:
            account_no: 계좌번호
        
        Returns:
            dict: 계좌 정보 딕셔너리
        """
        try:
            # TR 입력값 설정
            self.set_input_value("계좌번호", account_no)
            self.set_input_value("비밀번호", "")  # 공백: 사용자가 수동 입력
            self.set_input_value("비밀번호입력매체구분", "00")  # 00: 보안카드
            self.set_input_value("조회구분", "2")  # 2: 일반조회
            
            # TR 요청
            result = self.comm_rq_data("계좌평가잔고내역", "opw00018", 0, "0101")
            
            if result != 0:
                logger.error(f"계좌 정보 조회 요청 실패: {result}")
                return None
            
            # 이벤트 루프 생성
            self._event_loop = QEventLoop()
            self._event_loop.exec_()
            
            return self._account_data
        
        except Exception as e:
            logger.exception("계좌 정보 조회 중 오류 발생")
            return None
    
    def get_deposit(self, account_no):
        """
        예수금을 조회합니다.
        
        Args:
            account_no: 계좌번호
        
        Returns:
            int: 예수금
        """
        try:
            # TR 입력값 설정
            self.set_input_value("계좌번호", account_no)
            self.set_input_value("비밀번호", "")  # 공백: 사용자가 수동 입력
            self.set_input_value("비밀번호입력매체구분", "00")  # 00: 보안카드
            
            # TR 요청
            result = self.comm_rq_data("예수금상세현황", "opw00001", 0, "0102")
            
            if result != 0:
                logger.error(f"예수금 조회 요청 실패: {result}")
                return 0
            
            # 이벤트 루프 생성
            self._event_loop = QEventLoop()
            self._event_loop.exec_()
            
            return self._deposit
        
        except Exception as e:
            logger.exception("예수금 조회 중 오류 발생")
            return 0
    
    def _on_receive_tr_data(self, screen_no, rqname, trcode, record_name, next, unused1, unused2, unused3, unused4):
        """
        TR 수신 이벤트 처리
        
        Args:
            screen_no: 화면번호
            rqname: 요청명
            trcode: TR 코드
            record_name: 레코드명
            next: 연속조회 유무
        """
        try:
            if rqname == "예수금상세현황":
                # 예수금 정보 처리
                deposit = self.get_comm_data(trcode, rqname, 0, "예수금")
                self._deposit = int(deposit)
                logger.debug(f"예수금: {self._deposit:,}")
            
            elif rqname == "계좌평가잔고내역":
                # 계좌 정보 처리
                account_data = {
                    '총매입금액': int(self.get_comm_data(trcode, rqname, 0, "총매입금액")),
                    '총평가금액': int(self.get_comm_data(trcode, rqname, 0, "총평가금액")),
                    '총평가손익금액': int(self.get_comm_data(trcode, rqname, 0, "총평가손익금액")),
                    '총수익률': float(self.get_comm_data(trcode, rqname, 0, "총수익률")),
                    '추정예탁자산': int(self.get_comm_data(trcode, rqname, 0, "추정예탁자산"))
                }
                
                # 보유 종목 정보
                rows = self.get_repeat_cnt(trcode, rqname)
                holdings = []
                
                for i in range(rows):
                    holding = {
                        '종목코드': self.get_comm_data(trcode, rqname, i, "종목코드").strip(),
                        '종목명': self.get_comm_data(trcode, rqname, i, "종목명").strip(),
                        '보유수량': int(self.get_comm_data(trcode, rqname, i, "보유수량")),
                        '매입가': int(self.get_comm_data(trcode, rqname, i, "매입가")),
                        '현재가': int(self.get_comm_data(trcode, rqname, i, "현재가")),
                        '평가손익': int(self.get_comm_data(trcode, rqname, i, "평가손익")),
                        '수익률': float(self.get_comm_data(trcode, rqname, i, "수익률"))
                    }
                    holdings.append(holding)
                
                account_data['보유종목'] = holdings
                self._account_data = account_data
                
                logger.debug(f"계좌 정보: {account_data}")
        
        except Exception as e:
            logger.exception("TR 데이터 처리 중 오류 발생")
        
        finally:
            # 이벤트 루프 종료
            if self._event_loop is not None:
                self._event_loop.exit() 