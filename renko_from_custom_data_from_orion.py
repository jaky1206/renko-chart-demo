import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.widgets import Slider, Button
import matplotlib.dates as mdates

# Load data from the file
df = pd.read_csv(r'renko_series_Test.txt')

# Strip any leading or trailing whitespace from the column names
df.columns = df.columns.str.strip()

# List of columns
# 'StartDateTime', 'EndDateTime', 'StartPrice', 'EndPrice', 'TotalUpVolume', 'TotalDownVolume', 'TotalVolume', 'Color'

# Ensure that the necessary columns exist
required_columns = ['StartDateTime', 'EndDateTime', 'StartPrice', 'EndPrice', 'Color', 'MovingAverage']
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

    # Define initial position for zooming in
    initial_position = len(df) - 100 if len(df) > 100 else 0

    # Create the figure and axis
    fig, axes = plt.subplots(figsize=(12, 8))
    plt.subplots_adjust(bottom=0.3)  # Adjusted to fit buttons and slider

    # Button for Renko
    axcolor = 'lightgoldenrodyellow'
    ax_renko = plt.axes([0.2, 0.05, 0.15, 0.05], facecolor=axcolor)
    btn_renko = Button(ax_renko, 'Renko')

    # Button for Candlestick
    ax_candlestick = plt.axes([0.4, 0.05, 0.15, 0.05], facecolor=axcolor)
    btn_candlestick = Button(ax_candlestick, 'Candlestick')

    # Initial plot type
    current_plot_type = 'Renko'

    def update_plot(plot_type):
        global current_plot_type
        axes.clear()  # Clear the axis before re-plotting

        if plot_type == 'Renko':
            # Plot the Renko bars
            index = 0
            for _, row in df.iterrows():
                if row['Color'] == 'G':  # Green for upward trend
                    if row['EndPrice'] - row['StartPrice'] <= 5:
                        renko = patches.Rectangle((index, row['StartPrice']), 1, row['EndPrice'] - row['StartPrice'], edgecolor='green', facecolor='green', alpha=0.7)
                        index += 1
                    elif row['EndPrice'] - row['StartPrice'] > 5:
                        renko = patches.Rectangle((index, row['StartPrice'] + 5), 1, 5, edgecolor='green', facecolor='green', alpha=0.7)
                        index += 1
                elif row['Color'] == 'R':  # Red for downward trend
                    if row['StartPrice'] - row['EndPrice'] <= 5:
                        renko = patches.Rectangle((index, row['StartPrice']), 1, row['EndPrice'] - row['StartPrice'], edgecolor='red', facecolor='red', alpha=0.7)
                        index += 1
                    elif row['StartPrice'] - row['EndPrice'] > 5:
                        renko = patches.Rectangle((index, row['EndPrice']), 1, 5, edgecolor='red', facecolor='red', alpha=0.7)
                        index += 1
                axes.add_patch(renko)

        elif plot_type == 'Candlestick':
            # Plot the Candlestick chart
            width = 0.6
            for i, row in df.iterrows():
                color = 'green' if row['EndPrice'] > row['StartPrice'] else 'red'
                lower = min(row['StartPrice'], row['EndPrice'])
                height = abs(row['EndPrice'] - row['StartPrice'])
                axes.add_patch(patches.Rectangle((i - width / 2, lower), width, height, facecolor=color, edgecolor='black'))
                axes.plot([i, i], [row['StartPrice'], row['EndPrice']], color='black', linewidth=1)
            axes.xaxis_date()
            axes.xaxis.set_major_locator(mdates.DayLocator())
            axes.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

        # Plot the moving average
        axes.plot(df.index, df['MovingAverage'], color='blue', label='Moving Average')

        # Set X-axis as timeline in dash style
        axes.set_xticks(df.index)
        axes.set_xticklabels(df['EndDateTime'].dt.strftime('%Y-%m-%d'), rotation=45, ha="right", fontsize=8)
        for label in axes.get_xticklabels():
            label.set_fontstyle('italic')

        # Adjust the axes limits based on the data
        axes.set_xlim(initial_position, initial_position + 30)
        axes.set_ylim([df[['StartPrice', 'EndPrice']].min().min(), df[['StartPrice', 'EndPrice']].max().max()])

        # Add grid, legend, and draw the plot
        axes.grid(True)
        axes.legend()
        plt.draw()

        # Update button states
        if plot_type == 'Renko':
            btn_renko.color = '#C0C0C0'  # Disabled color
            btn_renko.label.set_color('black')
            btn_candlestick.color = 'lightgoldenrodyellow'  # Enabled color
            btn_candlestick.label.set_color('black')
        elif plot_type == 'Candlestick':
            btn_candlestick.color = '#C0C0C0'  # Disabled color
            btn_candlestick.label.set_color('black')
            btn_renko.color = 'lightgoldenrodyellow'  # Enabled color
            btn_renko.label.set_color('black')

        current_plot_type = plot_type

    # Initial plot
    update_plot(current_plot_type)

    # Slider functionality
    def update_slider(val):
        pos = spos.val
        axes.set_xlim([pos, pos + 30])
        fig.canvas.draw_idle()

    axpos = plt.axes([0.2, 0.1, 0.6, 0.03], facecolor='lightgoldenrodyellow')
    spos = Slider(axpos, 'Pos', 0, max(0, len(df) - 30), valinit=initial_position, valstep=1)
    spos.on_changed(update_slider)

    # Button callbacks
    btn_renko.on_clicked(lambda event: update_plot('Renko'))
    btn_candlestick.on_clicked(lambda event: update_plot('Candlestick'))

    plt.show()
