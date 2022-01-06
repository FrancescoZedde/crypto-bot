import websocket
import json
import talib
import pprint
import numpy as np
from binance.client import Client
from binance.enums import *

amount = 0.001        
precision = 3
amt_str = "{:0.0{}f}".format(amount, precision)

client = Client('private', 
                'public')
print(client)

info = client.get_isolated_margin_symbol(symbol='BTCUSDT')

info = client.get_isolated_margin_account()


SOCKET = "wss://stream.binance.com:9443/ws/btcusdt@kline_1m"

TRADE_SYMBOL = "BTCUSDT"
TRADE_QUANTITY = 0.001

PERIOD = 3

type(TRADE_QUANTITY)

closes = []
opens = []
highs = []
lows = []

trade_results = []

order_count = 0
stop_loss_count = 0
take_profit_count = 0

in_position = False

PNL = 0
prev_PNL = 0
buy_price = 1
close = 0

def on_open(ws):
    print("opened connection")
    
def on_close(ws):
    print("closed connection")

def create_order(order):
    
    if order == "buy":
        '''
        loan = client.create_margin_loan(asset='USDT', amount='10', isIsolated=True, symbol="BTCUSDT")
        
        if loan:
            print("loan succed")
        else:
            print("problems with loan")
            
        ''' 
        
        amount = 0.001
        precision = 3
        amt_str = "{:0.0{}f}".format(amount, precision)
        
        order = client.create_margin_order(symbol='BTCUSDT',
                                           side=SIDE_BUY,
                                           type=ORDER_TYPE_MARKET,
                                           quantity=0.001,
                                           isIsolated = True)
        if order:
            print("order succed")            
        else:
            print("cant execute order")
            
    elif order == "sell":
    
        order = client.create_margin_order(symbol='BTCUSDT',
                                           side=SIDE_SELL,
                                           type=ORDER_TYPE_MARKET,
                                           quantity=0.001,
                                           isIsolated = True)
        
        #repay_loan = client.repay_margin_loan(asset='USDT', amount='1.1', isIsolated=True, symbol="BTCUSDT")
        
        if order:
            print("order succed")        
        else:
            print("cant execute order")
            

    
def on_message(ws, message):
    
    global closes, opens, highs, lows, order_count, stop_loss_count, take_profit_count,in_position,prev_PNL,trade_results, buy_price, PNL, close 
    
    print("received message")
    json_message = json.loads(message)
    #pprint.pprint(json_message)
    print(str(in_position))
    #print(str(order_count))
    
    candle = json_message["k"]
    

            
    is_candle_closed =  candle["x"]
    
    if is_candle_closed:
        
        close = candle["c"]
        ope_n = candle["o"]
        high = candle["h"]
        low = candle["l"]
        
        print("Positions opened since start: " + str(order_count))
        print("candle closed at {}".format(close))
        try:
            
            closes.append(float(close))
            opens.append(float(ope_n))
            highs.append(float(high))
            lows.append(float(low))
            
            print(len(closes))
            print(PERIOD)
            
        except:
            
            print("Problem")
            #print("Order Count: " + str(order_count))
            
        if len(closes) > PERIOD:
        
            try:
                
                np_closes = np.array(closes)
                np_opens = np.array(opens)
                np_highs = np.array(highs)
                np_lows = np.array(lows)
            
                rsi = talib.RSI(np_closes, PERIOD)
                will = talib.WILLR(np_highs, np_lows, np_closes, PERIOD)
            
                print("RSI & WILL")
                #print(rsi)
                #print(will)
                last_rsi = rsi[-1]
                last_will = will[-1]
            
                print(last_will)
                print(last_rsi)
                print(in_position)
                
            except:
                
                print("something not working.")
                
            
            if last_rsi < 30 and last_will < -80 and in_position == False:       
                
                print("BTC/USDT is Oversold ...")
                print("+ BUY ORDER +")
        
                order_count += 1
                    
                buy_price = close
                    
                in_position = True
                                
                #create_order("buy")
               
                order = client.create_margin_order(symbol='BTCUSDT',
                                           side=SIDE_BUY,
                                           type=ORDER_TYPE_MARKET,
                                           quantity=0.001,
                                           isIsolated = True)
                
                print("Now you are in_position: " + str(in_position))
                
                print("Orders since start: " + str(order_count))
        
            elif last_rsi > 70 and last_will > -20 and in_position == True:

                print("Closing position ...")
                print("+ SELL ORDER +")
                
                #PNL = ((100*close)/buy_price) - 100
                #print("PNL: " + str(PNL))

                #trade_results.append(float(PNL))
                
                in_position = False
                
                #create_order("sell")
                 
                order = client.create_margin_order(symbol='BTCUSDT',
                                           side=SIDE_SELL,
                                           type=ORDER_TYPE_MARKET,
                                           quantity=0.001,
                                           isIsolated = True)
                
                print("Now you are in_position: " + str(in_position))
            
            #PNL = (100*close)/buy_price - 100
            #print("PNL: " + str(PNL))
            
            elif in_position == True:

                #check position, stop loss take profit      
                print("check position:")
                try:
                    print(close)
                    print(buy_price)
                    
                    z = 100
                    j = 100*close
                    k = (j/buy_price)
                    
                    PNL = k - z
                    print(PNL)
                    PNL = (100*float(close))/float(buy_price) - 100
                    print(PNL)
                except:
                    print("Thats a problem")
                #print("PNL: " + str(PNL))
                
                if PNL < -1:
                 
                    print("Stop Loss ... Closing Position")
                    
                    print("PNL Trade: " + str(PNL))
                    
                    stop_loss_count += 1
                    
                    trade_results.append(float(PNL))
                    
                    in_position = False
                 
                elif PNL > 2:
                 
                    print("Take profit ... Closing Position")
                    
                    print("PNL Trade: " + str(PNL))
                    
                    take_profit_count += 1
                    
                    trade_results.append(float(PNL))
                    
                    in_position = False
                '''
                elif prev_PNL >= 1 and PNL < 1:
                    
                    print("Trailing Stop ... Closing Position")
                    
                    print("PNL Trade: " + str(PNL))
                    
                    trade_results.append(float(PNL))
                    
                    in_position = False
                
                prev_PNL = PNL
                '''
             
             
ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()




             ''' 
             
             
                else:
                print("Buy Buy Buy")
                #binance buy logic here
                order_succeeded = order(SIDE_BUY,TRADE_QUANTITY, TRADE_SYMBOL)
                if order_succeeded:
                in_position = True
             '''       




