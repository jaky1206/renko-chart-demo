import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from matplotlib.widgets import Slider

# Load data from the file
df = pd.read_csv(r'.\data\renko_series_with_moving_average.txt')

# Strip any leading or trailing whitespace from the column names
df.columns = df.columns.str.strip()

# Ensure that the necessary columns exist
required_columns = ['StartDateTime', 'EndDateTime', 'StartPrice', 'EndPrice', 'Color']
missing_columns = [col for col in required_columns if col not in df.columns]


# if missing_columns throw error and return
if missing_columns:
    print(f"Error: Missing columns: {missing_columns}")
    exit(1)


# Convert the price columns to numeric
df['StartPrice'] = pd.to_numeric(df['StartPrice'], errors='coerce')
df['EndPrice'] = pd.to_numeric(df['EndPrice'], errors='coerce')
df['MovingAverage'] = pd.to_numeric(df['MovingAverage'], errors='coerce')

# Create the Renko bars
def plot_renko_chart(df):
    fig, ax1 = plt.subplots(figsize=(12, 8))
    plt.subplots_adjust(bottom=0.3)

    index = 0
    for _, row in df.iterrows():
        if pd.notna(row['StartPrice']) and pd.notna(row['EndPrice']):
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
            ax1.add_patch(renko)

    ax1.plot(range(len(df)), df['MovingAverage'], color='blue', label='Moving Average')
    ax1.legend()

    ax1.set_xticks(range(len(df)))
    ax1.set_xticklabels(df['EndDateTime'], rotation=45, ha="right")
    for label in ax1.get_xticklabels():
        label.set_fontstyle('italic')

    initial_position = len(df) - 100 if len(df) > 100 else 0
    ax1.set_xlim(initial_position, initial_position + 50)
    ax1.set_ylim(df['StartPrice'].min() - 10, df['EndPrice'].max() + 10)

    ax1.set_ylabel('Price')
    ax1.set_title('Renko Chart')
    ax1.grid(True, linestyle='--')

    ax_slider = plt.axes([0.1, 0.05, 0.8, 0.03], facecolor='lightgoldenrodyellow')
    slider = Slider(ax_slider, 'Scroll', 0, len(df) - 50, valinit=initial_position, valstep=1)

    def update(val):
        pos = slider.val
        ax1.set_xlim([pos, pos + 50])
        fig.canvas.draw_idle()

    slider.on_changed(update)
    plt.show()

# Call the function to create the Renko chart
plot_renko_chart(df)
