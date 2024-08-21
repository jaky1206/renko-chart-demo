import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.ticker import FuncFormatter
from matplotlib.widgets import Slider, Button

def format_volume(x, pos):
    'The two args are the value and tick position'
    if x >= 100000:
        return f'{x*0.001:.0f}k'  # Convert to thousands for readability
    return f'{x:.0f}'

def load_and_clean_data(file_path):
    data = pd.read_csv(file_path)
    cleaned_data = data.dropna(subset=['Time_Start'])
    cleaned_data['Time_Start'] = pd.to_datetime(cleaned_data['Time_Start'], format='%H:%M:%S')
    return cleaned_data

def create_plot(cleaned_data):
    fig, ax1 = plt.subplots(figsize=(14, 7))
    plt.subplots_adjust(left=0.052, bottom=0.164, right=0.94, top=0.929, wspace=0.2, hspace=0.2)

    ax2 = ax1.twinx()  # Create a second y-axis to plot volume and indicators
    ax2.yaxis.set_major_formatter(FuncFormatter(format_volume))

    return fig, ax1, ax2

def plot_renko_and_volume(cleaned_data, ax1, ax2):
    position = 0
    positions = []
    volume_bars = []

    for index, row in cleaned_data.iterrows():
        color = 'green' if row['Renko_Open'] < row['Renko_Close'] else 'red'
        positions.append(position)

        if row['Volume_Total'] != 0:
            rect = patches.Rectangle(
                (position, min(row['Renko_Open'], row['Renko_Close'])),  # Bottom-left corner
                1,  # Uniform width
                abs(row['Renko_Close'] - row['Renko_Open']),  # Height (price movement)
                linewidth=1,
                edgecolor='black',
                facecolor=color
            )
            ax1.add_patch(rect)
            bar = ax2.bar(position, row['Volume_Total'], color=color, edgecolor='black', alpha=0.5, width=1, align='edge')
            volume_bars.append(bar)
            position += 1
        else:
            rect = patches.Rectangle(
                (position-1, min(row['Renko_Open'], row['Renko_Close'])),  # Bottom-left corner
                1,  # Uniform width
                abs(row['Renko_Close'] - row['Renko_Open']),  # Height (price movement)
                linewidth=1,
                edgecolor='black',
                facecolor=color
            )
            ax1.add_patch(rect)
            bar = ax2.bar(position-1, row['Volume_Total'], color=color, edgecolor='black', alpha=0.5, width=1, align='edge')
            volume_bars.append(bar)

    return position, positions, volume_bars

def plot_indicators(data, ax1, ax2):
    ax1.plot(data.index, data['Moving Average'], label='Moving Average', color='blue', linewidth=1)
    ax1.plot(data.index, data['Median'], label='Median', color='orange', linewidth=1)
    ax2.plot(data.index, data['Linear Regression'], label='Linear Regression on Volume', color='purple', linewidth=1)

def set_axes_limits(ax1, ax2, cleaned_data, position):
    ax1.set_xlim(0, position)
    ax1.set_ylim(cleaned_data[['Renko_Open', 'Renko_Close']].min().min() - 5, 
                 cleaned_data[['Renko_Open', 'Renko_Close']].max().max() + 5)
    ax2.set_ylim(0, cleaned_data['Volume_Total'].max() * 1.5)

def set_labels_and_titles(ax1, ax2):
    ax1.set_xlabel('Index')
    ax1.set_ylabel('Price')
    ax2.set_ylabel('Volume')
    ax1.set_title('Renko Chart')
    ax2.set_ylabel('Volume')
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')
    ax1.grid(False)

def set_time_labels(ax1, positions, time_labels):
    ax1.set_xticks(positions)
    ax1.set_xticklabels(time_labels, rotation=45, ha='right')

def add_slider(ax1, fig, positions):
    ax_slider = plt.axes([0.1, 0.02, 0.8, 0.03], facecolor='lightgoldenrodyellow')
    slider = Slider(ax_slider, 'Scroll', 0, max(positions) - 10, valinit=0, valstep=1)

    def update(val):
        pos = int(slider.val)
        ax1.set_xlim(pos, pos + 10)
        fig.canvas.draw_idle()

    slider.on_changed(update)
    return slider

def add_button(ax2, fig, volume_bars):
    ax_button = plt.axes([0.8, 0.95, 0.1, 0.05])  # Move button a bit upward
    button = Button(ax_button, 'Show Volume', color='lightgoldenrodyellow')

    volume_visible = False

    def toggle_volume(event):
        nonlocal volume_visible
        volume_visible = not volume_visible
        for bar in volume_bars:
            for rect in bar:
                rect.set_visible(volume_visible)
        ax2.get_yaxis().set_visible(volume_visible)
        button.label.set_text('Show Volume' if not volume_visible else 'Hide Volume')
        fig.canvas.draw_idle()

    for bar in volume_bars:
        for rect in bar:
            rect.set_visible(volume_visible)
    ax2.get_yaxis().set_visible(volume_visible)

    button.on_clicked(toggle_volume)
    return button

def main():
    file_path = r'.\data\nq-aug-for-renko-parsed-m.csv'
    cleaned_data = load_and_clean_data(file_path)
    fig, ax1, ax2 = create_plot(cleaned_data)
    position, positions, volume_bars = plot_renko_and_volume(cleaned_data, ax1, ax2)
    plot_indicators(cleaned_data, ax1, ax2)
    set_axes_limits(ax1, ax2, cleaned_data, position)
    set_labels_and_titles(ax1, ax2)
    set_time_labels(ax1, positions, cleaned_data['Time_Start'].dt.strftime('%H:%M:%S'))
    slider = add_slider(ax1, fig, positions)
    button = add_button(ax2, fig, volume_bars)
    plt.show()

if __name__ == "__main__":
    main()
