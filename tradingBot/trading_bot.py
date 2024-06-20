import alpaca_trade_api as tradeapi
import pandas as pd
import numpy as np

API_KEY = 'PKBRZJC662HUSC5NMVU7'
API_SECRET = 'X3zVB91NdMYTiL0cIrdXbeAnLNcJpCNRB0iO5IDD'
BASE_URL = 'https://paper-api.alpaca.markets'  # Use 'https://api.alpaca.markets' for live trading

# Initialize Alpaca API
api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')

# Parameters
symbol = 'AAPL'  
short_window = 40  
long_window = 100  
quantity = 1  

def get_historical_data(symbol, start, end):
    # Fetch historical data from Alpaca
    bars = api.get_bars(
        symbol,
        tradeapi.TimeFrame.Day,
        start=start,
        end=end
    ).df
    bars.index = pd.to_datetime(bars.index)
    return bars

def calculate_moving_averages(df, short_window, long_window):
    df['short_mavg'] = df['close'].rolling(window=short_window, min_periods=1).mean()
    df['long_mavg'] = df['close'].rolling(window=long_window, min_periods=1).mean()
    return df

def trading_signal(df):
    df['signal'] = 0
    df.loc[df.index[short_window:], 'signal'] = np.where(df.loc[df.index[short_window:], 'short_mavg'] > df.loc[df.index[short_window:], 'long_mavg'], 1, 0)
    df['position'] = df['signal'].diff()
    return df

def execute_trade(symbol, quantity):
    try:
        api.submit_order(
            symbol=symbol,
            qty=quantity,
            side='buy',
            type='market',
            time_in_force='gtc'
        )
        print(f"Buying {quantity} shares of {symbol}")
    except Exception as e:
        print(f"Error executing trade: {e}")

# Main function
if __name__ == "__main__":
    start_date = '2023-01-01'
    end_date = '2024-01-01'
    
    try:
        # Get historical data
        df = get_historical_data(symbol, start=start_date, end=end_date)
        print("Historical data fetched successfully.")
        print(df.head())  # Print the first few rows of the data for debugging
        
        # Calculate moving averages
        df = calculate_moving_averages(df, short_window, long_window)
        print("Moving averages calculated successfully.")
        print(df[['short_mavg', 'long_mavg']].tail())  # Print the moving averages
        
        # Determine trading signals
        df = trading_signal(df)
        print("Trading signals generated successfully.")
        print(df[['short_mavg', 'long_mavg', 'signal', 'position']].tail())  # Print signals and positions
        
        # Execute a test trade
        execute_trade(symbol, quantity)
    except Exception as e:
        print(f"Error in main function: {e}")
