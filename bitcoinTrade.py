import time
import pyupbit
import datetime
import numpy as np
from datetime import timedelta
from datetime import datetime
from pytz import timezone
from slacker import Slacker
import requests
import threading



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
    k = np.where((df.iloc[-1]['%B'] > 0.8), 0.0, np.where((df.iloc[-1]['%B'] < 0.8) & (df.iloc[-1]['%B'] >= 0.0), (1.0 - df.iloc[-1]['%B']), 0.5))
    
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

class Thread0(threading.Thread):
    def run(self) -> None:
        if Start[0] == 1 and Start[1] == 1:
            for i in range(len(coin_list)):
                krw[i] = get_balance("KRW") / (len(coin_list) - coin_list.index(coin_list[i]))
                current_price = get_current_price("KRW-"+coin_list[i])
                target_price = get_target_price("KRW-"+coin_list[i])
                KC_price = get_KC_price("KRW-"+coin_list[i])
                dbgout("KRW-"+coin_list[i]+ ' current: ' + str(current_price))
                dbgout("KRW-"+coin_list[i]+ ' target: ' + str(target_price))
                dbgout("KRW-"+coin_list[i]+ ' %K: ' + str(KC_price))
                Start[i] = 0
                time.sleep(1)


class Thread1(threading.Thread):
    def run(self) -> None:
        while True:
            try:
                time.sleep(1)
                now = datetime.now()
                start_time = get_start_time("KRW-"+coin_list[0])
                end_time = start_time + timedelta(days=1)
                coin_balance = get_balance(coin_list[0])

                if start_time <= now <= end_time - timedelta(seconds=10):
                    current_price = get_current_price("KRW-"+coin_list[0])
                    target_price = get_target_price("KRW-"+coin_list[0])

                    if target_price <= current_price:
                        
                        if coin_balance is None:
                            krw[0] = get_balance("KRW") / (len(coin_list) - coin_list.index(coin_list[0]))
                            if krw[0] >= 5000 + (krw[0]*0.9995):
                                dbgout("KRW-"+coin_list[0]+': '+str(round(krw[0],0))+'won'+' buy')
                                upbit.buy_market_order("KRW-"+coin_list[0], krw[0]*0.9995)

                else:
                    Start[0] = 1
                    if coin_balance is not None:
                        upbit.sell_market_order("KRW-"+coin_list[0], coin_balance)
                        time.sleep(1)
                        SellBalance[0] = get_current_price("KRW-"+coin_list[0]) * coin_balance
                        dbgout("KRW-"+coin_list[0]+': '+str(round(SellBalance[0],0))+'won'+' sell')
                    time.sleep(10)
                        
            except Exception as e:
                dbgout(str(e))
                time.sleep(1)



class Thread2(threading.Thread):
    def run(self) -> None:
        while True:

            try:
                time.sleep(1)
                now = datetime.now()
                start_time = get_start_time("KRW-"+coin_list[1])
                end_time = start_time + timedelta(days=1)
                coin_balance = get_balance(coin_list[1])

                if start_time <= now <= end_time - timedelta(seconds=10):
                    current_price = get_current_price("KRW-"+coin_list[1])
                    target_price = get_target_price("KRW-"+coin_list[1])

                    if target_price <= current_price:
                        
                        if coin_balance is None:
                            krw[1] = get_balance("KRW") / (len(coin_list) - coin_list.index(coin_list[1]))
                            if krw[1] >= 5000 + (krw[1]*0.9995):
                                dbgout("KRW-"+coin_list[1]+': '+str(round(krw[1],0))+'won'+' buy')
                                upbit.buy_market_order("KRW-"+coin_list[1], krw[1]*0.9995)

                else:
                    Start[1] = 1
                    if coin_balance is not None:
                        SellBalance[1] = get_current_price("KRW-"+coin_list[1]) * coin_balance
                        upbit.sell_market_order("KRW-"+coin_list[1], coin_balance)
                        time.sleep(1)
                        dbgout("KRW-"+coin_list[1]+': '+str(round(SellBalance[1],0))+'won'+' sell')
                    time.sleep(10)

            except Exception as e:
                dbgout(str(e))
                time.sleep(1)

if __name__ == '__main__':

    coin_list = ["ETH", "BTC"]
    dbgout('auto trade start')

    SellBalance = [None] * len(coin_list)
    krw = [None] * len(coin_list)
    Start = [None] * len(coin_list)

    t0 = Thread0()
    t0.start()
    t1 = Thread1()
    t1.start()
    t2 = Thread2()
    t2.start()
