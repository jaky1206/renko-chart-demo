import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Load stock price data from a text file
df = pd.read_csv('candlestick_series.txt')

# Clean column names (strip leading/trailing whitespace)
df.columns = df.columns.str.strip()

# Create a datetime column by combining 'Date' and 'Time'
df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])

# Set datetime as the index
df.set_index('DateTime', inplace=True)

# Ensure required columns exist
required_columns = ['Open', 'High', 'Low', 'Close']
missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    print(f"Error: Missing columns: {missing_columns}")
    exit(1)

# Create a new figure
fig, ax = plt.subplots(figsize=(12, 8))

# Plot candlestick bars
for i, row in df.iterrows():
    color = 'green' if row['Close'] >= row['Open'] else 'red'
    ax.plot([i, i], [row['Low'], row['High']], color=color, linewidth=1.5)  # High-low line
    ax.plot([i, i], [row['Open'], row['Close']], color=color, linewidth=5)  # Open-close bar

# Set x-axis labels and formatting
ax.xaxis_date()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
plt.xticks(rotation=45, ha='right')

# Set y-axis limits
plt.ylim(df['Low'].min() - 5, df['High'].max() + 5)

# Add grid and labels
plt.grid(True, linestyle='--')
plt.xlabel('DateTime')
plt.ylabel('Price')
plt.title('Candlestick Chart')

plt.show()
