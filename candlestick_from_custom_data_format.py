import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.widgets import Button
import matplotlib.patches as patches

# Load stock price data from a text file
df = pd.read_csv(r'.\data\candlestick_series_medium.txt')

# Clean column names (strip leading/trailing whitespace)
df.columns = df.columns.str.strip()

# Create a datetime column by combining 'Date' and 'Time'
df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], format='%m/%d/%Y %H:%M:%S')

# Set datetime as the index
df.set_index('DateTime', inplace=True)

# Ensure required columns exist
required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    print(f"Error: Missing columns: {missing_columns}")
    exit(1)

# Sort data by datetime
df.sort_index(inplace=True)

# Create a new figure
fig, ax = plt.subplots(figsize=(14, 8))

# Define the width of candlestick bars (adjust as needed)
width = pd.Timedelta(seconds=4)  # Width of candlestick bars
width_days = width / pd.Timedelta(days=1)  # Convert width to days for plotting

# Plot candlestick bars
for timestamp, row in df.iterrows():
    color = 'green' if row['Close'] >= row['Open'] else 'red'
    
    # Plot the high-low line
    ax.plot([timestamp, timestamp], [row['Low'], row['High']], color=color, linewidth=1.5)  
    
    # Plot the open-close rectangle
    open_close_rect = patches.Rectangle(
        (timestamp - pd.Timedelta(seconds=width.total_seconds() / 2), min(row['Open'], row['Close'])),
        width,
        abs(row['Close'] - row['Open']),
        edgecolor=color,
        facecolor=color
    )
    ax.add_patch(open_close_rect)

# Set x-axis labels and formatting
ax.xaxis_date()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
plt.xticks(rotation=45, ha='right')

# Adjust x-axis limits to show all data with some padding
ax.set_xlim(df.index.min() - pd.Timedelta(minutes=10), df.index.max() + pd.Timedelta(minutes=10))

# Set y-axis limits
ax.set_ylim(df['Low'].min() - 10, df['High'].max() + 10)

# Add grid and labels
ax.grid(True, linestyle='--', linewidth=0.5)  # Make grid lines lighter
ax.set_xlabel('DateTime')
ax.set_ylabel('Price')
ax.set_title('Candlestick Chart')

# Create a secondary y-axis to plot volume
ax2 = ax.twinx()
# Adjust volume bars width to match candlestick bars
volume_width = width.total_seconds() / (60 * 60 * 24)  # Convert width to days
volume_bars = ax2.bar(df.index, df['Volume'], color='gray', alpha=0.3, width=volume_width, visible=False)

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

# Resize the plot to fit the window and remove extra whitespace
plt.gcf().set_constrained_layout_pads(w_pad=2.0, h_pad=2.0)

plt.show()
