import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from matplotlib.widgets import Slider, Button
import matplotlib.dates as mdates

# Load data from the file
df = pd.read_csv('renko_series.txt')

# Strip any leading or trailing whitespace from the column names
df.columns = df.columns.str.strip()

# list of columns 'StartDateTime', 'EndDateTime', 'StartPrice', 'EndPrice', 'TotalUpVolume', 'TotalDownVolume', 'TotalVolume', 'Color'

# Ensure that the necessary columns exist
required_columns = ['StartDateTime', 'EndDateTime', 'StartPrice', 'EndPrice', 'Color']
missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    print(f"Error: Missing columns: {missing_columns}")
else:
    # Convert the price columns to numeric
    df['StartPrice'] = pd.to_numeric(df['StartPrice'], errors='coerce')
    df['EndPrice'] = pd.to_numeric(df['EndPrice'], errors='coerce')

    # Convert the date columns to datetime
    df['StartDateTime'] = pd.to_datetime(df['StartDateTime'])
    df['EndDateTime'] = pd.to_datetime(df['EndDateTime'])

    # Increase the window size for moving average and median
    window_size = 10  # Reduced window size for better continuity
    df['MA'] = df['EndPrice'].rolling(window=window_size).mean().ffill().bfill()
    df['Median'] = df['EndPrice'].rolling(window=window_size).median().ffill().bfill()

    # Calculate the linear regression line for the EndPrice
    x = np.arange(len(df))
    y = df['EndPrice'].values
    slope, intercept = np.polyfit(x, y, 1)
    df['LinearRegression'] = slope * x + intercept

    # Define the plot type (choose between 'Renko' and 'Candlestick')
    plot_type = 'Renko'  # Change this to 'Renko' or 'Candlestick'

    # Create the figure and axis
    fig, axes = plt.subplots(figsize=(12, 8))

    if plot_type == 'Renko':
        # Plot the Renko bars
        index = 0
        for _, row in df.iterrows():
            if row['Color'] == 'G':  # Green for upward trend
                if row['EndPrice'] - row['StartPrice'] <= 5:
                    renko = patches.Rectangle((index, row['StartPrice']), 1, row['EndPrice'] - row['StartPrice'], edgecolor='green', facecolor='green', alpha=0.7)
                    index += 1  # Increment index after placing the Renko bar
                elif row['EndPrice'] - row['StartPrice'] > 5:
                    renko = patches.Rectangle((index, row['StartPrice']+ 5), 1, 5, edgecolor='green', facecolor='green', alpha=0.7)
                    index += 1  # Increment index after placing the Renko bar
            elif row['Color'] == 'R':  # Red for downward trend
                if row['StartPrice'] - row['EndPrice'] <= 5:
                    renko = patches.Rectangle((index, row['StartPrice']), 1, row['EndPrice'] - row['StartPrice'], edgecolor='red', facecolor='red', alpha=0.7)
                    index += 1  # Increment index after placing the Renko bar
                elif row['StartPrice'] - row['EndPrice'] > 5:
                    renko = patches.Rectangle((index, row['EndPrice']), 1, 5, edgecolor='red', facecolor='red', alpha=0.7)
                    index += 1  # Increment index after placing the Renko bar
            axes.add_patch(renko)

    elif plot_type == 'Candlestick':
        # Define the width of the candlestick
        width = 0.6
        for i, row in df.iterrows():
            color = 'green' if row['EndPrice'] > row['StartPrice'] else 'red'
            lower = min(row['StartPrice'], row['EndPrice'])
            height = abs(row['EndPrice'] - row['StartPrice'])
            # Draw the candlestick body
            axes.add_patch(patches.Rectangle((i - width / 2, lower), width, height, color=color, edgecolor='black'))
            # Draw the wick (line from high to low)
            axes.plot([i, i], [row['StartPrice'], row['EndPrice']], color='black', linewidth=1)

        # Format the x-axis to show dates properly
        axes.xaxis_date()
        axes.xaxis.set_major_locator(mdates.MonthLocator())  # Adjust to MonthLocator or DayLocator
        axes.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))  # Format date labels

    # Plot the moving average, median, and linear regression lines
    axes.plot(df.index, df['MA'], color='blue', label=f'{window_size}-period MA')
    axes.plot(df.index, df['Median'], color='orange', label=f'{window_size}-period Median')
    axes.plot(df.index, df['LinearRegression'], color='purple', label='Linear Regression')

    # Adjust the axes limits based on the data
    axes.set_xlim([0, len(df) + 5])
    axes.set_ylim([df[['StartPrice', 'EndPrice']].min().min(), df[['StartPrice', 'EndPrice']].max().max()])

    # Add grid, legend, and show the plot
    axes.grid(True)
    axes.legend()

    # Increase the bottom margin to fit the slider and button
    plt.subplots_adjust(bottom=0.2)

    # Slider functionality as a separate function
    def update_plot(val):
        pos = spos.val
        axes.set_xlim([pos, pos + 30])  # Set the zoom level to 30 data points
        fig.canvas.draw_idle()

    # Slider
    axcolor = 'lightgoldenrodyellow'
    axpos = plt.axes([0.2, 0.12, 0.6, 0.03], facecolor=axcolor)  # Adjusted position
    spos = Slider(axpos, 'Pos', 0, max(0, len(df) - 30), valinit=0, valstep=1)
    spos.on_changed(update_plot)

    # Reset button
    axcolor = '#f0f0f0'
    resetax = plt.axes([0.8, 0.05, 0.1, 0.03], facecolor=axcolor)  # Adjusted position and size
    button = Button(resetax, 'Reset Slider')

    # Customize button appearance
    button.color = '#4CAF50'  # Button color
    button.hovercolor = '#45a049'  # Hover color
    button.label.set_fontsize(10)  # Smaller font size
    button.label.set_color('white')  # Font color
    button.label.set_weight('bold')  # Font weight
    resetax.set_xticks([])  # Remove x-ticks
    resetax.set_yticks([])  # Remove y-ticks

    def reset(event):
        spos.reset()  # Reset the slider position
        axes.set_xlim([0, len(df) + 5])  # Reset x-axis limits to the original range
        fig.canvas.draw_idle()

    button.on_clicked(reset)

    plt.show()
