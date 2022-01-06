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
import statsmodels.formula.api as sml
import plotly.graph_objects as go
import numpy as np
import plotly.io as pio
pio.renderers.default = 'browser'

client = Client('private', 'public  ')

info = client.get_all_tickers()
#select symbols // return a list with the returns the 20 cryptos with the highest volumes in 
#                  the quotation used (BUSD; USDT; BTC; etc)
def getSymbolsByQuote(quote):
    tickers = client.get_all_tickers()
    symbols = []
    for ticker in tickers:
        if ticker["symbol"].endswith(quote):
            kline = client.get_historical_klines(ticker["symbol"], Client.KLINE_INTERVAL_1DAY, "3 day ago UTC")
            try:
                print(ticker["symbol"])
                print(kline[0][7])
                if float(kline[0][7]) > 50000000:
                    symbols.append(ticker["symbol"])
            except:
                print("NO KLINE")
        else:
            print('not present')
    return symbols

symbols=getSymbolsByQuote('USDT')
'''
def higherVolumePairs(list_of_symbols):
    final_list = []
    for symbol in list_of_symbols:   
        kline = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1DAY, "3 day ago UTC")
        #print(kline[0][7])
        try:
            print(symbol)
            print(kline[0][7])
            if float(kline[0][7]) > 50000000:
                final_list.append(symbol)
        except:
            print("NO KLINE")
    return final_list

final = higherVolumePairs(symbols)
'''
def getData(symbols):
    df = pd.DataFrame()
    for symbol in symbols:
        klines = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1DAY, "1 Jan, 2018")
        closes = []
        for i in range(len(klines)):      
            close_price = klines[i][1]
            closes.append(close_price)
            #print(close_price)
        data = pd.DataFrame({symbol:closes})
        df = pd.concat([df, data], axis=1)        
        print(df)
    df = df.dropna(axis=1)
    df = df.astype(float)
    return df

data = getData(symbols)
#returns = data.pct_change().dropna()
def calcBeta(data):
    returns = data.pct_change().dropna()
    btc_returns = returns['BTCUSDT']
    btc_var = np.var(btc_returns)
    print(btc_var)
    cov_matrix = returns.cov()
    btc_cov = cov_matrix['BTCUSDT']
    print(btc_cov)
    #beta dei titoli
    betas = np.divide(btc_cov, btc_var)
    
    print(betas)    
    return betas

betas= calcBeta(data)

def startMontecarlo(data, betas, num_portfolios):
    columns_list = list(data)
    portfolio_values = ['ret','stdev','sharpe','Beta','Jensen']
    columns = portfolio_values + columns_list
    returns = data.pct_change().dropna()
    mean_daily_returns = returns.mean()
    cov_matrix = returns.cov()
    btc_returns = returns['BTCUSDT']
    risk_free = 0.01
    R_M = btc_returns.mean()
    results = np.zeros((6+len(betas)-1,num_portfolios))
    for i in range(num_portfolios):
    #select random weights for portfolio holdings
        weights = np.random.random(len(betas))
    #rebalance weights to sum to 1
        weights /= np.sum(weights)
    #calculate portfolio return and volatility
        portfolio_return = np.sum(mean_daily_returns * weights) * 252
        portfolio_std_dev = np.sqrt(np.dot(weights.T,np.dot(cov_matrix, weights))) * np.sqrt(252)
        portfolio_beta = np.sum(betas * weights)     
    #store results in results array
        results[0,i] = portfolio_return
        results[1,i] = portfolio_std_dev
    #store Sharpe Ratio, Beta and Jensen 
        results[2,i] = (results[0,i]-risk_free) / results[1,i]
        results[3,i] = portfolio_beta
        results[4,i] = (portfolio_return - risk_free - portfolio_beta * (R_M - risk_free))   
        for j in range(len(weights)):
            results[j+5,i] = weights[j]
            
    results_frame = pd.DataFrame(results.T,columns=columns)
    return results_frame

montecarlo_results = startMontecarlo(data, betas, 100000)

def createScatterPlot(montecarlo_simulation):
    trace = go.Scattergl(
    x = montecarlo_results['stdev'],
    y = montecarlo_results['ret'],
    hoverinfo = "x+y+text",
    hovertext ='(Expected return, Standard deviation ',
    mode='markers',
    marker=dict(
            colorscale='Viridis',
            line_width=1
            )
    )
    layout = go.Layout(
            title='CAPM In Crypto Market',
            #hovermode='closest',
            xaxis=dict(title='Standard Deviation', type='log', autorange=True),
            yaxis=dict(title='Returns', type='log', autorange=True))
    
    fig = go.Figure(data=[trace], layout=layout)
            
    return fig.show()

createScatterPlot(montecarlo_results)
