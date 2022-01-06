#Backtest

import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import plotly.io as pio
import plotly.express as px
pio.renderers.default='browser'
import kaleido
df = pd.read_csv("D:\df_btcusdt_1hour.csv", index_col=False)
#df = df.drop(df.columns[[0]], axis=1) 


df = df.loc[:10]

fig = go.Figure(data=[go.Candlestick(x=df['Unnamed: 0'],
                open=df['opens'],
                high=df['highs'],
                low=df['lows'],
                close=df['closes'])])
fig.show()

fig.write_image("D:/fig.png")


in_position = False

all_trades = []

list_usdt = []

usdt = 100

win_count = 0

loss_count = 0

stop_loss_count = 0

take_profit_count = 0

#ema_diff = 

#Momentum
#Williams Percent Range

#Volatility
#Average True Range


for i in range(len(df)):

    
    if df["RSI_3"][i] < 15 and in_position==False and df["WILL_3"][i] < -10:
        
        usdt = usdt - 10
        
        #update position
        in_position=True
                
        print("+++ BUY! +++ Position: " + str(in_position))
        
        print("Loop Number: " + str(i))

        
        buy_price = df["closes"][i]
        
        print("Buy Price: "+ str(buy_price) + "\n\n")
        
    elif df["RSI_3"][i] > 85 and in_position==True and df["WILL_3"][i] > -90:
        
        
        #update position
        in_position=False
        
        sell_price = df["closes"][i]
        
        PNL = (100*sell_price)/buy_price - 100
        
        all_trades.append(PNL)
        
        profit = 10 + (10/100 * PNL)*10
        
        print("+++ SELL! (RSI > 70) +++ Position: " + str(in_position))
        print("+++ Loop Number: " + str(i) )
        print("PNL: "+ str(PNL))
        print("Profit/Loss: "+ str(profit))
        
        print("buy price: " + str(buy_price))
        print("sell price: " + str(sell_price))
        
        
    
        if PNL > 0:
            
            win_count+=1
        else:
            
            loss_count+=1
        
        usdt = usdt + profit
        
        list_usdt.append(usdt)
        
        print("Conto:" + str(usdt) + "\n\n")

        #print("Sell!   Position: " + str(in_position) + " PNL: "+str(PNL))
     
    #check position (StopLoss & TakeProfit)
        
    if in_position == True:
        
        actual_position = ((100*df["closes"][i])/buy_price) -100
        
        print("Actual Position: " + str(actual_position) + "\n ")
        
        if actual_position < -2:
            
            print("+++ STOP LOSS CLOSING POSITION: \n")
            
            profit_loss = 10 + (10/100 * actual_position)*10
            
            print("Loss with StopLoss: " + str(profit_loss))
            
            all_trades.append(actual_position)
            
            usdt = usdt + profit_loss
            
            list_usdt.append(usdt)
            
            stop_loss_count+=2
            
            in_position = False       
            
        if actual_position > 0.5:
            
            print("+++ TAKE PROFIT CLOSING POSITION: \n")
            
            profit_win = 10 + (10/100 * actual_position)*10
            
            print("Win with Take Profit: " + str(profit_win))
            
            all_trades.append(actual_position)
            
            usdt = usdt + profit_win
            
            list_usdt.append(usdt)
            
            take_profit_count+=1
            
            in_position = False
            
            

            
import statistics
statistics.mean(all_trades)


from matplotlib import pyplot as plt

plt.plot(list_usdt)
plt.show()       
            
            
            
        #position stats
        position_PNL = 
5 *2