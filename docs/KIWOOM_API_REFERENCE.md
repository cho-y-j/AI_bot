# 키움증권 OpenAPI+ 레퍼런스

## 1. API 개요

키움증권의 OpenAPI+는 32비트 COM 기반의 API로, 실시간 시세 조회, 주문, 계좌 조회 등 다양한 기능을 제공합니다.

## 2. 주요 클래스 및 메서드

### 2.1 KOA_Functions (키움 OpenAPI 기본 함수)

#### 로그인 관련
```python
# 로그인 요청
CommConnect()

# 로그인 상태 확인
GetConnectState()  # 0: 연결안됨, 1: 연결됨

# 로그인 정보
GetLoginInfo(tag)  # tag: ACCOUNT_CNT, ACCLIST, USER_ID, USER_NAME, GetServerGubun 등
```

#### 조회 관련
```python
# TR 요청
SetInputValue(id, value)  # TR 입력값 설정
CommRqData(rqname, trcode, next, screen)  # TR 데이터 요청

# TR 수신 데이터 처리
GetRepeatCnt(trcode, rqname)  # 멀티데이터 개수
GetCommData(trcode, rqname, index, item)  # 데이터 가져오기
```

#### 실시간 데이터 관련
```python
# 실시간 등록/해제
SetRealReg(screen, code_list, fid_list, opt_type)  # 실시간 등록
SetRealRemove(screen, code)  # 실시간 해제

# 실시간 데이터 처리
GetCommRealData(code, fid)  # 실시간 데이터 가져오기
```

#### 주문 관련
```python
# 주문 요청
SendOrder(rqname, screen, acc, order_type, code, quantity, price, hoga, order_no)
```

### 2.2 주요 TR 코드

#### 시세 조회
- `opt10001`: 주식기본정보요청
- `opt10002`: 주식거래원요청
- `opt10003`: 체결정보요청
- `opt10004`: 주식호가요청
- `opt10005`: 주식일주월시분요청
- `opt10059`: 종목별투자자요청
- `opt10080`: 주식분봉차트조회요청
- `opt10081`: 주식일봉차트조회요청
- `opt10082`: 주식주봉차트조회요청
- `opt10083`: 주식월봉차트조회요청

#### 계좌 조회
- `opw00001`: 예수금상세현황요청
- `opw00018`: 계좌평가잔고내역요청

### 2.3 실시간 FID

#### 주요 FID 목록
- `10`: 현재가
- `11`: 전일대비
- `12`: 등락율
- `13`: 누적거래량
- `14`: 누적거래대금
- `15`: 거래량
- `16`: 시가
- `17`: 고가
- `18`: 저가
- `20`: 체결시간
- `27`: 최우선매도호가
- `28`: 최우선매수호가
- `41`: 매도호가1
- `51`: 매수호가1
- `61`: 매도호가수량1
- `71`: 매수호가수량1
- `228`: 체결강도
- `308`: 주식시간외호가구분
- `310`: 전일거래량대비

## 3. 이벤트 처리

### 3.1 TR 이벤트
```python
# TR 수신 이벤트
def OnReceiveTrData(self, screen, rqname, trcode, record, next):
    pass

# 메시지 수신 이벤트
def OnReceiveMsg(self, screen, rqname, trcode, msg):
    pass
```

### 3.2 실시간 이벤트
```python
# 실시간 데이터 수신 이벤트
def OnReceiveRealData(self, code, real_type, real_data):
    pass
```

### 3.3 주문 이벤트
```python
# 주문접수/체결 수신 이벤트
def OnReceiveChejanData(self, gubun, item_cnt, fid_list):
    pass

# 주문 서버 접수 이벤트
def OnReceiveRealCondition(self, code, type, condition_name, condition_index):
    pass
```

## 4. 주문 유형

### 4.1 매수/매도 주문
```python
# 매수 주문
kiwoom.SendOrder("매수주문", "0101", account, 1, code, quantity, price, "00", "")

# 매도 주문
kiwoom.SendOrder("매도주문", "0101", account, 2, code, quantity, price, "00", "")
```

### 4.2 주문 유형 코드
- `1`: 신규매수
- `2`: 신규매도
- `3`: 매수취소
- `4`: 매도취소
- `5`: 매수정정
- `6`: 매도정정

### 4.3 호가 구분 코드
- `00`: 지정가
- `03`: 시장가
- `05`: 조건부지정가
- `06`: 최유리지정가
- `07`: 최우선지정가
- `10`: 지정가IOC
- `13`: 시장가IOC
- `16`: 최유리IOC
- `20`: 지정가FOK
- `23`: 시장가FOK
- `26`: 최유리FOK
- `61`: 장전시간외종가
- `62`: 시간외단일가
- `81`: 장후시간외종가

## 5. 에러 코드

### 5.1 주요 에러 코드
- `-10`: 실패
- `-100`: 사용자정보교환실패
- `-101`: 서버접속실패
- `-102`: 버전처리실패
- `-103`: 개인방화벽실패
- `-104`: 메모리보호실패
- `-105`: 함수입력값오류
- `-106`: 통신연결종료
- `-107`: 보안모듈오류
- `-108`: 공인인증실패
- `-200`: 시세조회과부하
- `-201`: 전문작성초기화실패
- `-202`: 전문작성입력값오류
- `-203`: 데이터없음
- `-204`: 조회가능한종목수초과
- `-205`: 데이터수신실패
- `-206`: 조회가능한FID수초과
- `-207`: 실시간해제오류
- `-300`: 입력값오류
- `-301`: 계좌비밀번호없음
- `-302`: 타인계좌사용오류
- `-303`: 주문가격이상
- `-304`: 주문가격이하
- `-305`: 주문수량이상
- `-306`: 주문수량이하
- `-307`: 주문전송실패
- `-308`: 주문전송불가
- `-309`: 주문수량제한초과
- `-310`: 주문금액제한초과
- `-340`: 계좌정보없음
- `-500`: 종목코드없음

## 6. 사용 예시

### 6.1 로그인 및 계좌 정보 조회
```python
# 로그인
kiwoom.CommConnect()

# 계좌 목록 조회
account_num = kiwoom.GetLoginInfo("ACCNO")
account_list = account_num.split(';')
account = account_list[0]

# 예수금 조회
kiwoom.SetInputValue("계좌번호", account)
kiwoom.SetInputValue("비밀번호", "")
kiwoom.SetInputValue("비밀번호입력매체구분", "00")
kiwoom.SetInputValue("조회구분", "2")
kiwoom.CommRqData("예수금조회", "opw00001", 0, "0101")
```

### 6.2 종목 시세 조회
```python
# 종목 기본 정보 조회
kiwoom.SetInputValue("종목코드", "005930")  # 삼성전자
kiwoom.CommRqData("종목기본정보", "opt10001", 0, "0101")

# 일봉 데이터 조회
kiwoom.SetInputValue("종목코드", "005930")
kiwoom.SetInputValue("기준일자", "20230101")
kiwoom.SetInputValue("수정주가구분", "1")
kiwoom.CommRqData("일봉데이터", "opt10081", 0, "0101")
```

### 6.3 실시간 시세 등록
```python
# 실시간 시세 등록
codes = "005930;035720"  # 삼성전자, 카카오
fids = "9001;10;13"  # 종목코드;현재가;누적거래량
kiwoom.SetRealReg("0150", codes, fids, "0")
```

### 6.4 주문 실행
```python
# 매수 주문 (시장가)
kiwoom.SendOrder("시장가매수", "0101", account, 1, "005930", 1, 0, "03", "")

# 매도 주문 (지정가)
kiwoom.SendOrder("지정가매도", "0101", account, 2, "005930", 1, 70000, "00", "")
```

## 7. 주의사항

1. **32비트 환경 필수**
   - OpenAPI+는 32비트 COM 기반이므로 32비트 Python 환경 필수

2. **TR 요청 제한**
   - 초당 5회, 1분당 100회로 제한됨
   - 과도한 요청 시 서비스 제한될 수 있음

3. **실시간 데이터 제한**
   - 실시간 등록 종목 수에 제한 있음
   - 불필요한 실시간 등록은 해제 필요

4. **주문 오류 처리**
   - 주문 전송 후 반드시 OnReceiveChejanData 이벤트에서 처리 결과 확인
   - 주문 실패 시 에러 코드 확인 필요

5. **로그인 세션**
   - 로그인 세션 유지 시간 제한 있음
   - 장시간 사용 시 주기적 재로그인 필요

## 8. 참고 자료

- [키움증권 OpenAPI+ 개발 가이드](https://download.kiwoom.com/web/openapi/kiwoom_openapi_plus_devguide_ver_1.5.pdf)
- [키움증권 OpenAPI+ 개발 샘플](https://www.kiwoom.com/h/customer/download/VOpenApiSample)
- [키움증권 OpenAPI+ 기술 포럼](https://bbn.kiwoom.com/bbn.do?cmd=techForumList) 