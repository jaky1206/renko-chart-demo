import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.widgets import Button, Slider
import matplotlib.patches as patches
import numpy as np
import matplotlib.collections as collections

# Function to load and prepare data
def load_data(file_path):
    try:
        df = pd.read_csv(file_path)
        df.columns = df.columns.str.strip()
        df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], format='%m/%d/%Y %H:%M:%S')
        df.set_index('DateTime', inplace=True)
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing columns: {missing_columns}")
        df.sort_index(inplace=True)
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        exit(1)

# Function to plot candlestick chart with optimizations
def plot_candlestick(df, ax):
    width = pd.Timedelta(seconds=4)
    width_seconds = width.total_seconds()
    
    # Convert datetime index to float days since epoch for plotting
    timestamps = mdates.date2num(df.index.to_pydatetime())
    opens = df['Open'].values
    highs = df['High'].values
    lows = df['Low'].values
    closes = df['Close'].values
    colors = np.where(closes >= opens, 'green', 'red')

    # Create collections for high-low lines and open-close rectangles
    lines = []
    rectangles = []

    for i in range(len(timestamps)):
        # High-low lines
        lines.append((timestamps[i], lows[i], highs[i], colors[i]))

        # Open-close rectangles
        rect = patches.Rectangle(
            (timestamps[i] - width_seconds / (2 * 86400), min(opens[i], closes[i])),  # Convert width to days
            width_seconds / 86400,  # Convert width to days
            abs(closes[i] - opens[i]),
            edgecolor=colors[i],
            facecolor=colors[i]
        )
        rectangles.append(rect)

    # Plot high-low lines
    for timestamp, low, high, color in lines:
        ax.plot([timestamp, timestamp], [low, high], color=color, linewidth=1.5)

    # Add rectangles to the plot
    patch_collection = collections.PatchCollection(rectangles, match_original=True)
    ax.add_collection(patch_collection)

    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.xticks(rotation=45, ha='right', fontsize=8)
    ax.grid(True, linestyle='--', linewidth=0.5)
    ax.set_xlabel('DateTime')
    ax.set_ylabel('Price')
    ax.set_title('Candlestick Chart')

# Function to toggle volume bars
def toggle_volume(event, volume_bars, toggle_button):
    visible = volume_bars[0].get_visible()
    for bar in volume_bars:
        bar.set_visible(not visible)
    toggle_button.label.set_text("Hide Volume" if visible else "Show Volume")
    plt.draw()

# Function to update the x-axis range based on slider value
def update(val, ax, df, initial_range):
    slider_index = int(val)
    current_date = df.index[slider_index]
    ax.set_xlim(mdates.date2num(current_date - initial_range), mdates.date2num(current_date + initial_range))
    plt.draw()

# Main plotting function
def create_plot(file_path):
    df = load_data(file_path)

    fig, ax = plt.subplots(figsize=(14, 8))
    plt.subplots_adjust(bottom=0.35)

    plot_candlestick(df, ax)

    ax2 = ax.twinx()
    width_days = pd.Timedelta(seconds=4).total_seconds() / (60 * 60 * 24)
    volume_bars = ax2.bar(mdates.date2num(df.index), df['Volume'], color='gray', alpha=0.3, width=width_days, visible=False)
    ax2.set_ylabel('Volume')

    button_ax = plt.axes([0.85, 0.01, 0.1, 0.05])
    toggle_button = Button(button_ax, 'Show Volume')
    toggle_button.on_clicked(lambda event: toggle_volume(event, volume_bars, toggle_button))

    slider_ax = plt.axes([0.15, 0.10, 0.7, 0.03], facecolor='lightgoldenrodyellow')
    date_slider = Slider(slider_ax, 'Date Index', 0, len(df) - 1, valinit=0, valstep=1)
    initial_range = pd.Timedelta(minutes=10)
    date_slider.on_changed(lambda val: update(val, ax, df, initial_range))
    
    plt.gcf().set_constrained_layout_pads(w_pad=2.0, h_pad=2.0)
    plt.show()

# Execute the main function
create_plot(r'.\data\nq-aug-15-to-aug-16-2024-for-candlestick-b.txt')
