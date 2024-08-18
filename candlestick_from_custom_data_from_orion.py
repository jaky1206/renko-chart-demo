import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.widgets import Button

# Load stock price data from a text file
df = pd.read_csv(r'.\data\candlestick_series.txt')

# Clean column names (strip leading/trailing whitespace)
df.columns = df.columns.str.strip()

# Create a datetime column by combining 'Date' and 'Time'
df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])

# Set datetime as the index
df.set_index('DateTime', inplace=True)

# Ensure required columns exist
required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
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
ax.set_ylim(df['Low'].min() - 5, df['High'].max() + 5)

# Add grid and labels
ax.grid(True, linestyle='--')
ax.set_xlabel('DateTime')
ax.set_ylabel('Price')
ax.set_title('Candlestick Chart')

# Create a secondary y-axis to plot volume
ax2 = ax.twinx()
volume_bars = ax2.bar(df.index, df['Volume'], color='gray', alpha=0.3, width=0.001, visible=False)  # Initially hidden

# Set secondary y-axis label
ax2.set_ylabel('Volume')

# Function to toggle volume bars on or off
def toggle_volume(event):
    visible = volume_bars[0].get_visible()
    for bar in volume_bars:
        bar.set_visible(not visible)
    # Update button label
    if visible:
        toggle_button.label.set_text("Show Volume")
    else:
        toggle_button.label.set_text("Hide Volume")
    plt.draw()

# Create a button for toggling volume
button_ax = plt.axes([0.85, 0.01, 0.1, 0.05])  # Position of the button (x, y, width, height)
toggle_button = Button(button_ax, 'Show Volume')
toggle_button.on_clicked(toggle_volume)

# Resize the plot to fit the window
plt.tight_layout()

plt.show()
