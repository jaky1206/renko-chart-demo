import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.style as mplstyle

from matplotlib.ticker import FuncFormatter
from matplotlib.widgets import Slider, Button

# Constants
DATE_FORMAT = '%m/%d/%Y %H:%M:%S'
MPSTYLE = 'fast'

# Use Matplotlib Fast Style
mplstyle.use(MPSTYLE)

def format_volume(x, pos):
    if x >= 100000:
        return f'{x*0.001:.0f}k'
    return f'{x:.0f}'

def load_and_clean_data(file_path):
    data = pd.read_csv(file_path)
    cleaned_data = data.dropna(subset=['Time_Start'])
    cleaned_data['Time_Start'] = pd.to_datetime(cleaned_data['Time_Start'], format=DATE_FORMAT)
    return cleaned_data

def create_plot():
    fig, ax1 = plt.subplots(figsize=(14, 7))
    plt.subplots_adjust(left=0.052, bottom=0.164, right=0.94, top=0.929, wspace=0.2, hspace=0.2)
    ax2 = ax1.twinx()
    ax2.yaxis.set_major_formatter(FuncFormatter(format_volume))
    return fig, ax1, ax2

def plot_renko_and_volume(cleaned_data, ax1, ax2, show_volume):
    position = 0
    positions = []
    volume_bars = []
    brick_sizes = []

    # Calculate the smallest brick size
    smallest_brick_size = cleaned_data.apply(
        lambda row: abs(row['Renko_Close'] - row['Renko_Open']), axis=1
    ).min()

    for index, row in cleaned_data.iterrows():
        color = 'green' if row['Renko_Open'] < row['Renko_Close'] else 'red'
        brick_size = abs(row['Renko_Close'] - row['Renko_Open'])
        brick_sizes.append(brick_size)
        positions.append(position)

        # Draw the main Renko bar
        rect = patches.Rectangle(
            (position, min(row['Renko_Open'], row['Renko_Close'])),
            1,
            brick_size,
            linewidth=1,
            edgecolor='black',
            facecolor=color
        )
        ax1.add_patch(rect)
        
        # Draw internal black lines for larger bars
        if brick_size % smallest_brick_size == 0 and brick_size > smallest_brick_size:
            num_lines = brick_size // smallest_brick_size
            for i in range(1, num_lines):
                ax1.plot([position, position + 1], [min(row['Renko_Open'], row['Renko_Close']) + i * smallest_brick_size] * 2,
                         color='black', linewidth=0.5)  # Draw internal black lines

        if row['Volume_Total'] != 0:
            bar = ax2.bar(position, row['Volume_Total'], color=color, edgecolor='black', alpha=0.5, width=1, align='edge')
            volume_bars.append(bar)
            if not show_volume:
                for rect in bar:
                    rect.set_visible(False)

        position += 1

    return position, positions, volume_bars, brick_sizes

def plot_indicators(data, ax1, ax2):
    ax1.plot(data.index, data['Moving Average'], label='Moving Average', color='blue', linewidth=1)
    ax1.plot(data.index, data['Median'], label='Median', color='orange', linewidth=1)
    # ax2.plot(data.index, data['Linear Regression'], label='Linear Regression on Volume', color='purple', linewidth=1)

def set_axes_limits(ax1, ax2, cleaned_data, position):
    ax1.set_xlim(0, position)
    ax1.set_ylim(cleaned_data[['Renko_Open', 'Renko_Close']].min().min() - 5, 
                 cleaned_data[['Renko_Open', 'Renko_Close']].max().max() + 5)
    ax2.set_ylim(0, cleaned_data['Volume_Total'].max() * 1.5)

def set_labels_and_titles(ax1, ax2):
    ax1.set_xlabel('', fontsize=10)
    ax1.set_ylabel('', fontsize=10)
    ax2.set_ylabel('', fontsize=10)
    # move ylabel to right side
    ax2.yaxis.set_label_position('right')
    ax1.set_title('Renko Chart', fontsize=12)
    ax1.legend(loc='upper left', fontsize=8)
    ax2.legend(loc='upper right', fontsize=8)
    ax1.tick_params(axis='both', which='major', labelsize=8)
    ax2.tick_params(axis='both', which='major', labelsize=8)
    ax1.grid(False)

def set_time_labels(ax1, positions, time_labels):
    ax1.set_xticks(positions)
    ax1.set_xticklabels(time_labels, rotation=45, ha='right', fontsize=6)

def add_slider(ax1, fig, positions):
    ax_slider = plt.axes([0.1, 0.02, 0.8, 0.03], facecolor='lightgoldenrodyellow')
    slider = Slider(ax_slider, 'Scroll', 0, max(positions) - 10, valinit=0, valstep=1)

    def update(val):
        pos = int(slider.val)
        ax1.set_xlim(pos, pos + 10)
        fig.canvas.draw_idle()

    slider.on_changed(update)
    return slider

def update_plot(cleaned_data, ax1, ax2, slider, fig, show_volume):
    ax1.clear()
    ax2.clear()
    plt.subplots_adjust(left=0.048, bottom=0.164, right=0.99, top=0.930, wspace=0.2, hspace=0.2)

    position, positions, volume_bars, brick_sizes = plot_renko_and_volume(cleaned_data, ax1, ax2, show_volume)
    plot_indicators(cleaned_data, ax1, ax2)
    set_axes_limits(ax1, ax2, cleaned_data, position)
    set_labels_and_titles(ax1, ax2)
    set_time_labels(ax1, positions, cleaned_data['Time_Start'].dt.strftime(DATE_FORMAT))
    
    if slider:
        slider.valmax = max(positions) - 10  # Update the slider's max value
        slider.ax.set_xlim(slider.valmin, slider.valmax)
        slider.set_val(positions[0] if positions else 0)

    # Set tick visibility based on show_volume
    ax2.get_yaxis().set_visible(show_volume)
    ax2.tick_params(axis='y', labelsize=8 if show_volume else 0)  # Hide ticks when not visible
    
    return positions, volume_bars



def add_button(ax2, fig, show_volume):
    ax_button = plt.axes([0.8, 0.95, 0.1, 0.05])
    button = Button(ax_button, 'Show Volume', color='lightgoldenrodyellow')

    def toggle_volume(event):
        nonlocal show_volume
        show_volume = not show_volume

        for bar in ax2.containers:
            for rect in bar:
                rect.set_visible(show_volume)

        # Control visibility of the y-axis label, ticks, and legend
        ax2.get_yaxis().set_visible(show_volume)
        ax2.set_ylabel('Volume', fontsize=10 if show_volume else 0)  # Hide label text when not visible
        ax2.tick_params(axis='y', which='both', labelsize=8 if show_volume else 0)  # Hide ticks when not visible
        
        if show_volume:
            ax2.legend(loc='upper right', fontsize=8)  # Show legend
        else:
            ax2.legend_.remove()  # Hide legend

        button.label.set_text('Show Volume' if not show_volume else 'Hide Volume')
        plt.subplots_adjust(right=0.95 if show_volume else 0.99)
        fig.canvas.draw_idle()



    button.on_clicked(toggle_volume)
    return button

def add_buttons(ax1, ax2, data1, data2, slider, fig, show_volume):
    ax_button_forward = plt.axes([0.2, 0.95, 0.1, 0.05])
    button_forward = Button(ax_button_forward, 'Forward', color='lightgoldenrodyellow')
    ax_button_backward = plt.axes([0.1, 0.95, 0.1, 0.05])
    button_backward = Button(ax_button_backward, 'Backward', color='lightgoldenrodyellow')

    current_data = {'index': 0}

    def update_plot_for_data(data):
        nonlocal show_volume
        positions, volume_bars = update_plot(data, ax1, ax2, slider, fig, show_volume)
        if positions:
            slider.set_val(positions[0])  # Reset slider to the beginning

    def toggle_data_forward(event):
        current_data['index'] = (current_data['index'] + 1) % 2
        datasets = [data1, data2]
        update_plot_for_data(datasets[current_data['index']])

    def toggle_data_backward(event):
        current_data['index'] = (current_data['index'] - 1) % 2
        datasets = [data1, data2]
        update_plot_for_data(datasets[current_data['index']])

    button_forward.on_clicked(toggle_data_forward)
    button_backward.on_clicked(toggle_data_backward)
    return button_backward, button_forward


def main():
    file_path1 = r'data\nq-aug-04-to-aug-09-2024-for-renko-parsed-l.txt'
    file_path2 = r'data\nq-aug-11-to-aug-16-2024-for-renko-parsed-l.txt'

    data1 = load_and_clean_data(file_path1)
    data2 = load_and_clean_data(file_path2)
    
    cleaned_data = load_and_clean_data(file_path1)
    fig, ax1, ax2 = create_plot()

    show_volume = False
    positions, volume_bars = update_plot(cleaned_data, ax1, ax2, None, fig, show_volume)
    slider = add_slider(ax1, fig, positions)
    toggle_button = add_button(ax2, fig, show_volume)  # Pass show_volume to the button
    backward_button, forward_button = add_buttons(ax1, ax2, data1, data2, slider, fig, show_volume)
    plt.show()

if __name__ == "__main__":
    main()
