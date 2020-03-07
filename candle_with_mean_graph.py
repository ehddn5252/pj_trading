import pandas_datareader.data as web
import datetime
import matplotlib.pyplot as plt
import mpl_finance
import matplotlib.ticker as ticker

start = datetime.datetime(2018,10,1)
end = datetime.datetime(2020,2,26)

skhynix = web.DataReader("000660.KS", "yahoo", start, end)
skhynix = skhynix[skhynix['Volume']>0]

ma5 = skhynix['Close'].rolling(window=5).mean()
ma10 = skhynix['Close'].rolling(window=10).mean()
ma20 = skhynix['Close'].rolling(window=20).mean()
ma60 = skhynix['Close'].rolling(window=60).mean()
ma120 = skhynix['Close'].rolling(window=120).mean()

skhynix['MA5'] = ma5
skhynix['MA10'] = ma10
skhynix['MA20'] = ma20
skhynix['MA60'] = ma60
skhynix['MA120'] = ma120


fig = plt.figure(figsize=(12,8))
ax = fig.add_subplot(111)
day_list = range(len(skhynix))



name_list = []
for day in skhynix.index:
    name_list.append(day.strftime('%d'))

ax.xaxis.set_major_locator(ticker.FixedLocator(day_list))
ax.xaxis.set_major_formatter(ticker.FixedFormatter(name_list))

mpl_finance.candlestick2_ohlc(ax, skhynix["Open"], skhynix["High"], skhynix["Low"], skhynix["Close"], width=0.5, colorup='r', colordown='b')

ax.plot(day_list, skhynix['MA5'], label='MA5')
ax.plot(day_list, skhynix['MA10'], label='MA10')
ax.plot(day_list, skhynix['MA20'], label='MA20')
ax.plot(day_list, skhynix['MA60'], label='MA60')
ax.plot(day_list, skhynix['MA120'], label='MA120')

plt.legend(loc=6)
plt.tight_layout()
plt.show()
