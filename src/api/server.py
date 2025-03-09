"""
API 서버 모듈
"""
import os
from flask import Flask, jsonify, request
from flask_restx import Api, Resource, Namespace
from flask_cors import CORS

from src.config import constants
from src.utils.logger import setup_logger
from src.utils.env_loader import get_env

# 로거 설정
logger = setup_logger('api_server', constants.LOG_LEVEL)

def create_app(trading_bot):
    """
    Flask 애플리케이션 생성
    
    Args:
        trading_bot: 트레이딩봇 인스턴스
        
    Returns:
        Flask: Flask 애플리케이션 인스턴스
    """
    # Flask 애플리케이션 생성
    app = Flask(__name__)
    
    # CORS 설정
    CORS(app)
    
    # API 설정
    api = Api(
        app,
        version='1.0',
        title='트레이딩봇 API',
        description='키움증권 API를 활용한 트레이딩봇 API',
        doc='/docs'
    )
    
    # 네임스페이스 생성
    account_api = Namespace('account', description='계좌 관련 API')
    order_api = Namespace('order', description='주문 관련 API')
    market_api = Namespace('market', description='시장 데이터 관련 API')
    backtest_api = Namespace('backtest', description='백테스팅 관련 API')
    
    # 네임스페이스 등록
    api.add_namespace(account_api, path='/account')
    api.add_namespace(order_api, path='/order')
    api.add_namespace(market_api, path='/market')
    api.add_namespace(backtest_api, path='/backtest')
    
    # 전역 변수 설정
    app.config['trading_bot'] = trading_bot
    
    # 계좌 API 라우트
    @account_api.route('/info')
    class AccountInfo(Resource):
        def get(self):
            """계좌 정보 조회"""
            try:
                kiwoom = app.config['trading_bot'].kiwoom
                account_no = kiwoom.account_number
                
                # 예수금 정보 조회
                deposit_info = kiwoom.get_deposit_info(account_no)
                
                # 계좌평가잔고내역 조회
                account_eval = kiwoom.get_account_evaluation(account_no)
                
                # 응답 데이터 구성
                response = {
                    'account_number': account_no,
                    'deposit': deposit_info.get('deposit', 0),
                    'available': deposit_info.get('available', 0),
                    'total_purchase': account_eval.get('total_purchase', 0),
                    'total_eval': account_eval.get('total_eval', 0),
                    'total_profit': account_eval.get('total_profit', 0),
                    'total_profit_rate': account_eval.get('total_profit_rate', 0),
                    'stocks': account_eval.get('stocks', [])
                }
                
                return jsonify(response)
            
            except Exception as e:
                logger.exception(f"계좌 정보 조회 중 오류 발생: {e}")
                return jsonify({'error': str(e)}), 500
    
    @account_api.route('/stocks')
    class AccountStocks(Resource):
        def get(self):
            """보유 종목 조회"""
            try:
                kiwoom = app.config['trading_bot'].kiwoom
                account_no = kiwoom.account_number
                
                # 계좌평가잔고내역 조회
                account_eval = kiwoom.get_account_evaluation(account_no)
                
                # 응답 데이터 구성
                response = {
                    'account_number': account_no,
                    'stocks': account_eval.get('stocks', [])
                }
                
                return jsonify(response)
            
            except Exception as e:
                logger.exception(f"보유 종목 조회 중 오류 발생: {e}")
                return jsonify({'error': str(e)}), 500
    
    # 주문 API 라우트
    @order_api.route('/buy')
    class OrderBuy(Resource):
        def post(self):
            """매수 주문"""
            try:
                kiwoom = app.config['trading_bot'].kiwoom
                account_no = kiwoom.account_number
                
                # 요청 데이터 파싱
                data = request.get_json()
                stock_code = data.get('code')
                quantity = data.get('quantity', 1)
                price = data.get('price', 0)
                order_type = data.get('order_type', '시장가')
                
                # 주문 유형 변환
                hoga_gb = '03'  # 기본값: 시장가
                if order_type == '지정가':
                    hoga_gb = '00'
                
                # 주문 실행
                order_result = kiwoom.send_order(
                    '매수주문',
                    constants.SCREEN_ORDER_STOCK,
                    account_no,
                    1,  # 매수
                    stock_code,
                    quantity,
                    price,
                    hoga_gb,
                    ''
                )
                
                # 응답 데이터 구성
                response = {
                    'order_result': order_result,
                    'account_number': account_no,
                    'stock_code': stock_code,
                    'quantity': quantity,
                    'price': price,
                    'order_type': order_type
                }
                
                return jsonify(response)
            
            except Exception as e:
                logger.exception(f"매수 주문 중 오류 발생: {e}")
                return jsonify({'error': str(e)}), 500
    
    @order_api.route('/sell')
    class OrderSell(Resource):
        def post(self):
            """매도 주문"""
            try:
                kiwoom = app.config['trading_bot'].kiwoom
                account_no = kiwoom.account_number
                
                # 요청 데이터 파싱
                data = request.get_json()
                stock_code = data.get('code')
                quantity = data.get('quantity', 1)
                price = data.get('price', 0)
                order_type = data.get('order_type', '시장가')
                
                # 주문 유형 변환
                hoga_gb = '03'  # 기본값: 시장가
                if order_type == '지정가':
                    hoga_gb = '00'
                
                # 주문 실행
                order_result = kiwoom.send_order(
                    '매도주문',
                    constants.SCREEN_ORDER_STOCK,
                    account_no,
                    2,  # 매도
                    stock_code,
                    quantity,
                    price,
                    hoga_gb,
                    ''
                )
                
                # 응답 데이터 구성
                response = {
                    'order_result': order_result,
                    'account_number': account_no,
                    'stock_code': stock_code,
                    'quantity': quantity,
                    'price': price,
                    'order_type': order_type
                }
                
                return jsonify(response)
            
            except Exception as e:
                logger.exception(f"매도 주문 중 오류 발생: {e}")
                return jsonify({'error': str(e)}), 500
    
    # 시장 데이터 API 라우트
    @market_api.route('/stock')
    class MarketStock(Resource):
        def get(self):
            """종목 정보 조회"""
            try:
                kiwoom = app.config['trading_bot'].kiwoom
                
                # 요청 파라미터 파싱
                stock_code = request.args.get('code', constants.SAMSUNG_CODE)
                
                # 종목 정보 조회
                stock_info = kiwoom.get_stock_basic_info(stock_code)
                
                return jsonify(stock_info)
            
            except Exception as e:
                logger.exception(f"종목 정보 조회 중 오류 발생: {e}")
                return jsonify({'error': str(e)}), 500
    
    @market_api.route('/chart')
    class MarketChart(Resource):
        def get(self):
            """차트 데이터 조회"""
            try:
                kiwoom = app.config['trading_bot'].kiwoom
                
                # 요청 파라미터 파싱
                stock_code = request.args.get('code', constants.SAMSUNG_CODE)
                base_date = request.args.get('base_date', '')
                req_count = int(request.args.get('count', 100))
                
                # 차트 데이터 조회
                chart_data = kiwoom.get_day_chart_data(stock_code, base_date, req_count)
                
                return jsonify(chart_data)
            
            except Exception as e:
                logger.exception(f"차트 데이터 조회 중 오류 발생: {e}")
                return jsonify({'error': str(e)}), 500
    
    # 루트 라우트
    @app.route('/')
    def index():
        return jsonify({
            'name': '트레이딩봇 API',
            'version': '1.0',
            'docs': '/docs'
        })
    
    return app

def run_server(app, host=None, port=None):
    """
    서버 실행 함수
    
    Args:
        app: Flask 애플리케이션 인스턴스
        host (str): 호스트 주소
        port (int): 포트 번호
    """
    host = host or get_env('API_HOST', constants.API_HOST)
    port = port or int(get_env('API_PORT', constants.API_PORT))
    
    logger.info(f"API 서버 시작: {host}:{port}")
    app.run(host=host, port=port, debug=False, use_reloader=False) 