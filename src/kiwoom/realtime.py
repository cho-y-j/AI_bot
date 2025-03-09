"""
Kiwoom API Realtime Module - 키움증권 API 실시간 데이터 관련 기능
"""

from .base import KiwoomBase

class KiwoomRealtime(KiwoomBase):
    """키움증권 API의 실시간 데이터 관련 기능을 제공하는 클래스"""
    
    def __init__(self):
        """초기화"""
        super().__init__()
        self.fids = {
            '현재가': 10,
            '거래량': 15,
            '거래대금': 16,
            '시가': 20,
            '고가': 17,
            '저가': 18,
            '전일대비': 11,
            '등락율': 12,
            '누적거래량': 13,
            '누적거래대금': 14,
            '시가총액': 311,
            '장구분': 290,
            '전일거래량': 26,
            '거래회전율': 31,
            '전일종가': 10,
            '체결시간': 20,
            '체결량': 15,
            '시간외종가': 10,
            '호가시간': 21,
            '매도호가1': 41,
            '매수호가1': 51,
            '매도호가수량1': 61,
            '매수호가수량1': 71
        }
        
    def set_real_reg(self, screen_no, code_list, fid_list, real_type):
        """실시간 데이터 요청
        
        Args:
            screen_no (str): 화면번호
            code_list (str): 종목코드 리스트 (종목코드1;종목코드2;...)
            fid_list (str): FID 번호 리스트 (FID1;FID2;...)
            real_type (str): 실시간 타입 (0: 해제, 1: 등록)
            
        Returns:
            int: 실시간 등록 결과
        """
        return self.ocx.dynamicCall(
            "SetRealReg(QString, QString, QString, QString)",
            [screen_no, code_list, fid_list, real_type])
            
    def set_real_remove(self, screen_no, code_list):
        """실시간 데이터 해제
        
        Args:
            screen_no (str): 화면번호
            code_list (str): 종목코드 리스트 (종목코드1;종목코드2;...)
        """
        self.ocx.dynamicCall("SetRealRemove(QString, QString)",
                           [screen_no, code_list])
                           
    def get_comm_real_data(self, code, fid):
        """실시간 데이터 조회
        
        Args:
            code (str): 종목코드
            fid (int): FID
            
        Returns:
            str: 수신 데이터
        """
        return self.ocx.dynamicCall("GetCommRealData(QString, int)",
                                  [code, fid]).strip()
                                  
    def _handler_real_data(self, code, real_type, real_data):
        """실시간 데이터 수신 이벤트
        
        Args:
            code (str): 종목코드
            real_type (str): 실시간 타입
            real_data (str): 실시간 데이터
        """
        if real_type == "주식시세":
            # 현재가 실시간 데이터 처리
            current_price = abs(int(self.get_comm_real_data(code, self.fids['현재가'])))
            volume = int(self.get_comm_real_data(code, self.fids['거래량']))
            trade_amount = int(self.get_comm_real_data(code, self.fids['거래대금']))
            open_price = abs(int(self.get_comm_real_data(code, self.fids['시가'])))
            high_price = abs(int(self.get_comm_real_data(code, self.fids['고가'])))
            low_price = abs(int(self.get_comm_real_data(code, self.fids['저가'])))
            change = float(self.get_comm_real_data(code, self.fids['등락율']))
            
            self.logger.debug(f"실시간 시세: {code} "
                            f"현재가: {current_price}, "
                            f"거래량: {volume}, "
                            f"거래대금: {trade_amount}, "
                            f"시가: {open_price}, "
                            f"고가: {high_price}, "
                            f"저가: {low_price}, "
                            f"등락율: {change}%")
                            
        elif real_type == "주식체결":
            # 체결 실시간 데이터 처리
            current_price = abs(int(self.get_comm_real_data(code, self.fids['현재가'])))
            volume = int(self.get_comm_real_data(code, self.fids['체결량']))
            time = self.get_comm_real_data(code, self.fids['체결시간'])
            
            self.logger.debug(f"실시간 체결: {code} "
                            f"체결가: {current_price}, "
                            f"체결량: {volume}, "
                            f"체결시간: {time}")
                            
        elif real_type == "주식호가잔량":
            # 호가 실시간 데이터 처리
            time = self.get_comm_real_data(code, self.fids['호가시간'])
            ask_price = abs(int(self.get_comm_real_data(code, self.fids['매도호가1'])))
            bid_price = abs(int(self.get_comm_real_data(code, self.fids['매수호가1'])))
            ask_volume = int(self.get_comm_real_data(code, self.fids['매도호가수량1']))
            bid_volume = int(self.get_comm_real_data(code, self.fids['매수호가수량1']))
            
            self.logger.debug(f"실시간 호가: {code} "
                            f"시간: {time}, "
                            f"매도호가1: {ask_price}, "
                            f"매수호가1: {bid_price}, "
                            f"매도수량1: {ask_volume}, "
                            f"매수수량1: {bid_volume}") 