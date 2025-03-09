# 텔레그램 봇 연동 가이드

## 1. 텔레그램 봇 개요

텔레그램 봇은 트레이딩봇의 알림 시스템으로 활용할 수 있습니다. 주가 변동, 매매 신호, 주문 체결 등 중요한 이벤트가 발생했을 때 실시간으로 알림을 받을 수 있습니다.

## 2. 텔레그램 봇 생성 방법

### 2.1 BotFather를 통한 봇 생성
1. 텔레그램 앱에서 [@BotFather](https://t.me/BotFather) 검색
2. `/newbot` 명령어 입력
3. 봇 이름 입력 (예: MyTradingBot)
4. 봇 사용자명 입력 (예: my_trading_bot) - 반드시 '_bot'으로 끝나야 함
5. 생성 완료 후 API 토큰 받기 (예: `123456789:ABCDefGhIJKlmNoPQRsTUVwxyZ`)

### 2.2 봇과 대화 시작
1. 생성된 봇 사용자명으로 검색 (예: @my_trading_bot)
2. `/start` 명령어로 대화 시작

### 2.3 Chat ID 확인
1. 봇과 대화를 시작한 후 다음 URL 접속:
   `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   (YOUR_BOT_TOKEN을 실제 토큰으로 대체)
2. 응답에서 `"chat":{"id":123456789}` 형태로 Chat ID 확인

## 3. 기본 설정

### 3.1 환경 변수 설정
```python
# .env 파일에 텔레그램 봇 설정 저장
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

### 3.2 필요 패키지 설치
```bash
pip install python-telegram-bot python-dotenv
```

### 3.3 기본 설정 코드
```python
import os
import logging
from telegram import Bot
from telegram.ext import Updater, CommandHandler
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 텔레그램 봇 설정
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# 봇 인스턴스 생성
bot = Bot(token=BOT_TOKEN)
```

## 4. 주요 기능 및 사용 예시

### 4.1 기본 메시지 전송
```python
def send_message(message):
    """텔레그램으로 메시지 전송"""
    try:
        bot.send_message(chat_id=CHAT_ID, text=message)
        return True
    except Exception as e:
        logging.error(f"텔레그램 메시지 전송 실패: {e}")
        return False
```

### 4.2 차트 이미지 전송
```python
def send_chart(chart_path, caption=None):
    """차트 이미지 전송"""
    try:
        with open(chart_path, 'rb') as chart:
            bot.send_photo(
                chat_id=CHAT_ID,
                photo=chart,
                caption=caption
            )
        return True
    except Exception as e:
        logging.error(f"텔레그램 차트 전송 실패: {e}")
        return False
```

### 4.3 주문 알림 전송
```python
def send_order_notification(order_type, stock_code, stock_name, quantity, price):
    """주문 체결 알림 전송"""
    
    # 주문 유형에 따른 이모지 설정
    emoji = "🔴" if order_type == "매수" else "🔵"
    
    message = f"{emoji} {order_type} 주문 체결\n\n" \
              f"종목: {stock_name} ({stock_code})\n" \
              f"수량: {quantity}주\n" \
              f"가격: {price:,}원\n" \
              f"총액: {quantity * price:,}원\n" \
              f"시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    return send_message(message)
```

### 4.4 가격 알림 전송
```python
def send_price_alert(stock_code, stock_name, current_price, change_rate, alert_type):
    """가격 변동 알림 전송"""
    
    # 알림 유형에 따른 이모지 설정
    if alert_type == "상승":
        emoji = "🔺"
    elif alert_type == "하락":
        emoji = "🔻"
    elif alert_type == "목표가":
        emoji = "🎯"
    elif alert_type == "손절가":
        emoji = "⚠️"
    else:
        emoji = "ℹ️"
    
    message = f"{emoji} {stock_name} ({stock_code}) {alert_type} 알림\n\n" \
              f"현재가: {current_price:,}원\n" \
              f"등락률: {change_rate:.2f}%\n" \
              f"시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    return send_message(message)
```

### 4.5 매매 신호 알림
```python
def send_trading_signal(stock_code, stock_name, signal_type, strategy, confidence):
    """매매 신호 알림 전송"""
    
    # 신호 유형에 따른 이모지 설정
    if signal_type == "매수":
        emoji = "🟢"
    elif signal_type == "매도":
        emoji = "🔴"
    elif signal_type == "관망":
        emoji = "⚪"
    else:
        emoji = "ℹ️"
    
    # 신뢰도에 따른 별점 표시
    stars = "★" * int(confidence) + "☆" * (5 - int(confidence))
    
    message = f"{emoji} {signal_type} 신호 발생\n\n" \
              f"종목: {stock_name} ({stock_code})\n" \
              f"전략: {strategy}\n" \
              f"신뢰도: {stars} ({confidence}/5)\n" \
              f"시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    return send_message(message)
```

## 5. 봇 명령어 처리

### 5.1 기본 봇 설정
```python
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

def start_bot():
    """텔레그램 봇 시작"""
    
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    
    # 명령어 핸들러 등록
    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("status", status_command))
    dispatcher.add_handler(CommandHandler("portfolio", portfolio_command))
    
    # 봇 시작
    updater.start_polling()
    updater.idle()
```

### 5.2 명령어 핸들러 구현
```python
def start_command(update, context):
    """시작 명령어 처리"""
    user = update.effective_user
    update.message.reply_text(f'안녕하세요 {user.first_name}님! 트레이딩봇 알림 서비스입니다.')

def help_command(update, context):
    """도움말 명령어 처리"""
    help_text = """사용 가능한 명령어:
/start - 봇 시작
/help - 도움말 표시
/status - 시스템 상태 확인
/portfolio - 포트폴리오 현황 조회
"""
    update.message.reply_text(help_text)

def status_command(update, context):
    """시스템 상태 명령어 처리"""
    # 시스템 상태 정보 수집
    system_status = get_system_status()  # 별도 함수로 구현 필요
    
    status_text = f"""시스템 상태:
실행 시간: {system_status['uptime']}
CPU 사용률: {system_status['cpu_usage']}%
메모리 사용률: {system_status['memory_usage']}%
활성 전략: {system_status['active_strategies']}개
오늘 거래: {system_status['today_trades']}건
"""
    update.message.reply_text(status_text)

def portfolio_command(update, context):
    """포트폴리오 명령어 처리"""
    # 포트폴리오 정보 수집
    portfolio = get_portfolio_status()  # 별도 함수로 구현 필요
    
    portfolio_text = f"""포트폴리오 현황:
총 자산: {portfolio['total_value']:,}원
현금: {portfolio['cash']:,}원
주식: {portfolio['stock_value']:,}원
수익률: {portfolio['profit_rate']:.2f}%

보유 종목:
"""
    
    for stock in portfolio['stocks']:
        portfolio_text += f"- {stock['name']} ({stock['code']}): {stock['quantity']}주, {stock['current_price']:,}원, {stock['profit_rate']:.2f}%\n"
    
    update.message.reply_text(portfolio_text)
```

## 6. 트레이딩봇 통합 예시

### 6.1 실시간 알림 시스템
```python
class TelegramNotifier:
    """텔레그램 알림 관리자"""
    
    def __init__(self, bot_token, chat_id):
        self.bot = Bot(token=bot_token)
        self.chat_id = chat_id
        self.logger = logging.getLogger(__name__)
    
    def send_message(self, message):
        try:
            self.bot.send_message(chat_id=self.chat_id, text=message)
            return True
        except Exception as e:
            self.logger.error(f"텔레그램 메시지 전송 실패: {e}")
            return False
    
    def send_photo(self, photo_path, caption=None):
        try:
            with open(photo_path, 'rb') as photo:
                self.bot.send_photo(
                    chat_id=self.chat_id,
                    photo=photo,
                    caption=caption
                )
            return True
        except Exception as e:
            self.logger.error(f"텔레그램 사진 전송 실패: {e}")
            return False
    
    def send_document(self, doc_path, caption=None):
        try:
            with open(doc_path, 'rb') as doc:
                self.bot.send_document(
                    chat_id=self.chat_id,
                    document=doc,
                    caption=caption
                )
            return True
        except Exception as e:
            self.logger.error(f"텔레그램 문서 전송 실패: {e}")
            return False
```

### 6.2 키움 API 이벤트와 연동
```python
# kiwoom.py에 추가
class KiwoomAPI:
    # ... 기존 코드 ...
    
    def __init__(self):
        # ... 기존 코드 ...
        
        # 텔레그램 알림 설정
        self.notifier = TelegramNotifier(
            bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
            chat_id=os.getenv("TELEGRAM_CHAT_ID")
        )
    
    # 주문 체결 시 호출되는 이벤트 핸들러
    def OnReceiveChejanData(self, gubun, item_cnt, fid_list):
        # ... 기존 코드 ...
        
        # 주문 체결 정보 추출
        if gubun == "0":  # 주문 체결
            order_type = self.GetChejanData(905)  # 주문구분
            stock_code = self.GetChejanData(9001)  # 종목코드
            stock_name = self.GetChejanData(302)  # 종목명
            quantity = int(self.GetChejanData(900))  # 수량
            price = int(self.GetChejanData(901))  # 가격
            
            # 텔레그램 알림 전송
            self.notifier.send_message(
                f"{'🔴' if '매수' in order_type else '🔵'} {order_type} 주문 체결\n\n"
                f"종목: {stock_name} ({stock_code})\n"
                f"수량: {quantity}주\n"
                f"가격: {price:,}원\n"
                f"총액: {quantity * price:,}원"
            )
```

### 6.3 자동 매매 시스템과 연동
```python
# auto_trading.py에 추가
class AutoTradingSystem:
    # ... 기존 코드 ...
    
    def __init__(self):
        # ... 기존 코드 ...
        
        # 텔레그램 알림 설정
        self.notifier = TelegramNotifier(
            bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
            chat_id=os.getenv("TELEGRAM_CHAT_ID")
        )
    
    def execute_strategy(self, strategy_name):
        # ... 기존 코드 ...
        
        # 매매 신호 발생 시
        if signal == "BUY":
            # 매수 로직 실행
            # ...
            
            # 텔레그램 알림 전송
            self.notifier.send_message(
                f"🟢 매수 신호 발생\n\n"
                f"종목: {stock_name} ({stock_code})\n"
                f"전략: {strategy_name}\n"
                f"가격: {current_price:,}원\n"
                f"수량: {quantity}주"
            )
            
            # 차트 이미지가 있는 경우 전송
            if chart_path:
                self.notifier.send_photo(
                    chart_path,
                    caption=f"{stock_name} 매수 포인트"
                )
```

## 7. 알림 설정 관리

### 7.1 알림 설정 클래스
```python
class AlertSettings:
    """알림 설정 관리"""
    
    def __init__(self, settings_file="alert_settings.json"):
        self.settings_file = settings_file
        self.settings = self.load_settings()
    
    def load_settings(self):
        """설정 파일 로드"""
        if os.path.exists(self.settings_file):
            with open(self.settings_file, "r") as f:
                return json.load(f)
        else:
            # 기본 설정
            default_settings = {
                "price_alerts": True,
                "order_alerts": True,
                "signal_alerts": True,
                "daily_summary": True,
                "error_alerts": True,
                "quiet_hours": {
                    "enabled": False,
                    "start": "22:00",
                    "end": "08:00"
                }
            }
            self.save_settings(default_settings)
            return default_settings
    
    def save_settings(self, settings=None):
        """설정 저장"""
        if settings is None:
            settings = self.settings
        
        with open(self.settings_file, "w") as f:
            json.dump(settings, f, indent=4)
    
    def update_setting(self, key, value):
        """설정 업데이트"""
        if key in self.settings:
            self.settings[key] = value
            self.save_settings()
            return True
        return False
    
    def is_alert_enabled(self, alert_type):
        """알림 활성화 여부 확인"""
        if alert_type in self.settings:
            return self.settings[alert_type]
        return False
    
    def is_quiet_hours(self):
        """조용한 시간대 여부 확인"""
        if not self.settings["quiet_hours"]["enabled"]:
            return False
        
        now = datetime.now().time()
        start = datetime.strptime(self.settings["quiet_hours"]["start"], "%H:%M").time()
        end = datetime.strptime(self.settings["quiet_hours"]["end"], "%H:%M").time()
        
        if start <= end:
            return start <= now <= end
        else:  # 자정을 넘어가는 경우
            return now >= start or now <= end
```

### 7.2 알림 관리자 통합
```python
class NotificationManager:
    """알림 관리자"""
    
    def __init__(self, bot_token, chat_id, settings_file="alert_settings.json"):
        self.notifier = TelegramNotifier(bot_token, chat_id)
        self.settings = AlertSettings(settings_file)
        self.logger = logging.getLogger(__name__)
    
    def send_alert(self, alert_type, message, photo_path=None):
        """알림 전송"""
        # 알림 설정 확인
        if not self.settings.is_alert_enabled(alert_type):
            self.logger.info(f"{alert_type} 알림이 비활성화되어 있습니다.")
            return False
        
        # 조용한 시간대 확인 (에러 알림은 항상 전송)
        if alert_type != "error_alerts" and self.settings.is_quiet_hours():
            self.logger.info("조용한 시간대입니다. 알림이 지연됩니다.")
            return False
        
        # 알림 전송
        success = self.notifier.send_message(message)
        
        # 사진 전송 (있는 경우)
        if success and photo_path:
            success = self.notifier.send_photo(photo_path)
        
        return success
```

## 8. 주의사항

1. **봇 토큰 보안**
   - 봇 토큰은 절대 코드에 직접 포함하지 말 것
   - 환경 변수나 안전한 저장소 사용

2. **메시지 제한**
   - 텔레그램은 초당 메시지 수 제한 있음
   - 과도한 알림 발송 시 속도 제한 발생 가능

3. **오류 처리**
   - 네트워크 오류 등으로 메시지 전송 실패 가능성 고려
   - 적절한 예외 처리 및 재시도 로직 구현

4. **사용자 경험**
   - 너무 많은 알림은 사용자 경험 저하
   - 중요한 알림만 선별적으로 전송

5. **그룹 채팅**
   - 여러 사용자에게 알림을 보내려면 그룹 채팅 활용
   - 그룹 채팅에서는 봇을 관리자로 설정 필요

## 9. 참고 자료

- [텔레그램 봇 API 공식 문서](https://core.telegram.org/bots/api)
- [Python Telegram Bot 라이브러리](https://github.com/python-telegram-bot/python-telegram-bot)
- [텔레그램 봇 FAQ](https://core.telegram.org/bots/faq) 