import sys, os

INTERP = os.path.join(os.environ['HOME'], '', 'venv', 'bin', 'python3')
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)
sys.path.append(os.getcwd())

from flask import Flask, render_template, request
import yfinance as yf
from flask_mysqldb import MySQL
import pandas as pd
from scipy.signal import argrelextrema
import plotly
import plotly.graph_objects as go
import numpy as np
import json
import math

with open('host.txt') as g:
    hostname = g.read()

with open('dbname.txt') as f:
    var = f.read()

with open('username.txt') as h:
    username = h.read()

with open('pwd.txt') as i:
    pwd = i.read()

application = Flask(__name__)

application.config['MYSQL_HOST'] = hostname
application.config['MYSQL_USER'] = username
application.config['MYSQL_PASSWORD'] = pwd
application.config['MYSQL_DB'] = var

mysql = MySQL(application)

@application.route('/simple')
def output_simple():
    out_text = 'hello world now'
    return render_template('output.html', arithmetic=out_text)

@application.route('/chain')
def opt_chain():
    return "Hello World"

@application.route('/numbers')
def hello():
    ticker = 'NQ=F'
    data = yf.download(tickers=ticker, period='6mo')
    return data.to_html(header='true', table_id='table')

@application.route('/testdb')
def data():
    cur = mysql.connection.cursor()
    cur.execute("SELECT firstName FROM MyUsers")
    mysql.connection.commit()
    remaining_rows = cur.fetchall()
    cur.close()
    df = pd.DataFrame(remaining_rows)
    return df.to_html(header='true', table_id='table')

@application.route('/chart', methods=['GET', 'POST'])
def graph():
    if request.method == "POST":
        details = request.form

        ticker = details['ticker']

        period = details['period']
        interval = details['interval']

        df = yf.download(tickers=ticker, period=period, interval=interval)
        #df = yf.download(tickers = ticker, start='2013-01-01', end='2014-12-31')

        df = df.reset_index()

        Order = 5

        max_idx = argrelextrema(df['Close'].values, np.greater, order=Order)[0]
        min_idx = argrelextrema(df['Close'].values, np.less, order=Order)[0]


        fig1 = go.Figure(data=[go.Candlestick(x=df['Date'],
                                              open=df['Open'],
                                              high=df['High'],
                                              low=df['Low'],
                                              close=df['Close'], showlegend=False)])
        Size = 15
        Width = 1

        fig1.add_trace(
            go.Scatter(
                name='Sell Here!',
                mode='markers',
                x=df.iloc[max_idx]['Date'],
                y=df.iloc[max_idx]['High'],
                marker=dict(
                    symbol=46,
                    color='darkred',
                    size=Size,
                    line=dict(
                        color='MediumPurple',
                        width=Width
                    )
                ),
                showlegend=True
            )
        )

        fig1.add_trace(
            go.Scatter(
                name='Buy Here!',
                mode='markers',
                x=df.iloc[min_idx]['Date'],
                y=df.iloc[min_idx]['Low'],
                marker=dict(
                    symbol=45,
                    color='forestgreen',
                    size=Size,
                    line=dict(
                        color='MediumPurple',
                        width=Width
                    )
                ),
                showlegend=True
            )
        )

        # fig1.show()

        fig1.update_layout(
            title=ticker, xaxis_rangeslider_visible=False
        )

        graphJSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)

        return render_template('neckline.html', graphJSON=graphJSON)
    return render_template('dropdown.html')

@application.route('/gauss', methods=['GET', 'POST'])
def gauss_chart():
    if request.method == "POST":
        details = request.form

        start = int(details['start'])
        end = int(details['end'])

        START = start
        END = end

        # ticker = yf.Ticker(symbol)

        ticker = details['ticker']

        period = details['period']
        interval = details['interval']

        # data = yf.download(tickers = ticker, start='2019-01-04', end='2021-06-09')
        data = yf.download(tickers=ticker, period=period, interval=interval)

        # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
        # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
        # data = yf.download("SPY AAPL", start="2017-01-01", end="2017-04-30")

        df1 = pd.DataFrame(data)

        df = df1.reset_index()

        last_row = df.index[-1] + 0.5

        df7 = df.rename(
            columns={'Date': 'date', 'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'},
            inplace=False)

        df7.to_csv('daily.csv')

        n = 1

        df3 = df7.groupby(np.arange(len(df7)) // n).max()
        # print('df3 max:', df3)

        df4 = df7.groupby(np.arange(len(df7)) // n).min()
        # print('df4 min:', df4)

        df5 = df7.groupby(np.arange(len(df7)) // n).first()
        # print('df5 open:', df5)

        df6 = df7.groupby(np.arange(len(df7)) // n).last()
        # print('df6 close:', df6)

        agg_df = pd.DataFrame()

        agg_df['date'] = df6['date']
        agg_df['low'] = df4['low']
        agg_df['high'] = df3['high']
        agg_df['open'] = df5['open']
        agg_df['close'] = df6['close']

        # print(agg_df)

        df2 = agg_df

        # print(df2)
        num_periods = 21

        # Gauss
        num_periods_gauss = 15.5
        df2['symbol'] = 2 * math.pi / num_periods_gauss
        df2['beta'] = (1 - np.cos(df2['symbol'])) / ((1.414) ** (0.5) - 1)
        df2['alpha'] = - df2['beta'] + (df2['beta'] ** 2 + df2['beta'] * 2) ** 2

        # Gauss equation
        # initialize
        df2.loc[0, 'gauss'] = df2.loc[0, 'close']
        df2.loc[1, 'gauss'] = df2.loc[1, 'close']
        df2.loc[2, 'gauss'] = df2.loc[2, 'close']
        df2.loc[3, 'gauss'] = df2.loc[3, 'close']
        df2.loc[4, 'gauss'] = df2.loc[4, 'close']

        for i in range(4, len(df2)):
            df2.loc[i, 'gauss'] = df2.loc[i, 'close'] * df2.loc[i, 'alpha'] ** 4 + (4 * (1 - df2.loc[i, 'alpha'])) * \
                                  df2.loc[i - 1, 'gauss'] \
                                  - (6 * ((1 - df2.loc[i, 'alpha']) ** 2) * df2.loc[i - 2, 'gauss']) \
                                  + (4 * (1 - df2.loc[i, 'alpha']) ** 3) * df2.loc[i - 3, 'gauss'] \
                                  - ((1 - df2.loc[i, 'alpha']) ** 4) * df2.loc[i - 4, 'gauss']

        # ATR

        num_periods_ATR = 21
        multiplier = 1

        df2['ATR_diff'] = df2['high'] - df2['low']
        df2['ATR'] = df2['ATR_diff'].ewm(span=num_periods_ATR, adjust=False).mean()
        # df2['Line'] = df2['WMA'].round(2)
        df2['Line'] = df2['gauss']
        df2['line_change'] = df2['Line'] / df2['Line'].shift(1)

        df2['upper_band'] = df2['Line'] + multiplier * df2['ATR']
        df2['lower_band'] = df2['Line'] - multiplier * df2['ATR']

        multiplier_1 = 1.6
        multiplier_2 = 2.3

        df2['upper_band_1'] = (df2['Line'] + multiplier_1 * df2['ATR']).round(2)
        df2['lower_band_1'] = (df2['Line'] - multiplier_1 * df2['ATR']).round(2)

        df2['upper_band_2'] = df2['Line'] + multiplier_2 * df2['ATR'].round(2)
        df2['lower_band_2'] = df2['Line'] - multiplier_2 * df2['ATR'].round(2)

        # df2.reset_index(drop=True)

        print(df2)

        select3 = df2[df2.index.isin({START})]  # Choose by index
        select4 = df2[df2.index.isin({END})]  # Choose by index

        idx1 = select3.index.item()
        idx2 = select4.index.item()

        selection_df = df2.loc[idx1:idx2]

        print(selection_df)

        y0 = max(selection_df['high'])
        y1 = min(selection_df['low'])

        x0 = selection_df.index[0] - 0.5
        x1 = selection_df.index[-1] + 0.5
        length_of_selection = x1 - x0

        selection_df = selection_df.reset_index(drop=True)
        selection_df = selection_df.drop('date', 1)
        last_row_select = selection_df.index[-1] + 2

        # calculate diff
        # take difference between 'high' of first df first row and second df last row
        df_high = df2['high'].iloc[-1]  # get last row of our starting point
        selection_df_high = selection_df['high'].iloc[0]  # get first row of selection
        # selection_df_high = selection_df['high'].iloc[-1]       # get last row of selection for reversal
        diff = selection_df_high - df_high
        print(diff)

        selection_df -= diff

        frames = [df2, selection_df]
        symmetric_df = pd.concat(frames)

        symmetric_df = symmetric_df.reset_index(drop=True)

        symmetric_df = symmetric_df.reset_index(drop=True)

        # print(symmetric_df)
        forecast_df = symmetric_df.tail(last_row_select)
        # print(forecast_df)

        text_y_position = forecast_df['high'].iloc[0] * 1.2

        fig1 = go.Figure(data=[go.Candlestick(x=df2.index,
                                              open=df2['open'],
                                              high=df2['high'],
                                              low=df2['low'],
                                              close=df2['close'])]

                         )

        fig1.add_trace(go.Candlestick(x=forecast_df.index,
                                      open=forecast_df['open'],
                                      high=forecast_df['high'],
                                      low=forecast_df['low'],
                                      close=forecast_df['close'])

                       )

        fig1.add_trace(
            go.Scatter(
                x=df2.index,
                y=df2['upper_band'].round(2),
                name='upper band',
                mode="lines",
                line=go.scatter.Line(color="gray"),
            )
        )

        fig1.add_trace(
            go.Scatter(
                x=df2.index,
                y=df2['lower_band'].round(2),
                name='lower band',
                mode="lines",
                line=go.scatter.Line(color="gray"),
            )
        )

        fig1.add_trace(
            go.Scatter(
                x=forecast_df.index,
                y=forecast_df['upper_band'].round(2),
                name='upper band',
                mode="lines",
                line=go.scatter.Line(color="gray"),
            )
        )

        fig1.add_trace(
            go.Scatter(
                x=forecast_df.index,
                y=forecast_df['lower_band'].round(2),
                name='lower band',
                mode="lines",
                line=go.scatter.Line(color="gray"),
            )
        )

        fig1.add_trace(
            go.Scatter(
                x=df2.index,
                y=df2['upper_band_1'].round(2),
                name='upper band_1',
                mode="lines",
                line=go.scatter.Line(color="gray"),
            )
        )

        fig1.add_trace(
            go.Scatter(
                x=df2.index,
                y=df2['lower_band_1'].round(2),
                name='lower band_1',
                mode="lines",
                line=go.scatter.Line(color="gray"),
            )
        )

        fig1.add_trace(
            go.Scatter(
                x=forecast_df.index,
                y=forecast_df['upper_band_1'].round(2),
                name='upper band_1',
                mode="lines",
                line=go.scatter.Line(color="gray"),
            )
        )

        fig1.add_trace(
            go.Scatter(
                x=forecast_df.index,
                y=forecast_df['lower_band_1'].round(2),
                name='lower band_1',
                mode="lines",
                line=go.scatter.Line(color="gray"),
            )
        )

        fig1.add_trace(
            go.Scatter(
                x=df2.index,
                y=df2['Line'],
                name="WMA",
                mode="lines",
                line=go.scatter.Line(color="blue"),
            )
        )

        fig1.add_trace(
            go.Scatter(
                x=forecast_df.index,
                y=forecast_df['Line'],
                name="WMA",
                mode="lines",
                line=go.scatter.Line(color="blue"),
            )
        )

        fig1.add_shape(type="rect",
                       x0=x0, y0=y0, x1=x1, y1=y1,
                       line=dict(color="RoyalBlue"), )

        fig1.update_layout(
            hovermode='x unified',
            title=ticker,
            showlegend=False,
            xaxis_rangeslider_visible=False
        )

        # width = 1800,
        # height = 800,

        fig1.add_vline(x=last_row, line_width=3, line_dash="dash", line_color="green")

        text_spacer = 10

        fig1.add_annotation(text='Actuals', x=last_row - text_spacer, y=text_y_position, showarrow=False, font_size=20)

        fig1.add_annotation(text='Forecast', x=last_row + text_spacer, y=text_y_position, showarrow=False, font_size=20)

        graphJSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)

        return render_template('gauss.html', graphJSON=graphJSON)
    return render_template('history.html')

@application.route('/calculatortqqq', methods=['GET', 'POST'])
def tqqq_target():
    if request.method == "POST":
        details = request.form

        target = details['ticker']
        target = int(target)
        tqqq_ticker = "TQQQ"

        df_tqqq = yf.download(tickers=tqqq_ticker, interval='5m', period ='1d')
        recent_tqqq = df_tqqq['Close'].iloc[-1]
        # print(df_tqqq['Close'])
        # print(recent_tqqq)

        nq_ticker = 'NQ=F'
        df_nq = yf.download(tickers=nq_ticker, interval='5m', period ='1d')
        recent_nq = df_nq['Close'].iloc[-1]
        # print(df_nq['Close'])
        # print(recent_nq)


        nq_current = recent_nq
        tqqq_current = recent_tqqq
        nq_target = target
        tqqq_target = ((nq_target / nq_current - 1) * 3 + 1)* tqqq_current
        # print(tqqq_target)
        tqqq_display = str(tqqq_target)
        df = pd.DataFrame(data=[tqqq_ticker, tqqq_display])
        return df.to_html(header='true', table_id='table')
    return render_template('target.html')

@application.route('/calculatortna', methods=['GET', 'POST'])
def tna_target():
    if request.method == "POST":
        details = request.form

        target = details['ticker']
        target = int(target)
        tqqq_ticker = "TNA"

        df_tqqq = yf.download(tickers=tqqq_ticker, interval='5m', period ='1d')
        recent_tqqq = df_tqqq['Close'].iloc[-1]
        # print(df_tqqq['Close'])
        # print(recent_tqqq)

        nq_ticker = 'RTY=F'
        df_nq = yf.download(tickers=nq_ticker, interval='5m', period ='1d')
        recent_nq = df_nq['Close'].iloc[-1]
        # print(df_nq['Close'])
        # print(recent_nq)


        nq_current = recent_nq
        tqqq_current = recent_tqqq
        nq_target = target
        tqqq_target = ((nq_target / nq_current - 1) * 3 + 1)* tqqq_current
        # print(tqqq_target)
        tqqq_display = str(tqqq_target)
        df = pd.DataFrame(data=[tqqq_ticker, tqqq_display])
        return df.to_html(header='true', table_id='table')
    return render_template('target.html')

@application.route('/calculatorfas', methods=['GET', 'POST'])
def fas_target():
    if request.method == "POST":
        details = request.form

        target = details['ticker']
        target = int(target)
        tqqq_ticker = "FAS"

        df_tqqq = yf.download(tickers=tqqq_ticker, interval='5m', period ='1d')
        recent_tqqq = df_tqqq['Close'].iloc[-1]
        # print(df_tqqq['Close'])
        # print(recent_tqqq)

        nq_ticker = 'XLF'
        df_nq = yf.download(tickers=nq_ticker, interval='5m', period ='1d')
        recent_nq = df_nq['Close'].iloc[-1]
        # print(df_nq['Close'])
        # print(recent_nq)


        nq_current = recent_nq
        tqqq_current = recent_tqqq
        nq_target = target
        tqqq_target = ((nq_target / nq_current - 1) * 3 + 1)* tqqq_current
        # print(tqqq_target)
        tqqq_display = str(tqqq_target)
        df = pd.DataFrame(data=[tqqq_ticker, tqqq_display])
        return df.to_html(header='true', table_id='table')
    return render_template('target.html')

@application.route('/calculatorupro', methods=['GET', 'POST'])
def upro_target():
    if request.method == "POST":
        details = request.form

        target = details['ticker']
        target = int(target)
        tqqq_ticker = "UPRO"

        df_tqqq = yf.download(tickers=tqqq_ticker, interval='5m', period ='1d')
        recent_tqqq = df_tqqq['Close'].iloc[-1]
        # print(df_tqqq['Close'])
        # print(recent_tqqq)

        nq_ticker = 'ES=F'
        df_nq = yf.download(tickers=nq_ticker, interval='5m', period ='1d')
        recent_nq = df_nq['Close'].iloc[-1]
        # print(df_nq['Close'])
        # print(recent_nq)


        nq_current = recent_nq
        tqqq_current = recent_tqqq
        nq_target = target
        tqqq_target = ((nq_target / nq_current - 1) * 3 + 1)* tqqq_current
        # print(tqqq_target)
        tqqq_display = str(tqqq_target)
        df = pd.DataFrame(data=[tqqq_ticker, tqqq_display])
        return df.to_html(header='true', table_id='table')
    return render_template('target.html')

@application.route('/calculator', methods=['GET', 'POST'])
def dropdown_fn():
    if request.method == "POST":
        details = request.form

        target = details['target']
        target = float(target)
        ticker_input = details['ticker']

        if ticker_input == "UPRO":
            tqqq_ticker = ticker_input

            df_tqqq = yf.download(tickers=tqqq_ticker, interval='5m', period ='1d')
            recent_tqqq = df_tqqq['Close'].iloc[-1]
            # print(df_tqqq['Close'])
            # print(recent_tqqq)

            nq_ticker = 'ES=F'
            df_nq = yf.download(tickers=nq_ticker, interval='5m', period ='1d')
            recent_nq = df_nq['Close'].iloc[-1]
            # print(df_nq['Close'])
            # print(recent_nq)


            nq_current = recent_nq
            tqqq_current = recent_tqqq
            nq_target = target
            tqqq_target = ((nq_target / nq_current - 1) * 3 + 1)* tqqq_current
            # print(tqqq_target)
            # tqqq_display = str(tqqq_target)
            tqqq_display = "{:.2f}".format(tqqq_target)
            out_text = tqqq_display
            # df = pd.DataFrame(data=[tqqq_ticker, tqqq_display])
            # print(df)

        elif ticker_input == "TQQQ":
            tqqq_ticker = ticker_input

            df_tqqq = yf.download(tickers=tqqq_ticker, interval='5m', period='1d')
            recent_tqqq = df_tqqq['Close'].iloc[-1]
            # print(df_tqqq['Close'])
            # print(recent_tqqq)

            nq_ticker = 'NQ=F'
            df_nq = yf.download(tickers=nq_ticker, interval='5m', period='1d')
            recent_nq = df_nq['Close'].iloc[-1]
            # print(df_nq['Close'])
            # print(recent_nq)

            nq_current = recent_nq
            tqqq_current = recent_tqqq
            nq_target = target
            tqqq_target = ((nq_target / nq_current - 1) * 3 + 1) * tqqq_current
            # print(tqqq_target)
            # tqqq_display = str(tqqq_target)
            tqqq_display = "{:.2f}".format(tqqq_target)
            out_text = tqqq_display
            # df = pd.DataFrame(data=[tqqq_ticker, tqqq_display])
            # print(df)

        elif ticker_input == "TNA":
            tqqq_ticker = ticker_input

            df_tqqq = yf.download(tickers=tqqq_ticker, interval='5m', period='1d')
            recent_tqqq = df_tqqq['Close'].iloc[-1]
            # print(df_tqqq['Close'])
            # print(recent_tqqq)

            nq_ticker = 'RTY=F'
            df_nq = yf.download(tickers=nq_ticker, interval='5m', period='1d')
            recent_nq = df_nq['Close'].iloc[-1]
            # print(df_nq['Close'])
            # print(recent_nq)

            nq_current = recent_nq
            tqqq_current = recent_tqqq
            nq_target = target
            tqqq_target = ((nq_target / nq_current - 1) * 3 + 1) * tqqq_current
            # print(tqqq_target)
            # tqqq_display = str(tqqq_target)
            tqqq_display = "{:.2f}".format(tqqq_target)
            out_text = tqqq_display
            # df = pd.DataFrame(data=[tqqq_ticker, tqqq_display])
            # print(df)

        elif ticker_input == "FAS":
            tqqq_ticker = ticker_input
            df_tqqq = yf.download(tickers=tqqq_ticker, interval='5m', period='1d')
            recent_tqqq = df_tqqq['Close'].iloc[-1]
            # print(df_tqqq['Close'])
            # print(recent_tqqq)

            nq_ticker = 'XLF'
            df_nq = yf.download(tickers=nq_ticker, interval='5m', period='1d')
            recent_nq = df_nq['Close'].iloc[-1]
            # print(df_nq['Close'])
            # print(recent_nq)

            nq_current = recent_nq
            tqqq_current = recent_tqqq
            nq_target = target
            tqqq_target = ((nq_target / nq_current - 1) * 3 + 1) * tqqq_current
            # print(tqqq_target)
            # tqqq_display = str(tqqq_target)
            tqqq_display = "{:.2f}".format(tqqq_target)
            out_text = tqqq_display
            # df = pd.DataFrame(data=[tqqq_ticker, tqqq_display])
            # print(df)

        return render_template('output.html', arithmetic=out_text)
    return render_template('dropdown_ticker.html')
