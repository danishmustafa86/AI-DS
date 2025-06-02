import pandas as pd
import matplotlib.pyplot as plt

# Load dataset
url = "https://query1.finance.yahoo.com/v7/finance/download/AAPL?period1=1609459200&period2=1640995200&interval=1d&events=history&includeAdjustedClose=true"
df = pd.read_csv(url)

# Convert 'Date' column to datetime
df['Date'] = pd.to_datetime(df['Date'])

# Set Date as index
df.set_index('Date', inplace=True)

# Plot closing price over time
plt.figure(figsize=(10,5))
plt.plot(df.index, df['Close'], label="Closing Price", color='blue')
plt.title("Apple Stock Prices")
plt.xlabel("Date")
plt.ylabel("Price (USD)")
plt.legend()
plt.grid()
plt.show()

# Calculate moving average (50-day and 200-day)
df['50-day MA'] = df['Close'].rolling(window=50).mean()
df['200-day MA'] = df['Close'].rolling(window=200).mean()

# Plot Moving Averages
plt.figure(figsize=(10,5))
plt.plot(df.index, df['Close'], label="Closing Price", color='blue', alpha=0.5)
plt.plot(df.index, df['50-day MA'], label="50-Day Moving Average", color='red')
plt.plot(df.index, df['200-day MA'], label="200-Day Moving Average", color='green')
plt.title("Apple Stock Price with Moving Averages")
plt.xlabel("Date")
plt.ylabel("Price (USD)")
plt.legend()
plt.grid()
plt.show()