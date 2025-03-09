"""
트레이딩봇에서 사용하는 상수 정의
"""

# 계좌 정보
ACCOUNT = ""  # 실제 사용 시 계좌번호 입력

# 화면번호
SCREEN_ACCOUNT = "1000"  # 계좌 관련 화면
SCREEN_TRADING_STOCK = "2000"  # 주식 거래 화면
SCREEN_CHART = "3000"  # 차트 화면
SCREEN_REAL_TIME = "4000"  # 실시간 시세 화면
SCREEN_CONDITION = "5000"  # 조건검색 화면

# 주문유형
ORDER_TYPE_BUY = 1  # 신규매수
ORDER_TYPE_SELL = 2  # 신규매도
ORDER_TYPE_CANCEL_BUY = 3  # 매수취소
ORDER_TYPE_CANCEL_SELL = 4  # 매도취소
ORDER_TYPE_MODIFY_BUY = 5  # 매수정정
ORDER_TYPE_MODIFY_SELL = 6  # 매도정정

# 호가유형
HOGA_TYPE_LIMIT = "00"  # 지정가
HOGA_TYPE_MARKET = "03"  # 시장가
HOGA_TYPE_CONDITIONAL = "05"  # 조건부지정가
HOGA_TYPE_BEST_LIMIT = "06"  # 최유리지정가
HOGA_TYPE_BEST_PRIORITY = "07"  # 최우선지정가
HOGA_TYPE_LIMIT_IOC = "10"  # 지정가IOC
HOGA_TYPE_MARKET_IOC = "13"  # 시장가IOC
HOGA_TYPE_BEST_LIMIT_IOC = "16"  # 최유리IOC
HOGA_TYPE_LIMIT_FOK = "20"  # 지정가FOK
HOGA_TYPE_MARKET_FOK = "23"  # 시장가FOK
HOGA_TYPE_BEST_LIMIT_FOK = "26"  # 최유리FOK
HOGA_TYPE_AFTER_MARKET_CLOSE = "61"  # 장전시간외종가
HOGA_TYPE_SINGLE_PRICE = "62"  # 시간외단일가
HOGA_TYPE_AFTER_MARKET_OPEN = "81"  # 장후시간외종가

# 종목 코드
SAMSUNG_CODE = "005930"  # 삼성전자
KAKAO_CODE = "035720"  # 카카오
NAVER_CODE = "035420"  # 네이버
LG_CHEM_CODE = "051910"  # LG화학
SK_HYNIX_CODE = "000660"  # SK하이닉스

# 자동 매매 설정
AUTO_TRADING_INTERVAL = 1  # 자동 매매 실행 간격 (초)
MAX_BUY_AMOUNT = 1000000  # 최대 매수 금액
MAX_STOCKS_COUNT = 10  # 최대 보유 종목 수
PROFIT_RATE = 2.0  # 익절 비율 (%)
LOSS_RATE = 1.0  # 손절 비율 (%)

# 기술적 지표 설정
BOLLINGER_N = 20  # 볼린저 밴드 기간
BOLLINGER_K = 2  # 볼린저 밴드 표준편차 배수
RSI_PERIOD = 14  # RSI 기간
MACD_FAST = 12  # MACD 빠른 기간
MACD_SLOW = 26  # MACD 느린 기간
MACD_SIGNAL = 9  # MACD 시그널 기간

# 로깅 설정
LOG_LEVEL = "INFO"
LOG_FILE = "trading_bot.log"

# API 설정
API_HOST = "127.0.0.1"
API_PORT = 5000

# TR코드
TR_OPT10001 = "opt10001"  # 주식기본정보
TR_OPT10081 = "opt10081"  # 일봉데이터
TR_OPW00001 = "opw00001"  # 예수금상세조회
TR_OPW00018 = "opw00018"  # 계좌평가

# 차트 타입
CHART_TYPE_MINUTE = "분봉"
CHART_TYPE_DAY = "일봉"
CHART_TYPE_WEEK = "주봉"
CHART_TYPE_MONTH = "월봉"

# 분봉 시간 간격
MINUTE_INTERVAL_1 = "1"
MINUTE_INTERVAL_3 = "3"
MINUTE_INTERVAL_5 = "5"
MINUTE_INTERVAL_10 = "10"
MINUTE_INTERVAL_15 = "15"
MINUTE_INTERVAL_30 = "30"
MINUTE_INTERVAL_60 = "60" 