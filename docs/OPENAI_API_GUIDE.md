# OpenAI API 연동 가이드

## 1. OpenAI API 개요

OpenAI API는 GPT 모델을 활용하여 자연어 처리, 텍스트 생성, 분석 등 다양한 AI 기능을 제공합니다. 트레이딩봇에서는 이를 활용하여 뉴스 분석, 종목 추천, 시장 분석 등의 기능을 구현할 수 있습니다.

## 2. API 키 발급 방법

1. [OpenAI 웹사이트](https://platform.openai.com/)에 접속하여 계정 생성 또는 로그인
2. 우측 상단의 프로필 아이콘 클릭 후 "View API keys" 선택
3. "Create new secret key" 버튼 클릭하여 새 API 키 생성
4. 생성된 API 키를 안전하게 저장 (한 번만 표시됨)

## 3. 기본 설정

### 3.1 환경 변수 설정
```python
# .env 파일에 API 키 저장
OPENAI_API_KEY=your_api_key_here
```

### 3.2 필요 패키지 설치
```bash
pip install openai python-dotenv
```

### 3.3 기본 설정 코드
```python
import os
from openai import OpenAI
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
```

## 4. 주요 기능 및 사용 예시

### 4.1 뉴스 분석 및 요약
```python
def analyze_news(news_text):
    """뉴스 텍스트를 분석하여 주식 시장에 미치는 영향을 평가"""
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "당신은 금융 뉴스 분석 전문가입니다. 뉴스가 주식 시장에 미치는 영향을 분석해주세요."},
            {"role": "user", "content": f"다음 뉴스를 분석하고 주식 시장에 미치는 영향을 평가해주세요: {news_text}"}
        ],
        temperature=0.3,
        max_tokens=500
    )
    
    return response.choices[0].message.content
```

### 4.2 종목 분석 및 추천
```python
def analyze_stock(stock_code, stock_name, financial_data):
    """종목 데이터를 분석하여 투자 의견 제공"""
    
    # 재무 데이터를 문자열로 변환
    financial_str = "\n".join([f"{k}: {v}" for k, v in financial_data.items()])
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "당신은 주식 분석 전문가입니다. 제공된 재무 데이터를 바탕으로 종목을 분석해주세요."},
            {"role": "user", "content": f"종목코드: {stock_code}, 종목명: {stock_name}\n\n재무데이터:\n{financial_str}\n\n이 종목에 대한 분석과 투자 의견을 제공해주세요."}
        ],
        temperature=0.4,
        max_tokens=800
    )
    
    return response.choices[0].message.content
```

### 4.3 기술적 지표 해석
```python
def interpret_technical_indicators(indicators):
    """기술적 지표 데이터를 해석하여 매매 신호 제공"""
    
    # 지표 데이터를 문자열로 변환
    indicators_str = "\n".join([f"{k}: {v}" for k, v in indicators.items()])
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "당신은 기술적 분석 전문가입니다. 제공된 기술적 지표를 해석하여 매매 신호를 제공해주세요."},
            {"role": "user", "content": f"다음 기술적 지표를 분석하고 매매 신호를 제공해주세요:\n{indicators_str}"}
        ],
        temperature=0.3,
        max_tokens=500
    )
    
    return response.choices[0].message.content
```

### 4.4 시장 동향 분석
```python
def analyze_market_trend(market_data, news_headlines):
    """시장 데이터와 뉴스 헤드라인을 분석하여 시장 동향 예측"""
    
    # 시장 데이터와 뉴스 헤드라인 문자열 변환
    market_str = "\n".join([f"{k}: {v}" for k, v in market_data.items()])
    news_str = "\n".join(news_headlines)
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "당신은 금융 시장 분석 전문가입니다. 시장 데이터와 뉴스 헤드라인을 분석하여 시장 동향을 예측해주세요."},
            {"role": "user", "content": f"시장 데이터:\n{market_str}\n\n최근 뉴스 헤드라인:\n{news_str}\n\n이 정보를 바탕으로 현재 시장 동향과 단기 전망을 분석해주세요."}
        ],
        temperature=0.4,
        max_tokens=800
    )
    
    return response.choices[0].message.content
```

### 4.5 매매 전략 생성
```python
def generate_trading_strategy(stock_info, risk_level):
    """종목 정보와 위험 수준을 바탕으로 맞춤형 매매 전략 생성"""
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "당신은 트레이딩 전략 전문가입니다. 종목 정보와 위험 수준을 바탕으로 맞춤형 매매 전략을 제공해주세요."},
            {"role": "user", "content": f"종목 정보:\n{stock_info}\n\n위험 수준: {risk_level}\n\n이 정보를 바탕으로 구체적인 매매 전략을 제공해주세요. 진입점, 목표가, 손절가, 포지션 크기 등을 포함해주세요."}
        ],
        temperature=0.4,
        max_tokens=1000
    )
    
    return response.choices[0].message.content
```

## 5. 트레이딩봇 통합 예시

### 5.1 뉴스 기반 자동 매매 시스템
```python
import time
from datetime import datetime
import pandas as pd
from news_crawler import get_latest_news
from stock_api import get_stock_price, place_order

def news_based_trading_system():
    """뉴스 분석 기반 자동 매매 시스템"""
    
    # 관심 종목 리스트
    watch_list = {
        "005930": "삼성전자",
        "035720": "카카오",
        "035420": "NAVER",
        "051910": "LG화학",
        "000660": "SK하이닉스"
    }
    
    while True:
        # 최신 뉴스 수집
        latest_news = get_latest_news(list(watch_list.values()))
        
        for stock_code, stock_name in watch_list.items():
            # 해당 종목 관련 뉴스 필터링
            stock_news = [news for news in latest_news if stock_name in news["title"]]
            
            if stock_news:
                # 가장 최신 뉴스 분석
                latest_stock_news = stock_news[0]
                analysis = analyze_news(latest_stock_news["content"])
                
                # 분석 결과에서 매매 신호 추출
                if "매수" in analysis and "강력" in analysis:
                    # 현재 주가 확인
                    current_price = get_stock_price(stock_code)
                    
                    # 매수 주문
                    place_order(
                        stock_code=stock_code,
                        order_type="buy",
                        quantity=1,
                        price=current_price,
                        order_method="market"
                    )
                    
                    print(f"[{datetime.now()}] {stock_name} 매수 주문 실행: {latest_stock_news['title']}")
                
                elif "매도" in analysis and "강력" in analysis:
                    # 매도 주문 로직
                    # ...
                    
        # 1시간마다 실행
        time.sleep(3600)
```

### 5.2 AI 기반 종목 스크리너
```python
def ai_stock_screener(financial_criteria, technical_criteria, market_cap_min=None, market_cap_max=None):
    """AI 기반 종목 스크리너"""
    
    # 전체 종목 리스트 가져오기
    all_stocks = get_all_stocks()
    
    # 시가총액 필터링
    if market_cap_min or market_cap_max:
        filtered_stocks = filter_by_market_cap(all_stocks, market_cap_min, market_cap_max)
    else:
        filtered_stocks = all_stocks
    
    results = []
    
    for stock in filtered_stocks:
        # 재무 데이터 가져오기
        financial_data = get_financial_data(stock["code"])
        
        # 기술적 지표 가져오기
        technical_indicators = get_technical_indicators(stock["code"])
        
        # 종목 분석
        analysis = analyze_stock(stock["code"], stock["name"], financial_data)
        
        # 기술적 지표 해석
        technical_analysis = interpret_technical_indicators(technical_indicators)
        
        # 분석 결과 종합
        combined_analysis = f"재무 분석:\n{analysis}\n\n기술적 분석:\n{technical_analysis}"
        
        # 점수 계산 (예: "매수" 언급 횟수)
        score = combined_analysis.count("매수") - combined_analysis.count("매도")
        
        results.append({
            "code": stock["code"],
            "name": stock["name"],
            "score": score,
            "analysis": combined_analysis
        })
    
    # 점수 기준 정렬
    sorted_results = sorted(results, key=lambda x: x["score"], reverse=True)
    
    return sorted_results[:10]  # 상위 10개 종목 반환
```

## 6. 비용 관리 및 최적화

### 6.1 API 호출 비용
- GPT-4: 약 $0.03/1K 토큰 (입력), $0.06/1K 토큰 (출력)
- GPT-3.5-Turbo: 약 $0.0015/1K 토큰 (입력), $0.002/1K 토큰 (출력)

### 6.2 비용 최적화 전략
1. **캐싱 활용**
   ```python
   import hashlib
   import json
   import os
   
   def get_cached_response(prompt, model="gpt-3.5-turbo", cache_dir="cache"):
       """캐시된 응답 가져오기, 없으면 API 호출"""
       
       # 캐시 디렉토리 생성
       os.makedirs(cache_dir, exist_ok=True)
       
       # 프롬프트 해시 생성
       prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
       cache_file = os.path.join(cache_dir, f"{model}_{prompt_hash}.json")
       
       # 캐시 확인
       if os.path.exists(cache_file):
           with open(cache_file, "r") as f:
               return json.load(f)
       
       # API 호출
       response = client.chat.completions.create(
           model=model,
           messages=[{"role": "user", "content": prompt}],
           temperature=0.3
       )
       
       result = response.choices[0].message.content
       
       # 캐시 저장
       with open(cache_file, "w") as f:
           json.dump(result, f)
       
       return result
   ```

2. **모델 선택 최적화**
   - 간단한 분석: GPT-3.5-Turbo 사용
   - 복잡한 분석: GPT-4 사용

3. **토큰 사용량 최적화**
   - 불필요한 데이터 제거
   - 프롬프트 간결화
   - 출력 토큰 제한

### 6.3 일일 비용 제한 설정
```python
class APIBudgetManager:
    """API 사용 예산 관리자"""
    
    def __init__(self, daily_budget=5.0):
        self.daily_budget = daily_budget
        self.today_cost = 0
        self.today_date = datetime.now().date()
    
    def update_cost(self, tokens_in, tokens_out, model="gpt-4"):
        """비용 업데이트"""
        
        # 날짜 확인 및 초기화
        current_date = datetime.now().date()
        if current_date > self.today_date:
            self.today_cost = 0
            self.today_date = current_date
        
        # 모델별 비용 계산
        if model == "gpt-4":
            cost = (tokens_in * 0.03 + tokens_out * 0.06) / 1000
        elif model == "gpt-3.5-turbo":
            cost = (tokens_in * 0.0015 + tokens_out * 0.002) / 1000
        else:
            cost = 0
        
        self.today_cost += cost
        
        return self.today_cost < self.daily_budget
    
    def can_make_request(self, estimated_tokens_in, estimated_tokens_out, model="gpt-4"):
        """요청 가능 여부 확인"""
        
        # 날짜 확인 및 초기화
        current_date = datetime.now().date()
        if current_date > self.today_date:
            self.today_cost = 0
            self.today_date = current_date
        
        # 예상 비용 계산
        if model == "gpt-4":
            estimated_cost = (estimated_tokens_in * 0.03 + estimated_tokens_out * 0.06) / 1000
        elif model == "gpt-3.5-turbo":
            estimated_cost = (estimated_tokens_in * 0.0015 + estimated_tokens_out * 0.002) / 1000
        else:
            estimated_cost = 0
        
        return (self.today_cost + estimated_cost) < self.daily_budget
```

## 7. 주의사항

1. **API 키 보안**
   - API 키는 절대 코드에 직접 포함하지 말 것
   - 환경 변수나 안전한 저장소 사용

2. **응답 신뢰성**
   - AI 응답은 100% 정확하지 않을 수 있음
   - 중요한 결정은 추가 검증 필요

3. **비용 관리**
   - 무한 루프나 과도한 API 호출 주의
   - 예산 제한 설정 권장

4. **에러 처리**
   - API 호출 실패 시 적절한 에러 처리 필요
   - 재시도 로직 구현 권장

5. **속도 제한**
   - 과도한 API 호출 시 속도 제한 발생 가능
   - 적절한 지연 시간 설정 필요

## 8. 참고 자료

- [OpenAI API 공식 문서](https://platform.openai.com/docs/api-reference)
- [OpenAI 요금 정책](https://openai.com/pricing)
- [Python OpenAI 라이브러리](https://github.com/openai/openai-python) 