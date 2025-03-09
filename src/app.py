"""
트레이딩봇 메인 애플리케이션
"""
import os
import sys
import time
import threading
import logging
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTabWidget, QMessageBox
from PyQt5.QtCore import Qt, QTimer

from src.config import constants
from src.utils.logger import setup_logger
from src.utils.env_loader import load_env_vars, get_env
from src.kiwoom.kiwoom import KiwoomAPI
from src.api.server import create_app, run_server
from src.gui.main_window import MainWindow

# 로거 설정
logger = setup_logger('app', constants.LOG_LEVEL, constants.LOG_FILE)

class TradingBot:
    """
    트레이딩봇 메인 클래스
    """
    def __init__(self, use_gui=True, use_api=False):
        """
        초기화 함수
        
        Args:
            use_gui (bool): GUI 사용 여부
            use_api (bool): API 서버 사용 여부
        """
        # 환경 변수 로드
        load_env_vars()
        
        # 키움 API 인스턴스 생성
        self.kiwoom = None
        
        # GUI 설정
        self.use_gui = use_gui
        self.main_window = None
        
        # API 서버 설정
        self.use_api = use_api
        self.app = None if not use_api else create_app(self)
        
        # 스레드 설정
        self.server_thread = None
        self.trading_thread = None
        self.is_running = False
        
        # QApplication 인스턴스 생성
        if not QApplication.instance():
            self.q_app = QApplication(sys.argv)
        else:
            self.q_app = QApplication.instance()
        
        logger.info("트레이딩봇 초기화 완료")
    
    def start(self):
        """
        트레이딩봇 시작
        """
        logger.info("트레이딩봇 시작")
        self.is_running = True
        
        # 키움 API 초기화
        if not self._init_kiwoom():
            logger.error("키움 API 초기화 실패")
            if self.use_gui:
                QMessageBox.critical(None, "오류", "키움 API 초기화에 실패했습니다.\n키움 OpenAPI가 설치되어 있는지 확인하세요.")
            return False
        
        # GUI 초기화
        if self.use_gui:
            self.main_window = MainWindow(self)
            self.main_window.show()
        
        # API 서버 스레드 시작 (사용하는 경우)
        if self.use_api and self.app:
            self.server_thread = threading.Thread(target=run_server, args=(self.app,))
            self.server_thread.daemon = True
            self.server_thread.start()
            logger.info("API 서버 스레드 시작")
        
        # 트레이딩 스레드 시작
        self.trading_thread = threading.Thread(target=self._run_trading)
        self.trading_thread.daemon = True
        self.trading_thread.start()
        logger.info("트레이딩 스레드 시작")
        
        logger.info("트레이딩봇 시작 완료")
        
        # GUI 이벤트 루프 실행 (GUI 사용 시)
        if self.use_gui:
            return self.q_app.exec_()
        
        return True
    
    def stop(self):
        """
        트레이딩봇 종료
        """
        logger.info("트레이딩봇 종료")
        self.is_running = False
        
        # 스레드 종료 대기
        if self.trading_thread and self.trading_thread.is_alive():
            self.trading_thread.join(timeout=5)
        
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=5)
        
        # GUI 종료
        if self.use_gui and self.main_window:
            self.main_window.close()
        
        logger.info("트레이딩봇 종료 완료")
    
    def _init_kiwoom(self):
        """
        키움 API 초기화
        """
        try:
            # 키움 API 인스턴스 생성
            self.kiwoom = KiwoomAPI()
            
            # 로그인
            if not self.kiwoom.login():
                logger.error("키움 API 로그인 실패")
                return False
            
            # 계좌 정보 설정
            account = get_env('KIWOOM_ACCOUNT', '')
            if account:
                self.kiwoom.account_number = account
                logger.info(f"계좌 설정 완료: {account}")
            elif self.kiwoom.account_list:
                self.kiwoom.account_number = self.kiwoom.account_list[0]
                logger.info(f"기본 계좌 설정 완료: {self.kiwoom.account_number}")
            else:
                logger.error("계좌 정보가 없습니다.")
                return False
            
            logger.info("키움 API 초기화 완료")
            return True
        
        except Exception as e:
            logger.exception(f"키움 API 초기화 중 오류 발생: {e}")
            return False
    
    def _run_trading(self):
        """
        트레이딩 실행 함수
        """
        logger.info("트레이딩 스레드 시작")
        
        while self.is_running:
            try:
                # 자동 매매 로직 실행
                if self.main_window and hasattr(self.main_window, 'auto_trading_enabled') and self.main_window.auto_trading_enabled:
                    # 자동 매매가 활성화된 경우에만 실행
                    self._execute_auto_trading()
                
                # 일정 시간 대기
                time.sleep(constants.AUTO_TRADING_INTERVAL)
            
            except Exception as e:
                logger.exception(f"트레이딩 실행 중 오류 발생: {e}")
                time.sleep(10)  # 오류 발생 시 10초 대기
        
        logger.info("트레이딩 스레드 종료")
    
    def _execute_auto_trading(self):
        """
        자동 매매 실행 함수
        """
        try:
            # 메인 윈도우에서 자동 매매 설정 가져오기
            if not self.main_window or not hasattr(self.main_window, 'auto_trading_settings'):
                logger.warning("자동 매매 설정이 없습니다.")
                return
            
            settings = self.main_window.auto_trading_settings
            
            # 설정이 없으면 실행하지 않음
            if not settings:
                return
            
            # 설정에서 필요한 정보 가져오기
            code = settings.get('code')
            strategy = settings.get('strategy')
            
            if not code or not strategy:
                logger.warning("자동 매매에 필요한 종목 코드 또는 전략이 없습니다.")
                return
            
            # 현재가 조회
            current_price = self.kiwoom.get_current_price(code)
            
            if not current_price:
                logger.warning(f"종목 {code}의 현재가를 조회할 수 없습니다.")
                return
            
            # 보유 종목 확인
            position = self._get_position(code)
            
            # 차트 데이터 가져오기
            chart_data = self._get_chart_data(code, settings.get('chart_type', 'D'))
            
            if chart_data is None or len(chart_data) < 20:
                logger.warning(f"종목 {code}의 차트 데이터가 부족합니다.")
                return
            
            # 매매 신호 확인
            if not position['is_holding'] and strategy.should_buy(chart_data, current_price, position):
                # 매수 가능 금액 계산
                available_cash = self._get_available_cash()
                
                if available_cash < current_price * 10:  # 최소 10주 이상 매수 가능한지 확인
                    logger.warning(f"매수 가능 금액이 부족합니다. (가능 금액: {available_cash})")
                    return
                
                # 매수 수량 계산 (가용 금액의 최대 30%까지만 사용)
                max_amount = available_cash * 0.3
                quantity = int(max_amount / current_price)
                
                if quantity < 1:
                    logger.warning(f"매수 가능 수량이 부족합니다. (계산 수량: {quantity})")
                    return
                
                # 매수 주문
                order_result = self.kiwoom.send_order(
                    rqname="신규매수",
                    screen_no="0101",
                    acc_no=self.kiwoom.account_number,
                    order_type=1,  # 신규매수
                    code=code,
                    quantity=quantity,
                    price=0,  # 시장가
                    hoga_gb="03",  # 시장가
                    org_order_no=""
                )
                
                if order_result == 0:
                    logger.info(f"매수 주문 성공: {code}, {quantity}주, 시장가")
                else:
                    logger.error(f"매수 주문 실패: {code}, {quantity}주, 시장가, 오류코드: {order_result}")
            
            elif position['is_holding'] and strategy.should_sell(chart_data, current_price, position):
                # 매도 수량 (보유 수량 전체)
                quantity = position['quantity']
                
                if quantity <= 0:
                    logger.warning(f"매도 가능 수량이 없습니다. (보유 수량: {quantity})")
                    return
                
                # 매도 주문
                order_result = self.kiwoom.send_order(
                    rqname="신규매도",
                    screen_no="0101",
                    acc_no=self.kiwoom.account_number,
                    order_type=2,  # 신규매도
                    code=code,
                    quantity=quantity,
                    price=0,  # 시장가
                    hoga_gb="03",  # 시장가
                    org_order_no=""
                )
                
                if order_result == 0:
                    logger.info(f"매도 주문 성공: {code}, {quantity}주, 시장가")
                else:
                    logger.error(f"매도 주문 실패: {code}, {quantity}주, 시장가, 오류코드: {order_result}")
        
        except Exception as e:
            logger.exception(f"자동 매매 실행 중 오류 발생: {e}")
    
    def _get_position(self, code):
        """
        종목 보유 상태 조회
        
        Args:
            code (str): 종목 코드
            
        Returns:
            dict: 보유 상태 정보
        """
        try:
            # 계좌 잔고 조회
            account_no = self.kiwoom.account_number
            balance = self.kiwoom.get_balance(account_no)
            
            # 기본 포지션 정보
            position = {
                'is_holding': False,
                'quantity': 0,
                'entry_price': 0,
                'current_price': 0,
                'profit_loss': 0,
                'profit_loss_percent': 0,
            }
            
            # 보유 종목 확인
            for item in balance:
                if item['code'] == code:
                    position['is_holding'] = True
                    position['quantity'] = item['quantity']
                    position['entry_price'] = item['purchase_price']
                    position['current_price'] = item['current_price']
                    position['profit_loss'] = item['profit_loss']
                    position['profit_loss_percent'] = item['profit_loss_percent']
                    break
            
            return position
            
        except Exception as e:
            logger.exception(f"포지션 조회 중 오류 발생: {e}")
            return {'is_holding': False, 'quantity': 0, 'entry_price': 0}
    
    def _get_available_cash(self):
        """
        매수 가능 금액 조회
        
        Returns:
            float: 매수 가능 금액
        """
        try:
            # 예수금 조회
            account_no = self.kiwoom.account_number
            deposit = self.kiwoom.get_deposit_info(account_no)
            
            # 매수 가능 금액 반환
            return deposit.get('available_cash', 0)
            
        except Exception as e:
            logger.exception(f"매수 가능 금액 조회 중 오류 발생: {e}")
            return 0
    
    def _get_chart_data(self, code, chart_type='D', count=100):
        """
        차트 데이터 조회
        
        Args:
            code (str): 종목 코드
            chart_type (str): 차트 타입 ('D': 일봉, 'W': 주봉, 'M': 월봉, 'm': 분봉)
            count (int): 조회할 데이터 개수
            
        Returns:
            DataFrame: 차트 데이터
        """
        try:
            # 차트 데이터 조회
            if chart_type == 'D':
                df = self.kiwoom.get_daily_chart(code, count)
            elif chart_type == 'W':
                df = self.kiwoom.get_weekly_chart(code, count)
            elif chart_type == 'M':
                df = self.kiwoom.get_monthly_chart(code, count)
            elif chart_type == 'm':
                df = self.kiwoom.get_minute_chart(code, 1, count)  # 1분봉
            else:
                logger.warning(f"지원하지 않는 차트 타입: {chart_type}")
                return None
            
            return df
            
        except Exception as e:
            logger.exception(f"차트 데이터 조회 중 오류 발생: {e}")
            return None

def main():
    """
    메인 함수
    """
    try:
        # 명령행 인자 처리
        use_gui = True  # 기본값: GUI 사용
        use_api = False  # 기본값: API 서버 사용 안 함
        
        # 명령행 인자가 있는 경우 처리
        if len(sys.argv) > 1:
            if "--no-gui" in sys.argv:
                use_gui = False
            if "--api" in sys.argv:
                use_api = True
        
        # 트레이딩봇 인스턴스 생성
        bot = TradingBot(use_gui=use_gui, use_api=use_api)
        
        # 트레이딩봇 시작
        if use_gui:
            # GUI 모드에서는 이벤트 루프가 메인 스레드를 블록함
            sys.exit(bot.start())
        else:
            # 콘솔 모드에서는 메인 스레드에서 대기
            bot.start()
            while True:
                time.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("사용자에 의한 프로그램 종료")
    
    except Exception as e:
        logger.exception(f"프로그램 실행 중 오류 발생: {e}")
    
    finally:
        # 트레이딩봇 종료
        if 'bot' in locals():
            bot.stop()

if __name__ == "__main__":
    main() 