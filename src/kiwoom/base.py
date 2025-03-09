"""
Kiwoom API Base Module - 키움증권 API 기본 연결 및 이벤트 처리
"""

import os
import sys
import logging
from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtCore import QEventLoop, QTime

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
        """실시간 데이터 수신 이벤트 처리"""
        try:
            if real_type == "주식시세" or real_type == "주식체결":
                # 현재가 (음수면 하락, 양수면 상승)
                current_price = self.ocx.dynamicCall("GetCommRealData(QString, int)", code, 10)
                current_price = abs(int(current_price))
                
                # 전일대비
                diff = self.ocx.dynamicCall("GetCommRealData(QString, int)", code, 11)
                diff = int(diff)
                
                # 등락율
                diff_percent = self.ocx.dynamicCall("GetCommRealData(QString, int)", code, 12)
                diff_percent = float(diff_percent)
                
                # 거래량
                volume = self.ocx.dynamicCall("GetCommRealData(QString, int)", code, 15)
                volume = int(volume)
                
                # 거래대금
                amount = self.ocx.dynamicCall("GetCommRealData(QString, int)", code, 16)
                amount = int(amount)
                
                # 데이터 전달
                data = {
                    "현재가": current_price,
                    "전일대비": diff,
                    "등락율": diff_percent,
                    "거래량": volume,
                    "거래대금": amount
                }
                
                # 콜백 실행
                if code in self.real_data_handlers:
                    self.real_data_handlers[code](data)
                
                logger.debug(f"실시간 데이터 수신: {code} - {data}")
                
        except Exception as e:
            logger.error(f"실시간 데이터 처리 중 오류 발생: {e}")
    
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
        
        # 관심종목 저장소
        self.favorites = {}  # {그룹명: [{종목코드, 종목명, ...}, ...], ...}
        
        # 관심종목 파일 경로
        self.favorites_file = "data/favorites.json"
        
        # 저장된 관심종목 로드
        self.load_favorites()
        
        # 실시간 데이터 콜백 등록
        self.real_data_handlers = {}
        self.ocx.OnReceiveRealData.connect(self._on_receive_real_data)
    
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
    
    def get_market_state(self):
        """
        현재 장 상태를 반환합니다.
        Returns:
            str: '장전', '장중', '장후' 중 하나
        """
        try:
            current_time = QTime.currentTime()
            
            # 장 시작 시간 (9:00) 이전
            if current_time < QTime(9, 0, 0):
                return "장전"
            
            # 장 종료 시간 (15:30) 이후
            elif current_time > QTime(15, 30, 0):
                return "장후"
            
            # 장중
            else:
                return "장중"
                
        except Exception as e:
            logger.error(f"장 상태 확인 중 오류 발생: {e}")
            return "장후"
    
    def set_real_time_data(self, codes, fids):
        """
        실시간 데이터 요청을 등록합니다.
        Args:
            codes (list): 종목코드 리스트
            fids (list): 실시간 FID 리스트
        """
        try:
            # 화면번호는 실시간 시세 전용으로 '9999' 사용
            screen_no = "9999"
            
            # 실시간 등록
            codes_str = ";".join(codes)
            fids_str = ";".join([
                "10",  # 현재가
                "11",  # 전일대비
                "12",  # 등락율
                "15",  # 거래량
                "16",  # 거래대금
                "13",  # 누적거래량
                "14"   # 누적거래대금
            ])
            
            # 기존 등록 해제
            self.ocx.dynamicCall("SetRealRemove(QString, QString)", screen_no, "ALL")
            
            # 실시간 등록
            result = self.ocx.dynamicCall(
                "SetRealReg(QString, QString, QString, QString)", 
                screen_no, codes_str, fids_str, "0"
            )
            
            if result == 0:
                logger.info(f"실시간 데이터 등록 성공: {len(codes)}개 종목")
            else:
                logger.error(f"실시간 데이터 등록 실패: {result}")
            
        except Exception as e:
            logger.error(f"실시간 데이터 등록 중 오류 발생: {e}")
    
    def disset_real_time_data(self, codes):
        """
        실시간 데이터 요청을 해제합니다.
        Args:
            codes (list): 종목코드 리스트
        """
        try:
            # 화면번호는 실시간 시세 전용으로 '9999' 사용
            screen_no = "9999"
            
            # 실시간 해제
            for code in codes:
                self.ocx.dynamicCall(
                    "SetRealRemove(QString, QString)", 
                    screen_no, code
                )
                
                # 콜백 제거
                if code in self.real_data_handlers:
                    del self.real_data_handlers[code]
            
            logger.info(f"실시간 데이터 해제: {len(codes)}개 종목")
            
        except Exception as e:
            logger.error(f"실시간 데이터 해제 중 오류 발생: {e}")
    
    def get_current_price(self, code):
        """
        현재가 조회
        Args:
            code (str): 종목 코드
        Returns:
            dict: 현재가 정보 (현재가, 등락율, 거래량 등)
        """
        try:
            market_state = self.get_market_state()
            
            # TR 요청
            self.set_input_value("종목코드", code)
            result = self.comm_rq_data("주식기본정보", "opt10001", 0, "0101")
            
            if result != 0:
                logger.error(f"현재가 조회 실패: {result}")
                return None
            
            # 데이터 반환
            current_price = abs(int(self.get_comm_data("주식기본정보", "현재가")))
            diff = int(self.get_comm_data("주식기본정보", "전일대비"))
            diff_percent = float(self.get_comm_data("주식기본정보", "등락율"))
            volume = int(self.get_comm_data("주식기본정보", "거래량"))
            amount = int(self.get_comm_data("주식기본정보", "거래대금"))
            
            data = {
                "현재가": current_price,
                "전일대비": diff,
                "등락률": diff_percent,
                "거래량": volume,
                "거래대금": amount,
                "market_state": market_state
            }
            
            return data
            
        except Exception as e:
            logger.error(f"현재가 조회 중 오류 발생: {e}")
            return None
    
    def _on_receive_tr_data(self, screen_no, rqname, trcode, record_name, next, unused1, unused2, unused3, unused4):
        """TR 수신 이벤트 처리"""
        try:
            if self._event_loop is not None:
                self._event_loop.exit()
        except Exception as e:
            logger.exception("TR 데이터 수신 처리 중 오류 발생") 
    
    def search_stock(self, keyword):
        """
        종목을 검색합니다.
        
        Args:
            keyword (str): 검색어 (종목코드 또는 종목명)
            
        Returns:
            list: 검색된 종목 리스트 [{종목코드, 종목명, 시장구분}, ...]
        """
        try:
            results = []
            
            # 종목코드로 검색
            if keyword.isdigit():
                name = self.get_master_code_name(keyword)
                if name:
                    market = "코스피" if keyword in self.get_code_list("0") else "코스닥"
                    results.append({
                        "종목코드": keyword,
                        "종목명": name,
                        "시장구분": market
                    })
                    return results
            
            # 종목명으로 검색
            # 코스피 종목 검색
            for code in self.get_code_list("0"):
                name = self.get_master_code_name(code)
                if keyword.lower() in name.lower():
                    results.append({
                        "종목코드": code,
                        "종목명": name,
                        "시장구분": "코스피"
                    })
            
            # 코스닥 종목 검색
            for code in self.get_code_list("10"):
                name = self.get_master_code_name(code)
                if keyword.lower() in name.lower():
                    results.append({
                        "종목코드": code,
                        "종목명": name,
                        "시장구분": "코스닥"
                    })
            
            return results
            
        except Exception as e:
            logger.exception(f"종목 검색 중 오류 발생: {keyword}")
            return [] 
    
    def get_code_list(self, market):
        """
        시장별 종목코드 리스트를 반환합니다.
        
        Args:
            market (str): 시장구분
                - 0: 코스피
                - 10: 코스닥
                - 3: ELW
                - 8: ETF
                - 50: KONEX
                - 4: 뮤추얼펀드
                - 5: 신주인수권
                - 6: 리츠
                - 9: 하이얼펀드
                - 30: K-OTC
        
        Returns:
            list: 종목코드 리스트
        """
        try:
            code_list = self.ocx.dynamicCall("GetCodeListByMarket(QString)", market)
            codes = code_list.split(';')
            return [code for code in codes if code.strip()]  # 빈 문자열 제거
            
        except Exception as e:
            logger.exception(f"시장별 종목코드 조회 중 오류 발생: {market}")
            return [] 
    
    def save_favorites(self):
        """관심종목을 파일에 저장합니다."""
        try:
            import json
            import os
            
            # data 디렉토리가 없으면 생성
            os.makedirs("data", exist_ok=True)
            
            # JSON 파일로 저장
            with open(self.favorites_file, 'w', encoding='utf-8') as f:
                json.dump(self.favorites, f, ensure_ascii=False, indent=2)
            
            logger.info("관심종목 저장 완료")
            
        except Exception as e:
            logger.exception("관심종목 저장 중 오류 발생")
    
    def load_favorites(self):
        """저장된 관심종목을 로드합니다."""
        try:
            import json
            import os
            
            if os.path.exists(self.favorites_file):
                with open(self.favorites_file, 'r', encoding='utf-8') as f:
                    self.favorites = json.load(f)
                logger.info("관심종목 로드 완료")
            else:
                # 기본 그룹 생성
                self.favorites = {"관심종목1": []}
                logger.info("새로운 관심종목 목록 생성")
            
        except Exception as e:
            logger.exception("관심종목 로드 중 오류 발생")
            # 오류 발생 시 빈 상태로 시작
            self.favorites = {"관심종목1": []}
    
    def add_favorite(self, group, code, name):
        """
        관심종목을 추가합니다.
        
        Args:
            group (str): 관심종목 그룹명
            code (str): 종목코드
            name (str): 종목명
        """
        try:
            # 그룹이 없으면 생성
            if group not in self.favorites:
                self.favorites[group] = []
            
            # 이미 있는 종목인지 확인
            for stock in self.favorites[group]:
                if stock['종목코드'] == code:
                    return  # 이미 있으면 무시
            
            # 종목 정보 가져오기
            price_info = self.get_current_price(code)
            
            # 관심종목에 추가
            stock_info = {
                '종목코드': code,
                '종목명': name,
                '현재가': price_info['현재가'] if price_info else 0,
                '전일대비': price_info['전일대비'] if price_info else 0,
                '등락률': price_info['등락률'] if price_info else 0.0,
                '거래량': price_info['거래량'] if price_info else 0,
                '거래대금': price_info['거래대금'] if price_info else 0
            }
            
            self.favorites[group].append(stock_info)
            logger.info(f"관심종목 추가: {group} - {name}({code})")
            
            # 실시간 등록
            if self.get_market_state() == "장중":
                self.set_real_time_data([code], ["주식시세", "주식체결"])
            
            # 변경사항 저장
            self.save_favorites()
            
        except Exception as e:
            logger.exception(f"관심종목 추가 중 오류 발생: {group}, {code}")
            raise e
    
    def remove_favorite(self, group, code):
        """
        관심종목을 삭제합니다.
        
        Args:
            group (str): 관심종목 그룹명
            code (str): 종목코드
        """
        try:
            if group in self.favorites:
                self.favorites[group] = [
                    stock for stock in self.favorites[group] 
                    if stock['종목코드'] != code
                ]
                logger.info(f"관심종목 삭제: {group} - {code}")
                
                # 변경사항 저장
                self.save_favorites()
                
        except Exception as e:
            logger.exception(f"관심종목 삭제 중 오류 발생: {group}, {code}")
            raise e
    
    def get_favorites(self, group):
        """
        관심종목 목록을 반환합니다.
        
        Args:
            group (str): 관심종목 그룹명
            
        Returns:
            list: 관심종목 리스트 [{종목코드, 종목명, 현재가, ...}, ...]
        """
        try:
            if group in self.favorites:
                # 현재가 업데이트
                for stock in self.favorites[group]:
                    current_price = self.get_current_price(stock['종목코드'])
                    if current_price:
                        stock['현재가'] = current_price
                
                return self.favorites[group]
            return []
            
        except Exception as e:
            logger.exception(f"관심종목 조회 중 오류 발생: {group}")
            return [] 

    def _get_comm_data(self, tr_code, field_name, index=0):
        """TR 데이터 조회"""
        return self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                  tr_code, "", index, field_name) 