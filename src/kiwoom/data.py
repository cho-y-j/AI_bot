"""
Kiwoom API Data Module - 키움증권 API 데이터 조회 관련 기능
"""

from .base import KiwoomBase

class KiwoomData(KiwoomBase):
    """키움증권 API의 데이터 조회 관련 기능을 제공하는 클래스"""
    
    def __init__(self):
        """초기화"""
        super().__init__()
        
    def get_master_code_name(self, code):
        """종목코드의 한글명 조회
        
        Args:
            code (str): 종목코드
            
        Returns:
            str: 종목명
        """
        return self.ocx.dynamicCall("GetMasterCodeName(QString)", code)
        
    def get_master_listed_stock_cnt(self, code):
        """종목의 상장주식수 조회
        
        Args:
            code (str): 종목코드
            
        Returns:
            int: 상장주식수
        """
        return self.ocx.dynamicCall("GetMasterListedStockCnt(QString)", code)
        
    def get_master_construction(self, code):
        """종목의 감리구분 조회
        
        Args:
            code (str): 종목코드
            
        Returns:
            str: 감리구분 (정상, 투자주의, 투자경고, 투자위험, 투자주의환기종목)
        """
        return self.ocx.dynamicCall("GetMasterConstruction(QString)", code)
        
    def get_master_stock_state(self, code):
        """종목의 상태 조회
        
        Args:
            code (str): 종목코드
            
        Returns:
            str: 종목상태
        """
        return self.ocx.dynamicCall("GetMasterStockState(QString)", code)
        
    def get_current_price(self, code):
        """현재가 조회
        
        Args:
            code (str): 종목코드
            
        Returns:
            dict: 현재가 정보
        """
        self.received = False
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.ocx.dynamicCall("CommRqData(QString, QString, int, QString)",
                           "현재가조회", "opt10001", 0, "0101")
        self.tr_event_loop.exec_()
        
        if not self.received:
            raise RuntimeError("TR: 현재가조회 수신 실패")
            
        current_price = {
            'code': code,
            'name': self.get_master_code_name(code),
            'current_price': int(self.ocx.dynamicCall(
                "GetCommData(QString, QString, int, QString)",
                "opt10001", "현재가조회", 0, "현재가").strip().lstrip('-')),
            'volume': int(self.ocx.dynamicCall(
                "GetCommData(QString, QString, int, QString)",
                "opt10001", "현재가조회", 0, "거래량").strip()),
            'high': int(self.ocx.dynamicCall(
                "GetCommData(QString, QString, int, QString)",
                "opt10001", "현재가조회", 0, "고가").strip().lstrip('-')),
            'low': int(self.ocx.dynamicCall(
                "GetCommData(QString, QString, int, QString)",
                "opt10001", "현재가조회", 0, "저가").strip().lstrip('-')),
            'open': int(self.ocx.dynamicCall(
                "GetCommData(QString, QString, int, QString)",
                "opt10001", "현재가조회", 0, "시가").strip().lstrip('-')),
            'prev_close': int(self.ocx.dynamicCall(
                "GetCommData(QString, QString, int, QString)",
                "opt10001", "현재가조회", 0, "전일종가").strip().lstrip('-'))
        }
        
        return current_price
        
    def get_daily_chart(self, code, date_from, date_to):
        """일봉 데이터 조회
        
        Args:
            code (str): 종목코드
            date_from (str): 시작일자 (YYYYMMDD)
            date_to (str): 종료일자 (YYYYMMDD)
            
        Returns:
            list: 일봉 데이터 리스트
        """
        self.received = False
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "기준일자", date_to)
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")
        self.ocx.dynamicCall("CommRqData(QString, QString, int, QString)",
                           "일봉데이터조회", "opt10081", 0, "0101")
        self.tr_event_loop.exec_()
        
        if not self.received:
            raise RuntimeError("TR: 일봉데이터조회 수신 실패")
            
        daily_data = []
        rows = self.ocx.dynamicCall("GetRepeatCnt(QString, QString)",
                                  "opt10081", "일봉데이터조회")
        
        for i in range(rows):
            date = self.ocx.dynamicCall(
                "GetCommData(QString, QString, int, QString)",
                "opt10081", "일봉데이터조회", i, "일자").strip()
                
            if date < date_from:  # 요청 기간을 벗어난 데이터
                break
                
            data = {
                'date': date,
                'open': int(self.ocx.dynamicCall(
                    "GetCommData(QString, QString, int, QString)",
                    "opt10081", "일봉데이터조회", i, "시가").strip()),
                'high': int(self.ocx.dynamicCall(
                    "GetCommData(QString, QString, int, QString)",
                    "opt10081", "일봉데이터조회", i, "고가").strip()),
                'low': int(self.ocx.dynamicCall(
                    "GetCommData(QString, QString, int, QString)",
                    "opt10081", "일봉데이터조회", i, "저가").strip()),
                'close': int(self.ocx.dynamicCall(
                    "GetCommData(QString, QString, int, QString)",
                    "opt10081", "일봉데이터조회", i, "현재가").strip()),
                'volume': int(self.ocx.dynamicCall(
                    "GetCommData(QString, QString, int, QString)",
                    "opt10081", "일봉데이터조회", i, "거래량").strip())
            }
            daily_data.append(data)
            
        return daily_data 