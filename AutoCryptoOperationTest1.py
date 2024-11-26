import requests
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta, timezone

def fetch_candlestick_data(pair='btc_jpy', candlestick_type='1hour', date_str='20221001'):
    url = f'https://public.bitbank.cc/{pair}/candlestick/{candlestick_type}/{date_str}'
    response = requests.get(url)
    data = response.json()
    return data

def get_candlestick_data_for_month(pair='btc_jpy', candlestick_type='1hour'):
    all_data = []
    today = datetime.now(timezone.utc)
    one_month_ago = today - timedelta(days=30)
    
    current_date = today
    while current_date >= one_month_ago:
        date_str = current_date.strftime('%Y%m%d')
        data = fetch_candlestick_data(pair, candlestick_type, date_str)
        if data.get('success') == 1:  # 正常にデータを取得できた場合
            all_data.extend(data['data']['candlestick'][0]['ohlcv'])
        current_date -= timedelta(days=1)  # 日付を1日遡る
    return all_data

def sellBTC(priceBTC, myJPY, myBTC):
    myJPY += priceBTC * myBTC
    myBTC = 0
    return myJPY, myBTC

def buyBTC(priceBTC, myJPY, myBTC):
    myBTC += myJPY / priceBTC
    myJPY = 0
    return myJPY, myBTC

def main():
    pair = 'btc_jpy'
    candlestick_type = '1hour'
    
    # 直近1ヶ月間のデータを取得
    data = get_candlestick_data_for_month(pair, candlestick_type)
    
    myJPY = 1000000  # 初期JPY
    myBTC = 0        # 初期BTC
    hasBTC = False   # 初期状態

    for i in range(1, len(data)):
        if i == 0:
            continue

        prev_close = float(data[i - 1][3])  # 前のローソク足の終値
        curr_close = float(data[i][3])     # 現在のローソク足の終値

        if prev_close < curr_close and hasBTC:
            myJPY, myBTC = sellBTC(curr_close, myJPY, myBTC)
            hasBTC = False  # BTCを売却したので保有状態を更新
        
        elif prev_close > curr_close and not hasBTC:
            myJPY, myBTC = buyBTC(curr_close, myJPY, myBTC)
            hasBTC = True  # BTCを購入したので保有状態を更新
            
    print("BTC: " + str(myBTC))
    print("JPY: " + str(myJPY))

    # Convert data to DataFrame
    df = pd.DataFrame(data, columns=['open', 'high', 'low', 'close', 'volume', 'timestamp'])
    # Convert timestamp from milliseconds to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'].astype(float), unit='ms')
    # Convert prices and volume to float
    for col in ['open', 'high', 'low', 'close', 'volume']:
        df[col] = df[col].astype(float)

    # Sort by timestamp
    df = df.sort_values('timestamp')

    # Plot close price over time
    plt.figure(figsize=(12, 6))
    plt.plot(df['timestamp'], df['close'], label='Close Price')
    plt.title(f'{pair.upper()} Price Chart - Last 1 Month')
    plt.xlabel('Time')
    plt.ylabel('Price (JPY)')
    plt.grid(True)
    plt.legend()
    plt.show()

if __name__ == '__main__':
    main()