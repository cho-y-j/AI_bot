# 트레이딩봇 프로젝트 구조

## 메인 메뉴 구조

로그인창-> 키움 로그인 연동시켜 로그인 (기본설정 openai api 키 , 테레그램키, 계좌 비밀번로 미리 설정하여 저장 기능) 

0.메인 데시보드

-상단 메뉴 아래 1,2,3,4,6,7 번 에서 해당 하위 메뉴들은 새창 
-바디
각 페널들 새창 열기로 알아서 배치하고 대시보드1, 대시보드2, 대시보드3,...선택하여 볼수 있도록
-
1. **기본 메뉴**
   - 차트 보기
   - 현재가 조회
   - 보유종목 
   - 관심종목
   - 계좌 보기
   - 실시간 매매현황
   - 거래순위및 실시간검색어
   - 거래 내역
   - 수익률 분석
   - 로그 
2. AI 조건 매매
   - ai 조건 거래
   - 자동 거래 설정
3  ai 자동매매
   - ai 자동거래
   - 설정
4  ai 검색
   - 실기간 검색 결과
   - 검색 설정   
5. ai종목 분석
   -ai 뉴스검색
   -ai 종목 분석
6. 설정
   - 비밀 번호 관리
   - 알림 설정


## 디렉토리 구조

```
tradingbot/
  ├── main.py                # 메인 실행 파일
  ├── requirements.txt       # 필요한 패키지 목록
  ├── README.md              # 프로젝트 설명
  ├── .env.example           # 환경 변수 예시 파일
  ├── data/                  # 데이터 저장 디렉토리
  │   ├── models/            # AI 모델 저장 디렉토리
  │   └── logs/              # 로그 저장 디렉토리
  └── src/                   # 소스 코드
      ├── __init__.py
      ├── app.py             # 애플리케이션 클래스
      ├── config/            # 설정 관련 모듈
      │   ├── __init__.py
      │   ├── constants.py   # 상수 정의
      │   └── settings.py    # 설정 관리
      ├── utils/             # 유틸리티 모듈
      │   ├── __init__.py
      │   ├── logging.py     # 로깅 유틸리티
      │   ├── date_utils.py  # 날짜 관련 유틸리티
      │   └── file_utils.py  # 파일 관련 유틸리티
      ├── kiwoom/            # 키움 API 관련 모듈
      │   ├── __init__.py
      │   ├── base.py        # 기본 API 연결 및 이벤트 처리
      │   ├── account.py     # 계좌 관련 기능
      │   ├── order.py       # 주문 관련 기능
      │   ├── data.py        # 데이터 조회 기능
      │   ├── chart.py       # 차트 데이터 조회 기능
      │   ├── condition.py   # 조건검색 관련 기능
      │   └── realtime.py    # 실시간 데이터 관련 기능
      ├── models/            # AI 모델 관련 모듈
      │   ├── __init__.py
      │   └── price_predictor.py  # 가격 예측 모델
      ├── strategies/        # 트레이딩 전략 관련 모듈
      │   ├── __init__.py
      │   ├── base_strategy.py    # 기본 전략 클래스
      │   ├── bollinger_strategy.py  # 볼린저 밴드 전략
      │   ├── ai_strategy.py      # AI 기반 전략
      │   └── analysis/           # 다양한 분석 전략
      │       ├── __init__.py
      │       ├── technical.py    # 기술적 분석 전략
      │       ├── fundamental.py  # 기본적 분석 전략
      │       └── pattern.py      # 패턴 인식 전략
      ├── managers/          # 기능 관리 모듈
      │   ├── __init__.py
      │   ├── account_manager.py  # 계좌 관리
      │   ├── order_manager.py    # 주문 관리
      │   ├── data_manager.py     # 데이터 관리
      │   ├── chart_manager.py    # 차트 관리
      │   └── strategy_manager.py # 전략 관리
      ├── gui/               # GUI 관련 모듈
      │   ├── __init__.py
      │   ├── main_window.py      # 메인 윈도우 (기본 프레임)
      │   ├── dialogs/            # 다이얼로그 모듈
      │   │   ├── __init__.py
      │   │   ├── login_dialog.py      # 로그인 다이얼로그
      │   │   └── settings_dialog.py   # 설정 다이얼로그
      │   ├── panels/             # 패널 모듈
      │   │   ├── __init__.py
      │   │   ├── account_panel.py     # 계좌 정보 패널
      │   │   ├── stock_panel.py       # 종목 정보 패널
      │   │   ├── chart_panel.py       # 차트 패널
      │   │   ├── order_panel.py       # 주문 패널
      │   │   ├── log_panel.py         # 로그 패널
      │   │   └── holdings_panel.py    # 보유 종목 패널
              └── favorites_panel.py     관심종목
      │   ├── widgets/            # 위젯 모듈
      │   │   ├── __init__.py
      │   │   ├── chart_widget.py      # 차트 위젯
      │   │   ├── stock_table.py       # 종목 테이블 위젯
      │   │   └── order_widget.py      # 주문 위젯
      │   └── windows/            # 독립 윈도우 모듈
      │       ├── __init__.py
      │       ├── chart_window.py      # 차트 윈도우
      │       ├── current_price_window.py  # 현재가 윈도우
      │       ├── account_window.py    # 계좌 윈도우
      │       ├── transaction_window.py  # 거래 내역 윈도우
      │       ├── auto_trading_window.py  # 자동 거래 윈도우
      │       ├── ai_trading_window.py  # AI 자동 거래 윈도우
      │       ├── analysis_window.py   # 종목 분석 윈도우
      │       └── search_window.py     # 종목 찾기 윈도우
      ├── features/           # 주요 기능 모듈
      │   ├── __init__.py
      │   ├── auto_trading/        # ai 조건 자동 거래 기능
      │   │   ├── __init__.py
      │   │   ├── monitor.py       # 감시 주문
      │   │   ├── executor.py      # 자동 거래 실행
      │   │   └── settings.py      # 자동 거래 설정
      │   ├── ai_trading/          # AI 자동 거래 기능
      │   │   ├── __init__.py
      │   │   ├── predictor.py     # AI 예측 기능
      │   │   ├── executor.py      # AI 거래 실행
      │   │   └── settings.py      # AI 거래 설정
      │   ├── analysis/            # 종목 분석 기능
      │   │   ├── __init__.py
      │   │   ├── technical.py     # 기술적 분석
      │   │   ├── fundamental.py   # 기본적 분석
      │   │   └── pattern.py       # 패턴 분석
      │   └── search/              # 종목 찾기 기능
      │       ├── __init__.py
      │       ├── condition.py     # 조건식 검색
      │       └── filter.py        # 필터링 기능
      └── notification/      # 알림 관련 모듈
          ├── __init__.py
          ├── email.py       # 이메일 알림
          └── telegram.py    # 텔레그램 알림
```

## 모듈 설명

### 1. 키움 API 모듈 (src/kiwoom/)

- **base.py**: 키움 API 연결, 로그인, 기본 이벤트 처리
- **account.py**: 계좌 정보 조회, 잔고 조회 등
- **order.py**: 주문 처리, 주문 상태 조회 등
- **data.py**: 종목 정보, 시세 조회 등
- **chart.py**: 차트 데이터 조회 (일봉, 주봉, 월봉, 분봉)
- **condition.py**: 조건검색 관련 기능
- **realtime.py**: 실시간 데이터 수신 처리

### 2. 매니저 모듈 (src/managers/)

- **account_manager.py**: 계좌 관련 기능 통합 관리
- **order_manager.py**: 주문 관련 기능 통합 관리
- **data_manager.py**: 데이터 관련 기능 통합 관리
- **chart_manager.py**: 차트 관련 기능 통합 관리
- **strategy_manager.py**: 전략 관련 기능 통합 관리

### 3. GUI 모듈 (src/gui/)

- **main_window.py**: 메인 윈도우 기본 프레임
- **menu/**: 메뉴 관련 모듈
- **dialogs/**: 다이얼로그 관련 모듈
- **panels/**: 패널 관련 모듈
- **widgets/**: 위젯 관련 모듈
- **windows/**: 독립 윈도우 모듈 (새 창으로 열리는 화면)

### 4. 전략 모듈 (src/strategies/)

- **base_strategy.py**: 기본 전략 클래스 (추상 클래스)
- **bollinger_strategy.py**: 볼린저 밴드 기반 전략
- **ai_strategy.py**: AI 기반 전략
- **analysis/**: 다양한 분석 전략 모듈

### 5. 모델 모듈 (src/models/)

- **price_predictor.py**: 가격 예측 모델
- **analysis_models.py**: 종목 분석 모델

### 6. 기능 모듈 (src/features/)

- **auto_trading/**: 자동 거래 관련 기능
- **ai_trading/**: AI 자동 거래 관련 기능
- **analysis/**: 종목 분석 관련 기능
- **search/**: 종목 찾기 관련 기능

### 7. 설정 모듈 (src/config/)

- **constants.py**: 상수 정의
- **settings.py**: 설정 관리

### 8. 유틸리티 모듈 (src/utils/)

- **logging.py**: 로깅 유틸리티
- **date_utils.py**: 날짜 관련 유틸리티
- **file_utils.py**: 파일 관련 유틸리티

### 9. 알림 모듈 (src/notification/)

- **email.py**: 이메일 알림 기능
- **telegram.py**: 텔레그램 알림 기능 