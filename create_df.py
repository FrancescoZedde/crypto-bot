import websocket
import json
import talib
import pprint
import numpy as np
from binance.client import Client
from binance.enums import *
import pandas as pd
import talib
import nsepy
'''
close = 0.22
amount = round(float((20/float(close))), 4)'''

import config

client = Client(config.api_key, config.private_key)

balance = client.get_asset_balance(asset='BUSD')

depth = client.get_order_book(symbol='BNBBTC')

klines = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_1MINUTE, "1 Jun, 2020")

"""
    "0.01634790",       // Open
    "0.80000000",       // High
    "0.01575800",       // Low
    "0.01577100",       // Close
    "148976.11427815",  // Volume 
"""

def data(klines):
    
    opens = []
    
    highs = []
    
    lows = []
    
    closes = []
    
    volumes = []    

    for i in range(len(klines)):
        
        open_price = klines[i][1]
 
        high_price = klines[i][2]
        
        low_price = klines[i][3]
        
        close_price = klines[i][4]
        
        volume = klines[i][5]
        
        
        opens.append(open_price)
        
        highs.append(high_price)
                        
        lows.append(low_price)
        
        closes.append(close_price)
        
        volumes.append(volume)
        
        
    df = pd.DataFrame(np.column_stack([opens, highs, lows, closes, volumes]), 
                      columns=['opens', 'highs', 'lows' ,'closes', 'volume'])
    
    
    df = df.astype(str).astype(float)
    
    print(df.dtypes)
    
    var_list = []
    
    results = []
    
    for t in range(len(df)):
        
        var = (df["closes"][t]/df["opens"][t]) * 100 - 100
        
        var_list.append(var)
        
        if var > 0:
            
            result = 1 #positive
            
        else:
            
            result = 0
            
        results.append(result)
        
    df['var'] = var_list
    
    
    df["SMA_12"] = df.iloc[:,3].rolling(window=12).mean()

    df['SMA_7'] = df.iloc[:,3].rolling(window=7).mean()

    df['SMA_3'] = df.iloc[:,3].rolling(window=3).mean()
    
    
    df["RSI_12"] = talib.RSI(df["closes"], 12)
    
    df["RSI_7"] = talib.RSI(df["closes"], 7)
    
    df["RSI_3"] = talib.RSI(df["closes"], 3)
    
    
    df["EMA_21"] = talib.EMA(df["closes"], timeperiod = 21)

    df["EMA_15"] = talib.EMA(df["closes"], timeperiod = 15)
    
    df["EMA_7"] = talib.EMA(df["closes"], timeperiod = 7)
    

    df["ATR_3"] = talib.ATR(df["highs"], df["lows"], df["closes"], timeperiod=3)

    df["ATR_6"] = talib.ATR(df["highs"], df["lows"], df["closes"], timeperiod=6)

    df["ATR_10"] = talib.ATR(df["highs"], df["lows"], df["closes"], timeperiod=10)
    
    
    df["WILL_3"] = talib.WILLR(df["highs"], df["lows"], df["closes"], timeperiod=3)
    
    df["WILL_7"] = talib.WILLR(df["highs"], df["lows"], df["closes"], timeperiod=7)
    
    df["WILL_10"] = talib.WILLR(df["highs"], df["lows"], df["closes"], timeperiod=10)

    
    df['results'] = results

    return df

        
df = data(klines)





df['results'] = df.results.shift(-1)
df['var'] = df.results.shift(-1)






df = df.dropna()

df["results"].value_counts()

df.to_csv("D:\df_btcusdt_1minute.csv")