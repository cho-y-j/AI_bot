"""
Kiwoom API Chart Module - 키움증권 API 차트 데이터 조회 관련 기능
"""

from datetime import datetime, timedelta
from .base import KiwoomBase

class KiwoomChart(KiwoomBase):
    """키움증권 API의 차트 데이터 조회 관련 기능을 제공하는 클래스"""
    
    def __init__(self):
        """초기화"""
        super().__init__()
        
    def get_daily_chart(self, code, start_date=None, end_date=None):
        """일봉 데이터 조회
        
        Args:
            code (str): 종목코드
            start_date (str, optional): 시작일자 (YYYYMMDD). 기본값은 None으로 과거 전체
            end_date (str, optional): 종료일자 (YYYYMMDD). 기본값은 None으로 현재일자
            
        Returns:
            list: 일봉 데이터 리스트
        """
        if end_date is None:
            end_date = datetime.now().strftime("%Y%m%d")
            
        if start_date is None:
            start_date = "19900101"
            
        self.received = False
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "기준일자", end_date)
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
                
            if date < start_date:  # 요청 기간을 벗어난 데이터
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
        
    def get_minute_chart(self, code, interval=1, start_date=None, end_date=None):
        """분봉 데이터 조회
        
        Args:
            code (str): 종목코드
            interval (int): 분봉 단위(1, 3, 5, 10, 15, 30, 45, 60)
            start_date (str, optional): 시작일자 (YYYYMMDD). 기본값은 None으로 과거 전체
            end_date (str, optional): 종료일자 (YYYYMMDD). 기본값은 None으로 현재일자
            
        Returns:
            list: 분봉 데이터 리스트
        """
        if interval not in [1, 3, 5, 10, 15, 30, 45, 60]:
            raise ValueError("올바른 분봉 단위가 아닙니다.")
            
        if end_date is None:
            end_date = datetime.now().strftime("%Y%m%d")
            
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
            
        self.received = False
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "틱범위", str(interval))
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "기준일자", end_date)
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")
        self.ocx.dynamicCall("CommRqData(QString, QString, int, QString)",
                           "분봉데이터조회", "opt10080", 0, "0101")
        self.tr_event_loop.exec_()
        
        if not self.received:
            raise RuntimeError("TR: 분봉데이터조회 수신 실패")
            
        minute_data = []
        rows = self.ocx.dynamicCall("GetRepeatCnt(QString, QString)",
                                  "opt10080", "분봉데이터조회")
        
        for i in range(rows):
            date = self.ocx.dynamicCall(
                "GetCommData(QString, QString, int, QString)",
                "opt10080", "분봉데이터조회", i, "체결시간").strip()
                
            if date[:8] < start_date:  # 요청 기간을 벗어난 데이터
                break
                
            data = {
                'date': date,
                'open': int(self.ocx.dynamicCall(
                    "GetCommData(QString, QString, int, QString)",
                    "opt10080", "분봉데이터조회", i, "시가").strip()),
                'high': int(self.ocx.dynamicCall(
                    "GetCommData(QString, QString, int, QString)",
                    "opt10080", "분봉데이터조회", i, "고가").strip()),
                'low': int(self.ocx.dynamicCall(
                    "GetCommData(QString, QString, int, QString)",
                    "opt10080", "분봉데이터조회", i, "저가").strip()),
                'close': int(self.ocx.dynamicCall(
                    "GetCommData(QString, QString, int, QString)",
                    "opt10080", "분봉데이터조회", i, "현재가").strip()),
                'volume': int(self.ocx.dynamicCall(
                    "GetCommData(QString, QString, int, QString)",
                    "opt10080", "분봉데이터조회", i, "거래량").strip())
            }
            minute_data.append(data)
            
        return minute_data 