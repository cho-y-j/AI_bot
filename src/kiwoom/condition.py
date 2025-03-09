"""
Kiwoom API Condition Module - 키움증권 API 조건검색 관련 기능
"""

from .base import KiwoomBase

class KiwoomCondition(KiwoomBase):
    """키움증권 API의 조건검색 관련 기능을 제공하는 클래스"""
    
    def __init__(self):
        """초기화"""
        super().__init__()
        self.condition_loaded = False
        self.condition_list = {}
        self.condition_stocks = []
        
    def get_condition_list(self):
        """조건식 목록 조회
        
        Returns:
            dict: 조건식 목록 {인덱스: 조건식이름}
        """
        if not self.condition_loaded:
            self.condition_loaded = self.ocx.dynamicCall("GetConditionLoad()")
            if not self.condition_loaded:
                raise RuntimeError("조건식 목록 로드 실패")
                
        data = self.ocx.dynamicCall("GetConditionNameList()")
        conditions = data.split(";")[:-1]
        
        for condition in conditions:
            index, name = condition.split("^")
            self.condition_list[int(index)] = name
            
        return self.condition_list
        
    def send_condition(self, screen_no, condition_name, index, search_type=0):
        """조건검색 요청
        
        Args:
            screen_no (str): 화면번호
            condition_name (str): 조건식 이름
            index (int): 조건식 인덱스
            search_type (int): 조회구분(0: 일반조회, 1: 실시간조회, 2: 연속조회)
            
        Returns:
            bool: 조건검색 요청 성공 여부
        """
        if not self.condition_loaded:
            self.get_condition_list()
            
        self.condition_stocks = []
        result = self.ocx.dynamicCall(
            "SendCondition(QString, QString, int, int)",
            screen_no, condition_name, index, search_type)
            
        if not result:
            raise RuntimeError("조건검색 요청 실패")
            
        return result
        
    def _handler_condition_ver(self, ret, msg):
        """조건식 목록 요청에 대한 이벤트"""
        if not ret:
            self.condition_loaded = False
            self.logger.error("조건식 목록 요청 실패")
            
    def _handler_tr_condition(self, screen_no, codes, condition_name, index, next):
        """조건검색 결과 수신 이벤트"""
        if codes == "":
            return
            
        for code in codes.split(";"):
            if code == "":
                continue
            self.condition_stocks.append(code)
            
        self.logger.info(f"조건검색 결과: {condition_name}({index}): {len(self.condition_stocks)}종목")
        
    def _handler_real_condition(self, code, event_type, condition_name, condition_index):
        """실시간 조건검색 결과 수신 이벤트"""
        if event_type == "I":  # 편입
            if code not in self.condition_stocks:
                self.condition_stocks.append(code)
                self.logger.info(f"실시간 조건검색 편입: {code}")
        elif event_type == "D":  # 이탈
            if code in self.condition_stocks:
                self.condition_stocks.remove(code)
                self.logger.info(f"실시간 조건검색 이탈: {code}")
                
    def stop_condition(self, screen_no, condition_name, index):
        """조건검색 중지
        
        Args:
            screen_no (str): 화면번호
            condition_name (str): 조건식 이름
            index (int): 조건식 인덱스
        """
        self.ocx.dynamicCall("SendConditionStop(QString, QString, int)",
                           screen_no, condition_name, index) 