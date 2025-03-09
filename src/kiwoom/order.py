"""
Kiwoom API Order Module - 키움증권 API 주문 관련 기능
"""
import logging
import json
import os
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict
from PyQt5.QtCore import QEventLoop, pyqtSignal
from .base import KiwoomBase

logger = logging.getLogger(__name__)

class OrderStatus:
    """주문 상태 코드"""
    RECEIPT = "00"        # 주문접수
    PROCESSING = "01"     # 주문처리중
    COMPLETE = "02"      # 주문완료
    CONFIRMED = "03"     # 주문확인
    REJECTED = "04"      # 주문거부
    CANCELLED = "05"     # 주문취소
    MODIFIED = "06"      # 주문정정
    
class KiwoomOrder(KiwoomBase):
    """키움 API 주문 관련 클래스"""
    
    # 실시간 이벤트 시그널
    order_executed = pyqtSignal(dict)  # 주문 체결 시그널
    balance_updated = pyqtSignal(dict)  # 잔고 변경 시그널
    order_status_changed = pyqtSignal(dict)  # 주문 상태 변경 시그널
    
    # 주문유형
    ORDER_TYPE_NEW = 1      # 신규매수/매도
    ORDER_TYPE_MODIFY = 2   # 정정
    ORDER_TYPE_CANCEL = 3   # 취소
    
    # 호가구분
    PRICE_TYPE_LIMIT = "00"  # 지정가
    PRICE_TYPE_MARKET = "03"  # 시장가
    
    # FID 상수
    FID_ACCOUNT_NO = 9201       # 계좌번호
    FID_ORDER_NO = 9203         # 주문번호
    FID_CODE = 9001            # 종목코드
    FID_NAME = 302             # 종목명
    FID_ORDER_TYPE = 905       # 주문구분
    FID_ORDER_QTY = 900        # 주문수량
    FID_ORDER_PRICE = 901      # 주문가격
    FID_EXECUTED_QTY = 911     # 체결수량
    FID_EXECUTED_PRICE = 910   # 체결가격
    FID_ORDER_STATUS = 913     # 주문상태
    FID_TRADE_TIME = 908       # 체결시간
    FID_TRADE_NO = 909         # 체결번호
    FID_BALANCE_QTY = 930      # 보유수량
    FID_BUYABLE_QTY = 933      # 주문가능수량
    FID_CURRENT_PRICE = 10     # 현재가
    FID_PROFIT_LOSS = 8019     # 손익률
    
    def __init__(self):
        """초기화"""
        super().__init__()
        self._order_result = {}
        self._order_history = []
        self._outstanding_orders = []
        self._real_time_enabled = False
        self._monitored_orders = defaultdict(dict)  # 모니터링 중인 주문 {주문번호: 주문정보}
        self._order_status_history = defaultdict(list)  # 주문 상태 이력 {주문번호: [상태변경이력]}
        self._auto_cancel_orders = {}  # 자동 취소 설정 {주문번호: 취소조건}
        self._auto_modify_orders = {}  # 자동 정정 설정 {주문번호: 정정조건}
        
        # 주문 이력 저장 설정
        self._history_dir = "data/order_history"
        self._daily_history_file = None
        self._ensure_history_dir()
    
    def _ensure_history_dir(self):
        """주문 이력 저장 디렉토리를 생성합니다."""
        if not os.path.exists(self._history_dir):
            os.makedirs(self._history_dir)
            logger.info(f"주문 이력 디렉토리 생성: {self._history_dir}")
    
    def _get_daily_history_file(self):
        """오늘 날짜의 주문 이력 파일명을 반환합니다."""
        today = datetime.now().strftime("%Y%m%d")
        return os.path.join(self._history_dir, f"order_history_{today}.json")
    
    def save_order_history(self, order_data):
        """
        주문 이력을 파일로 저장합니다.
        
        Args:
            order_data: 주문 정보
        """
        try:
            filename = self._get_daily_history_file()
            
            # 기존 데이터 로드
            history = []
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            
            # 타임스탬프 추가
            order_data['저장시각'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 새로운 주문 추가
            history.append(order_data)
            
            # 파일 저장
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"주문 이력 저장 완료: {filename}")
        
        except Exception as e:
            logger.exception("주문 이력 저장 중 오류 발생")
    
    def analyze_order_history(self, days=7):
        """
        주문 이력을 분석합니다.
        
        Args:
            days: 분석할 기간 (일)
        
        Returns:
            dict: 분석 결과
        """
        try:
            # 분석 기간 설정
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # 데이터 수집
            all_orders = []
            for date in pd.date_range(start_date, end_date):
                filename = os.path.join(self._history_dir, f"order_history_{date.strftime('%Y%m%d')}.json")
                if os.path.exists(filename):
                    with open(filename, 'r', encoding='utf-8') as f:
                        orders = json.load(f)
                        all_orders.extend(orders)
            
            if not all_orders:
                return {"message": "분석할 주문 이력이 없습니다."}
            
            # DataFrame 생성
            df = pd.DataFrame(all_orders)
            
            # 기본 통계
            analysis = {
                "기간": f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}",
                "총_거래횟수": len(df),
                "매수_거래횟수": len(df[df['주문구분'].str.contains('매수')]),
                "매도_거래횟수": len(df[df['주문구분'].str.contains('매도')]),
                "평균_거래금액": int(df['주문가격'].mean()),
                "최대_거래금액": int(df['주문가격'].max()),
                "최소_거래금액": int(df['주문가격'].min()),
                "총_거래금액": int(df['주문가격'].sum())
            }
            
            # 종목별 통계
            stock_stats = df.groupby('종목명').agg({
                '주문번호': 'count',
                '주문가격': ['mean', 'sum']
            }).reset_index()
            stock_stats.columns = ['종목명', '거래횟수', '평균가격', '총거래금액']
            
            analysis['종목별_통계'] = stock_stats.to_dict('records')
            
            # 시간대별 거래 패턴
            df['시간'] = pd.to_datetime(df['주문시간'], format='%H%M%S').dt.hour
            time_pattern = df.groupby('시간').size().to_dict()
            analysis['시간대별_거래횟수'] = time_pattern
            
            # 성공/실패율
            status_counts = df['주문상태'].value_counts()
            analysis['주문상태_통계'] = status_counts.to_dict()
            
            return analysis
        
        except Exception as e:
            logger.exception("주문 이력 분석 중 오류 발생")
            return {"error": str(e)}
    
    def get_trading_summary(self, days=1):
        """
        거래 요약 정보를 조회합니다.
        
        Args:
            days: 조회 기간 (일)
        
        Returns:
            dict: 거래 요약 정보
        """
        try:
            # 기간 설정
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # 데이터 수집
            all_orders = []
            for date in pd.date_range(start_date, end_date):
                filename = os.path.join(self._history_dir, f"order_history_{date.strftime('%Y%m%d')}.json")
                if os.path.exists(filename):
                    with open(filename, 'r', encoding='utf-8') as f:
                        orders = json.load(f)
                        all_orders.extend(orders)
            
            if not all_orders:
                return {"message": "거래 내역이 없습니다."}
            
            # DataFrame 생성
            df = pd.DataFrame(all_orders)
            
            # 요약 정보 생성
            summary = {
                "기간": f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}",
                "총_거래횟수": len(df),
                "체결_거래횟수": len(df[df['주문상태'] == OrderStatus.COMPLETE]),
                "실패_거래횟수": len(df[df['주문상태'] == OrderStatus.REJECTED]),
                "취소_거래횟수": len(df[df['주문상태'] == OrderStatus.CANCELLED]),
                "총_거래금액": int(df['주문가격'].sum()),
                "평균_거래금액": int(df['주문가격'].mean()),
                "거래_종목수": df['종목명'].nunique()
            }
            
            return summary
        
        except Exception as e:
            logger.exception("거래 요약 조회 중 오류 발생")
            return {"error": str(e)}
    
    def enable_real_time(self, enable=True):
        """
        실시간 체결 정보 수신을 활성화/비활성화합니다.
        
        Args:
            enable: 활성화 여부
        """
        if enable and not self._real_time_enabled:
            self.ocx.dynamicCall("SetRealReg(QString, QString, QString, QString)", 
                               ["0150", "", "9201;9203;9001;302;905;900;901;911;910;913;908;909", "0"])
            self._real_time_enabled = True
            logger.info("실시간 체결 정보 수신 시작")
        elif not enable and self._real_time_enabled:
            self.ocx.dynamicCall("SetRealRemove(QString, QString)", ["0150", ""])
            self._real_time_enabled = False
            logger.info("실시간 체결 정보 수신 중단")
    
    def monitor_order(self, order_no):
        """
        주문을 모니터링 대상에 추가합니다.
        
        Args:
            order_no: 주문번호
        """
        if order_no not in self._monitored_orders:
            self._monitored_orders[order_no] = {
                '시작시각': datetime.now(),
                '상태': None,
                '체결수량': 0,
                '미체결수량': 0
            }
            logger.info(f"주문 모니터링 시작: {order_no}")
    
    def stop_monitor_order(self, order_no):
        """
        주문 모니터링을 중단합니다.
        
        Args:
            order_no: 주문번호
        """
        if order_no in self._monitored_orders:
            del self._monitored_orders[order_no]
            logger.info(f"주문 모니터링 중단: {order_no}")
    
    def get_order_status_history(self, order_no):
        """
        주문의 상태 변경 이력을 조회합니다.
        
        Args:
            order_no: 주문번호
        
        Returns:
            list: 상태 변경 이력 리스트
        """
        return self._order_status_history.get(order_no, [])
    
    def _update_order_status(self, order_no, status_data):
        """
        주문 상태를 업데이트하고 필요한 알림을 발생시킵니다.
        
        Args:
            order_no: 주문번호
            status_data: 상태 정보
        """
        try:
            if order_no not in self._monitored_orders:
                return
            
            order_info = self._monitored_orders[order_no]
            prev_status = order_info.get('상태')
            curr_status = status_data.get('주문상태')
            
            # 상태가 변경된 경우
            if prev_status != curr_status:
                # 상태 이력 기록
                status_history = {
                    '시각': datetime.now(),
                    '이전상태': prev_status,
                    '현재상태': curr_status,
                    '체결수량': status_data.get('체결수량', 0),
                    '미체결수량': status_data.get('미체결수량', 0)
                }
                self._order_status_history[order_no].append(status_history)
                
                # 주문 정보 업데이트
                order_info.update({
                    '상태': curr_status,
                    '체결수량': status_data.get('체결수량', 0),
                    '미체결수량': status_data.get('미체결수량', 0),
                    '마지막업데이트': datetime.now()
                })
                
                # 상태 변경 알림
                notification = {
                    '주문번호': order_no,
                    '종목명': status_data.get('종목명', ''),
                    '상태': self._get_status_description(curr_status),
                    '체결수량': status_data.get('체결수량', 0),
                    '미체결수량': status_data.get('미체결수량', 0)
                }
                
                # 시그널 발생
                self.order_status_changed.emit(notification)
                
                # 로그 기록
                logger.info(f"주문상태변경: {notification['종목명']} - {notification['상태']}, "
                           f"체결: {notification['체결수량']}주, 미체결: {notification['미체결수량']}주")
                
                # 주문 완료 시 모니터링 중단
                if curr_status in [OrderStatus.COMPLETE, OrderStatus.REJECTED, OrderStatus.CANCELLED]:
                    self.stop_monitor_order(order_no)
                
                # 자동 주문 처리
                if curr_status not in [OrderStatus.COMPLETE, OrderStatus.REJECTED, OrderStatus.CANCELLED]:
                    current_price = status_data.get('체결가격') or status_data.get('주문가격')
                    self._process_auto_orders(order_no, current_price)
        
        except Exception as e:
            logger.exception(f"주문 상태 업데이트 중 오류 발생: {order_no}")
    
    def _get_status_description(self, status_code):
        """
        주문 상태 코드에 대한 설명을 반환합니다.
        
        Args:
            status_code: 상태 코드
        
        Returns:
            str: 상태 설명
        """
        status_map = {
            OrderStatus.RECEIPT: "주문접수",
            OrderStatus.PROCESSING: "주문처리중",
            OrderStatus.COMPLETE: "주문완료",
            OrderStatus.CONFIRMED: "주문확인",
            OrderStatus.REJECTED: "주문거부",
            OrderStatus.CANCELLED: "주문취소",
            OrderStatus.MODIFIED: "주문정정"
        }
        return status_map.get(status_code, "알수없음")
    
    def _on_receive_chejan_data(self, gubun, item_cnt, fid_list):
        """체결잔고 데이터를 수신합니다."""
        try:
            if gubun == "0":  # 주문체결
                # 주문체결 정보 파싱
                execution_data = {
                    '계좌번호': self._get_chejan_data(self.FID_ACCOUNT_NO),
                    '주문번호': self._get_chejan_data(self.FID_ORDER_NO),
                    '종목코드': self._get_chejan_data(self.FID_CODE),
                    '종목명': self._get_chejan_data(self.FID_NAME),
                    '주문구분': self._get_chejan_data(self.FID_ORDER_TYPE),
                    '주문수량': int(self._get_chejan_data(self.FID_ORDER_QTY) or 0),
                    '주문가격': int(self._get_chejan_data(self.FID_ORDER_PRICE) or 0),
                    '체결수량': int(self._get_chejan_data(self.FID_EXECUTED_QTY) or 0),
                    '체결가격': int(self._get_chejan_data(self.FID_EXECUTED_PRICE) or 0),
                    '주문상태': self._get_chejan_data(self.FID_ORDER_STATUS),
                    '체결시간': self._get_chejan_data(self.FID_TRADE_TIME),
                    '체결번호': self._get_chejan_data(self.FID_TRADE_NO)
                }
                
                # 미체결수량 계산
                execution_data['미체결수량'] = execution_data['주문수량'] - execution_data['체결수량']
                
                # 주문 이력 저장
                self.save_order_history(execution_data)
                
                # 주문상태 업데이트
                self._update_order_status(execution_data['주문번호'], execution_data)
                
                # 주문체결 시그널 발생
                self.order_executed.emit(execution_data)
                logger.info(f"주문체결: {execution_data['종목명']} - {execution_data['주문구분']} "
                          f"{execution_data['체결수량']}주 @ {execution_data['체결가격']:,}원")
            
            elif gubun == "1":  # 잔고
                # 잔고 정보 파싱
                balance_data = {
                    '계좌번호': self._get_chejan_data(self.FID_ACCOUNT_NO),
                    '종목코드': self._get_chejan_data(self.FID_CODE),
                    '종목명': self._get_chejan_data(self.FID_NAME),
                    '보유수량': int(self._get_chejan_data(self.FID_BALANCE_QTY) or 0),
                    '주문가능수량': int(self._get_chejan_data(self.FID_BUYABLE_QTY) or 0),
                    '현재가': int(self._get_chejan_data(self.FID_CURRENT_PRICE) or 0),
                    '손익률': float(self._get_chejan_data(self.FID_PROFIT_LOSS) or 0)
                }
                
                # 잔고변경 시그널 발생
                self.balance_updated.emit(balance_data)
                logger.info(f"잔고변경: {balance_data['종목명']} - "
                          f"보유: {balance_data['보유수량']}주, "
                          f"손익률: {balance_data['손익률']:.2f}%")
        
        except Exception as e:
            logger.exception("체결잔고 데이터 처리 중 오류 발생")
    
    def _get_chejan_data(self, fid):
        """
        체결잔고 데이터를 조회합니다.
        
        Args:
            fid: FID
        
        Returns:
            str: 데이터 값
        """
        return self.ocx.dynamicCall("GetChejanData(int)", [fid]).strip()
    
    def send_order(self, rqname, screen_no, account_no, order_type, code, quantity, price, price_type, order_no=""):
        """
        주문을 전송합니다.
        
        Args:
            rqname: 요청명
            screen_no: 화면번호
            account_no: 계좌번호
            order_type: 주문유형 (1:신규매수, 2:신규매도, 3:매수취소, 4:매도취소, 5:매수정정, 6:매도정정)
            code: 종목코드
            quantity: 주문수량
            price: 주문가격
            price_type: 호가구분 (00:지정가, 03:시장가)
            order_no: 원주문번호 (정정/취소 시)
        
        Returns:
            str: 주문번호
        """
        try:
            # 연결 상태 확인
            if not self.get_connect_state():
                logger.error("키움 API 연결 상태가 아닙니다.")
                return ""
            
            # 주문 전송
            result = self.ocx.dynamicCall(
                "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                [rqname, screen_no, account_no, order_type, code, quantity, price, price_type, order_no]
            )
            
            if result == 0:
                logger.info(f"주문 전송 성공: {code} - {'매수' if order_type == 1 else '매도'} {quantity}주 @ {price:,}원")
            else:
                logger.error(f"주문 전송 실패: {result}")
            
            # 이벤트 루프 생성
            self._event_loop = QEventLoop()
            self._event_loop.exec_()
            
            return self._order_result.get('주문번호', '')
        
        except Exception as e:
            logger.exception("주문 전송 중 오류 발생")
            return ""
    
    def send_market_buy_order(self, code, quantity, account_no, screen_no="0000"):
        """
        시장가 매수 주문을 전송합니다.
        
        Args:
            code: 종목코드
            quantity: 주문수량
            account_no: 계좌번호
            screen_no: 화면번호
        
        Returns:
            str: 주문번호
        """
        return self.send_order(
            "시장가매수", screen_no, account_no,
            1, code, quantity, 0, self.PRICE_TYPE_MARKET
        )
    
    def send_market_sell_order(self, code, quantity, account_no, screen_no="0000"):
        """
        시장가 매도 주문을 전송합니다.
        
        Args:
            code: 종목코드
            quantity: 주문수량
            account_no: 계좌번호
            screen_no: 화면번호
        
        Returns:
            str: 주문번호
        """
        return self.send_order(
            "시장가매도", screen_no, account_no,
            2, code, quantity, 0, self.PRICE_TYPE_MARKET
        )
    
    def send_limit_buy_order(self, code, quantity, price, account_no, screen_no="0000"):
        """
        지정가 매수 주문을 전송합니다.
        
        Args:
            code: 종목코드
            quantity: 주문수량
            price: 주문가격
            account_no: 계좌번호
            screen_no: 화면번호
        
        Returns:
            str: 주문번호
        """
        return self.send_order(
            "지정가매수", screen_no, account_no,
            1, code, quantity, price, self.PRICE_TYPE_LIMIT
        )
    
    def send_limit_sell_order(self, code, quantity, price, account_no, screen_no="0000"):
        """
        지정가 매도 주문을 전송합니다.
        
        Args:
            code: 종목코드
            quantity: 주문수량
            price: 주문가격
            account_no: 계좌번호
            screen_no: 화면번호
        
        Returns:
            str: 주문번호
        """
        return self.send_order(
            "지정가매도", screen_no, account_no,
            2, code, quantity, price, self.PRICE_TYPE_LIMIT
        )
    
    def cancel_order(self, order_no, code, quantity, account_no, screen_no="0000"):
        """
        주문을 취소합니다.
        
        Args:
            order_no: 원주문번호
            code: 종목코드
            quantity: 취소수량
            account_no: 계좌번호
            screen_no: 화면번호
        
        Returns:
            str: 주문번호
        """
        return self.send_order(
            "주문취소", screen_no, account_no,
            3, code, quantity, 0, self.PRICE_TYPE_LIMIT, order_no
        )
    
    def modify_order(self, order_no, code, quantity, price, account_no, screen_no="0000"):
        """
        주문을 정정합니다.
        
        Args:
            order_no: 원주문번호
            code: 종목코드
            quantity: 정정수량
            price: 정정가격
            account_no: 계좌번호
            screen_no: 화면번호
        
        Returns:
            str: 주문번호
        """
        return self.send_order(
            "주문정정", screen_no, account_no,
            5, code, quantity, price, self.PRICE_TYPE_LIMIT, order_no
        )
    
    def get_order_history(self, account_no, order_type="ALL", from_date="", to_date="", screen_no="0101"):
        """
        주문 내역을 조회합니다.
        
        Args:
            account_no: 계좌번호
            order_type: 주문종류 (ALL:전체, BUY:매수, SELL:매도)
            from_date: 시작일자 (YYYYMMDD)
            to_date: 종료일자 (YYYYMMDD)
            screen_no: 화면번호
        
        Returns:
            list: 주문 내역 리스트
        """
        try:
            # 연결 상태 확인
            if not self.get_connect_state():
                logger.error("키움 API 연결 상태가 아닙니다.")
                return []
            
            # TR 입력값 설정
            self.set_input_value("계좌번호", account_no)
            self.set_input_value("전체종목구분", "0")  # 0:전체, 1:종목
            self.set_input_value("체결구분", "0")  # 0:전체, 1:미체결, 2:체결
            self.set_input_value("매매구분", "0")  # 0:전체, 1:매도, 2:매수
            
            if from_date:
                self.set_input_value("시작일자", from_date)
            if to_date:
                self.set_input_value("종료일자", to_date)
            
            # TR 요청
            result = self.comm_rq_data("주문내역조회", "opt10075", 0, screen_no)
            
            if result != 0:
                logger.error(f"주문 내역 조회 요청 실패: {result}")
                return []
            
            # 이벤트 루프 생성
            self._event_loop = QEventLoop()
            self._event_loop.exec_()
            
            return self._order_history
        
        except Exception as e:
            logger.exception("주문 내역 조회 중 오류 발생")
            return []
    
    def get_outstanding_orders(self, account_no, screen_no="0102"):
        """
        미체결 주문 내역을 조회합니다.
        
        Args:
            account_no: 계좌번호
            screen_no: 화면번호
        
        Returns:
            list: 미체결 주문 리스트
        """
        try:
            # 연결 상태 확인
            if not self.get_connect_state():
                logger.error("키움 API 연결 상태가 아닙니다.")
                return []
            
            # TR 입력값 설정
            self.set_input_value("계좌번호", account_no)
            self.set_input_value("전체종목구분", "0")  # 0:전체
            self.set_input_value("체결구분", "1")  # 1:미체결
            self.set_input_value("매매구분", "0")  # 0:전체
            
            # TR 요청
            result = self.comm_rq_data("미체결주문조회", "opt10075", 0, screen_no)
            
            if result != 0:
                logger.error(f"미체결 주문 조회 요청 실패: {result}")
                return []
            
            # 이벤트 루프 생성
            self._event_loop = QEventLoop()
            self._event_loop.exec_()
            
            return self._outstanding_orders
        
        except Exception as e:
            logger.exception("미체결 주문 조회 중 오류 발생")
            return []
    
    def _on_receive_tr_data(self, screen_no, rqname, trcode, record_name, next, unused1, unused2, unused3, unused4):
        """TR 수신 이벤트 처리"""
        try:
            if trcode == "KOA_NORMAL_BUY_KP_ORD" or trcode == "KOA_NORMAL_SELL_KP_ORD":
                order_no = self.get_comm_data(trcode, rqname, 0, "주문번호")
                self._order_result = {
                    '주문번호': order_no,
                    '종목코드': self.get_comm_data(trcode, rqname, 0, "종목코드"),
                    '주문수량': int(self.get_comm_data(trcode, rqname, 0, "주문수량")),
                    '주문가격': int(self.get_comm_data(trcode, rqname, 0, "주문가격")),
                    '주문구분': self.get_comm_data(trcode, rqname, 0, "주문구분"),
                    '체결수량': int(self.get_comm_data(trcode, rqname, 0, "체결수량")),
                    '체결가격': int(self.get_comm_data(trcode, rqname, 0, "체결가격")),
                    '주문상태': self.get_comm_data(trcode, rqname, 0, "주문상태")
                }
                logger.debug(f"주문 결과: {self._order_result}")
            
            elif trcode == "opt10075":  # 주문체결조회
                rows = self.get_repeat_cnt(trcode, rqname)
                orders = []
                
                for i in range(rows):
                    order = {
                        '주문번호': self.get_comm_data(trcode, rqname, i, "주문번호"),
                        '종목코드': self.get_comm_data(trcode, rqname, i, "종목코드"),
                        '종목명': self.get_comm_data(trcode, rqname, i, "종목명"),
                        '주문구분': self.get_comm_data(trcode, rqname, i, "주문구분"),
                        '주문수량': int(self.get_comm_data(trcode, rqname, i, "주문수량")),
                        '주문가격': int(self.get_comm_data(trcode, rqname, i, "주문가격")),
                        '체결수량': int(self.get_comm_data(trcode, rqname, i, "체결수량")),
                        '체결가격': int(self.get_comm_data(trcode, rqname, i, "체결가격")),
                        '주문상태': self.get_comm_data(trcode, rqname, i, "주문상태"),
                        '주문시간': self.get_comm_data(trcode, rqname, i, "시간")
                    }
                    orders.append(order)
                
                if rqname == "미체결주문조회":
                    self._outstanding_orders = orders
                    logger.debug(f"미체결 주문: {len(orders)}건")
                else:
                    self._order_history = orders
                    logger.debug(f"주문 내역: {len(orders)}건")
        
        except Exception as e:
            logger.exception("TR 데이터 처리 중 오류 발생")
        
        finally:
            # 이벤트 루프 종료
            if self._event_loop is not None:
                self._event_loop.exit()
    
    def set_auto_cancel(self, order_no, timeout_seconds=None, price_threshold=None, market_price_threshold=None):
        """
        주문 자동 취소 조건을 설정합니다.
        
        Args:
            order_no: 주문번호
            timeout_seconds: 타임아웃 시간 (초)
            price_threshold: 가격 임계값 (원)
            market_price_threshold: 시장가 대비 임계값 (%)
        """
        if order_no not in self._monitored_orders:
            logger.warning(f"모니터링되지 않는 주문입니다: {order_no}")
            return
        
        self._auto_cancel_orders[order_no] = {
            '설정시각': datetime.now(),
            '타임아웃': timeout_seconds,
            '가격임계값': price_threshold,
            '시장가임계값': market_price_threshold
        }
        logger.info(f"자동 취소 설정: {order_no} - "
                   f"타임아웃: {timeout_seconds}초, "
                   f"가격임계값: {price_threshold}원, "
                   f"시장가임계값: {market_price_threshold}%")
    
    def set_auto_modify(self, order_no, target_price=None, price_step=None, max_tries=3):
        """
        주문 자동 정정 조건을 설정합니다.
        
        Args:
            order_no: 주문번호
            target_price: 목표가격 (원)
            price_step: 가격 단계 (원)
            max_tries: 최대 시도 횟수
        """
        if order_no not in self._monitored_orders:
            logger.warning(f"모니터링되지 않는 주문입니다: {order_no}")
            return
        
        self._auto_modify_orders[order_no] = {
            '설정시각': datetime.now(),
            '목표가격': target_price,
            '가격단계': price_step,
            '최대시도': max_tries,
            '시도횟수': 0
        }
        logger.info(f"자동 정정 설정: {order_no} - "
                   f"목표가격: {target_price}원, "
                   f"가격단계: {price_step}원, "
                   f"최대시도: {max_tries}회")
    
    def _check_auto_cancel(self, order_no, current_price=None):
        """
        주문 자동 취소 조건을 확인합니다.
        
        Args:
            order_no: 주문번호
            current_price: 현재가 (None인 경우 시장가 조회)
        
        Returns:
            bool: 취소 여부
        """
        if order_no not in self._auto_cancel_orders:
            return False
        
        cancel_info = self._auto_cancel_orders[order_no]
        order_info = self._monitored_orders[order_no]
        
        # 타임아웃 확인
        if cancel_info.get('타임아웃'):
            elapsed = (datetime.now() - cancel_info['설정시각']).total_seconds()
            if elapsed > cancel_info['타임아웃']:
                logger.info(f"주문 자동 취소 (타임아웃): {order_no}")
                return True
        
        # 가격 임계값 확인
        if cancel_info.get('가격임계값') and current_price:
            order_price = order_info.get('주문가격', 0)
            if abs(current_price - order_price) > cancel_info['가격임계값']:
                logger.info(f"주문 자동 취소 (가격 임계값): {order_no}")
                return True
        
        # 시장가 대비 임계값 확인
        if cancel_info.get('시장가임계값') and current_price:
            order_price = order_info.get('주문가격', 0)
            price_diff_percent = abs(current_price - order_price) / order_price * 100
            if price_diff_percent > cancel_info['시장가임계값']:
                logger.info(f"주문 자동 취소 (시장가 임계값): {order_no}")
                return True
        
        return False
    
    def _check_auto_modify(self, order_no, current_price=None):
        """
        주문 자동 정정 조건을 확인합니다.
        
        Args:
            order_no: 주문번호
            current_price: 현재가 (None인 경우 시장가 조회)
        
        Returns:
            tuple: (정정 여부, 새로운 가격)
        """
        if order_no not in self._auto_modify_orders:
            return False, None
        
        modify_info = self._auto_modify_orders[order_no]
        order_info = self._monitored_orders[order_no]
        
        # 최대 시도 횟수 확인
        if modify_info['시도횟수'] >= modify_info['최대시도']:
            logger.info(f"주문 자동 정정 중단 (최대 시도 횟수 초과): {order_no}")
            return False, None
        
        current_price = current_price or 0
        target_price = modify_info.get('목표가격')
        price_step = modify_info.get('가격단계', 0)
        
        # 목표가격이 설정된 경우
        if target_price:
            order_price = order_info.get('주문가격', 0)
            if abs(target_price - order_price) > price_step:
                # 목표가격 방향으로 한 단계 이동
                step_direction = 1 if target_price > order_price else -1
                new_price = order_price + (price_step * step_direction)
                logger.info(f"주문 자동 정정 (목표가격 방향): {order_no} - {new_price}원")
                modify_info['시도횟수'] += 1
                return True, new_price
        
        return False, None
    
    def _process_auto_orders(self, order_no, current_price=None):
        """
        자동 주문 처리를 수행합니다.
        
        Args:
            order_no: 주문번호
            current_price: 현재가
        """
        try:
            # 자동 취소 확인
            if self._check_auto_cancel(order_no, current_price):
                order_info = self._monitored_orders[order_no]
                self.cancel_order(
                    order_no,
                    order_info.get('종목코드', ''),
                    order_info.get('미체결수량', 0),
                    order_info.get('계좌번호', '')
                )
            
            # 자동 정정 확인
            should_modify, new_price = self._check_auto_modify(order_no, current_price)
            if should_modify and new_price:
                order_info = self._monitored_orders[order_no]
                self.modify_order(
                    order_no,
                    order_info.get('종목코드', ''),
                    order_info.get('미체결수량', 0),
                    new_price,
                    order_info.get('계좌번호', '')
                )
        
        except Exception as e:
            logger.exception(f"자동 주문 처리 중 오류 발생: {order_no}") 