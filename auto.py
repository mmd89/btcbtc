# import time
# import pyupbit
# import datetime

# access = "fX3IHacaarGpBgxe9rVNh6K6WJ3V9MU9Dsv8zhJf"
# secret = "EDJcNJQAE9DxZ0YwLynonjGBiUISMTmAVY2fHXkr"  

# def get_target_price(ticker, k):
#     """변동성 돌파 전략으로 매수 목표가 조회"""
#     df = pyupbit.get_ohlcv(ticker, interval="day", count=2) #2일치에 대한 일 데이터를 조회
#     target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
#     #df.iloc[0]['close']는 다음날 시가와 똑같고 여기에 + () 변동폭을 설정해서
#     #target_price를 설정해주고
#     #그걸 리턴해준다.
#     return target_price

# def get_start_time(ticker):
#     """시작 시간 조회"""
#     df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
#     start_time = df.index[0]
#     return start_time
# '''
# ohlcv 를 조회할 때 일봉으로 조회하면 (interval="day") 여기서 확인
# 이게 기본 9시로 설정되어 있음.
# 그것을 받아올 수 있도록 get.ohlcv를 이용해서 df에 넣고 df.index[0]의 위치가 시간값이니까
# 그걸 return해서 start_time으로 해준다.
# 그럼 def get_start_time(ticker) 는 시간값을 확인할 수 있는 파라미터가 된다.
# '''


# def get_balance(ticker):
#     """잔고 조회"""
#     balances = upbit.get_balances()
#     for b in balances:
#         if b['currency'] == ticker:
#             if b['balance'] is not None:
#                 return float(b['balance'])
#             else:
#                 return 0
#     return 0

# def get_current_price(ticker):
#     """현재가 조회"""
#     return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

# # 로그인
# upbit = pyupbit.Upbit(access, secret)
# print("autotrade start")

# # 자동매매 시작
# while True:
#     try:
#         #9시 < 현재 < 8시59분50초
#         now = datetime.datetime.now() #현재시간
#         start_time = get_start_time("KRW-BTC") #시작시간 get
#         end_time = start_time + datetime.timedelta(days=1) #끝나는 시간

#         if start_time < now < end_time - datetime.timedelta(seconds=10): 
#             target_price = get_target_price("KRW-BTC", 0.5)         #변동성 돌파 전략으로
#             current_price = get_current_price("KRW-BTC")            #현재 가격이 
#             if target_price < current_price:                        #target_price(목표가)보다 높다면
#                 krw = get_balance("KRW")                            # 그때 krw에 내 원화 잔고를 조회하고
#                 if krw > 5000:                                      # 이게 최소거래 금액인 5000원이 이상이면
#                     upbit.buy_market_order("KRW-BTC", krw*0.9995)   #코인을 매수한다. krw*0.9995는 수수료
#         else:                                                       #설정시간 이외의 시간 (10초)때는 
#             btc = get_balance("BTC")                                #btc 잔고를 가져와서
#             if btc > 0.00008:                                       #현재 잔고가 5000원 이상이면 (0.00008)
#                 upbit.sell_market_order("KRW-BTC", btc*0.9995)      #전량 매도 하는 코드 작성 (수수료를 생각해 9995)
#         time.sleep(1)
#     except Exception as e:
#         print(e)
#         time.sleep(1)
        
        
        
import time
import pyupbit
import datetime
import schedule
from fbprophet import Prophet

access = "fX3IHacaarGpBgxe9rVNh6K6WJ3V9MU9Dsv8zhJf"
secret = "EDJcNJQAE9DxZ0YwLynonjGBiUISMTmAVY2fHXkr"  

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

predicted_close_price = 0
def predict_price(ticker): #AI예측 함수 추가
    """Prophet으로 당일 종가 가격 예측"""
    global predicted_close_price
    df = pyupbit.get_ohlcv(ticker, interval="minute60")
    df = df.reset_index()
    df['ds'] = df['index']
    df['y'] = df['close']
    data = df[['ds','y']]
    model = Prophet()
    model.fit(data)
    future = model.make_future_dataframe(periods=24, freq='H')
    forecast = model.predict(future)
    closeDf = forecast[forecast['ds'] == forecast.iloc[-1]['ds'].replace(hour=9)]
    if len(closeDf) == 0:
        closeDf = forecast[forecast['ds'] == data.iloc[-1]['ds'].replace(hour=9)]
    closeValue = closeDf['yhat'].values[0]
    predicted_close_price = closeValue
predict_price("KRW-BTC")
schedule.every().hour.do(lambda: predict_price("KRW-BTC"))

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)
        schedule.run_pending()

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price("KRW-BTC", 0.7)
            current_price = get_current_price("KRW-BTC")
            if target_price < current_price and current_price < predicted_close_price: #현재가격(current_price) 보다 예측된 종가(predicted_close_price) 더 가격이 높은경우 매수 진행
                krw = get_balance("KRW")
                if krw > 5000:
                    upbit.buy_market_order("KRW-BTC", krw*0.9995)
        else:
            btc = get_balance("BTC")
            if btc > 0.00008:
                upbit.sell_market_order("KRW-BTC", btc*0.9995)
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
        