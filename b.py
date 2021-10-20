import time
import pyupbit
import datetime
import numpy as np
from datetime import timedelta
from datetime import datetime
from pytz import timezone
from slacker import Slacker
import requests



def post_message(token, channel, text):
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )
 


myToken = ""
def dbgout(message):
    print(datetime.now().strftime('[%m/%d %H:%M:%S]'), message)
    strbuf = datetime.now().strftime('[%m/%d %H:%M:%S]') + message
    post_message(myToken,"#upbit", strbuf)



access = ''
secret = ''
upbit = pyupbit.Upbit(access, secret)



def get_balance(ticker):
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0



def get_start_time(ticker):

    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time


def get_current_price(ticker):
    url = "https://api.upbit.com/v1/candles/days"

    querystring = {"market": ticker, "count": "1"}

    response = requests.request("GET", url, params=querystring)
    return response.json()[0]['trade_price']

def get_target_price(ticker):

    df = pyupbit.get_ohlcv(ticker, interval="day", count=50)

    df['pclose'] = df['close'].shift(1)
    df['diff1'] = abs(df['high'] - df['low'])
    df['diff2'] = abs(df['pclose'] - df['high'])
    df['diff3'] = abs(df['pclose'] - df['low'])
    df['TR'] = df[['diff1', 'diff2', 'diff3']].max(axis=1)
    df['ATR'] = df['TR'].rolling(window=15).mean().shift(1)
    w_size = 5
    pb     = 1
    df['Moving Average'] = df['pclose'].rolling(window=w_size).mean()
    df['Upper'] = df['Moving Average'] + (df['ATR'] * pb) 
    df['Lower'] = df['Moving Average'] - (df['ATR'] * pb)
    df['%B'] = ( df['pclose'] - df['Lower']) / (df['Upper'] - df['Lower'])
    k = np.where((df.iloc[-1]['%B'] > 0.8), 0.0, 0.5)
    
    target_price = df.iloc[-1]['open'] + (df.iloc[-2]['high'] - df.iloc[-2]['low']) * k

    return target_price


def get_KC_price(ticker):
    """%K"""

    df = pyupbit.get_ohlcv(ticker, interval="day", count=50)

    df['pclose'] = df['close'].shift(1)
    df['diff1'] = abs(df['high'] - df['low'])
    df['diff2'] = abs(df['pclose'] - df['high'])
    df['diff3'] = abs(df['pclose'] - df['low'])
    df['TR'] = df[['diff1', 'diff2', 'diff3']].max(axis=1)
    df['ATR'] = df['TR'].rolling(window=15).mean().shift(1)
    w_size = 5
    pb     = 1
    df['Moving Average'] = df['pclose'].rolling(window=w_size).mean()
    df['Upper'] = df['Moving Average'] + (df['ATR'] * pb) 
    df['Lower'] = df['Moving Average'] - (df['ATR'] * pb)
    df['%B'] = ( df['pclose'] - df['Lower']) / (df['Upper'] - df['Lower'])
    target_price = round(df.iloc[-1]['%B'],2)

    return target_price



Start = 1
dbgout('auto trade start')



while True:

    try:
        time.sleep(1)

        coin_list = ["ETH"]
        for coin in coin_list:
            
            now = datetime.now()
            start_time = get_start_time("KRW-"+coin)
            end_time = start_time + timedelta(days=1)
            coin_balance = get_balance(coin)

            if Start == 1:
                Start = 0
                krw = get_balance("KRW")
                dbgout('balance: '+ str( round(krw,0) ) + 'won')
                
                for coin in coin_list:
                    current_price = get_current_price("KRW-"+coin)
                    target_price = get_target_price("KRW-"+coin)
                    KC_price = get_KC_price("KRW-"+coin)
                    dbgout(coin + ' current_price: ' + str(c_price))
                    dbgout(coin + ' target_price: ' + str(t_price))
                    dbgout(coin + ' %K: ' + str(KC_price))

            if start_time <= now <= end_time - timedelta(seconds=10):
                current_price = get_current_price("KRW-"+coin)
                target_price = get_target_price("KRW-"+coin)

                if target_price <= current_price:
                    
                    if coin_balance is None:
                        krw = get_balance("KRW")
                        dbgout("KRW-"+coin+': '+str(krw)+'won'+' buy')
                        upbit.buy_market_order("KRW-"+coin, krw*0.9995)

            else:
                Start = 1
                if coin_balance is not None:
                    upbit.sell_market_order("KRW-"+coin, coin_balance)
                    time.sleep(10)
                    krw = get_balance("KRW")
                    dbgout("KRW-"+coin+': '+str(krw)+'won'+' sell')
                    

    

    except Exception as e:
        dbgout(str(e))
        time.sleep(1)
