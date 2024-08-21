import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.widgets import Slider
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# constants
DATE_FORMAT = '%m/%d/%Y %H:%M:%S'

def load_and_clean_data(file_path):
    data = pd.read_csv(file_path)
    cleaned_data = data.dropna(subset=['Time_Start'])
    cleaned_data['Time_Start'] = pd.to_datetime(cleaned_data['Time_Start'], format=DATE_FORMAT)
    return cleaned_data

def create_plot(cleaned_data):
    fig, ax1 = plt.subplots(figsize=(14, 7))
    plt.subplots_adjust(left=0.052, bottom=0.164, right=0.94, top=0.929, wspace=0.2, hspace=0.2)

    ax2 = ax1.twinx()  # Create a second y-axis to plot volume and indicators

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
    # Set label sizes
    ax1.set_xlabel('Index', fontsize=10)
    ax1.set_ylabel('Price', fontsize=10)
    ax2.set_ylabel('Volume', fontsize=10)
    ax1.set_title('Renko Chart', fontsize=12)
    ax2.set_ylabel('Volume', fontsize=10)
    
    # Set legend sizes
    ax1.legend(loc='upper left', fontsize=8)
    ax2.legend(loc='upper right', fontsize=8)
    
    # Set tick label sizes
    ax1.tick_params(axis='both', which='major', labelsize=8)
    ax2.tick_params(axis='both', which='major', labelsize=8)
    
    # Disable grid lines
    ax1.grid(False)

def set_time_labels(ax1, positions, time_labels):
    ax1.set_xticks(positions)
    ax1.set_xticklabels(time_labels, rotation=45, ha='right', fontsize=6)  # Adjust fontsize here

def add_slider(ax1, fig, positions):
    ax_slider = plt.axes([0.1, 0.02, 0.8, 0.03], facecolor='lightgoldenrodyellow')
    slider = Slider(ax_slider, 'Scroll', 0, max(positions) - 10, valinit=0, valstep=1)

    def update(val):
        pos = int(slider.val)
        ax1.set_xlim(pos, pos + 10)
        fig.canvas.draw_idle()

    slider.on_changed(update)
    return slider

def add_button(root, ax2, fig, volume_bars):
    volume_visible = False

    def toggle_volume():
        nonlocal volume_visible
        volume_visible = not volume_visible
        for bar in volume_bars:
            for rect in bar:
                rect.set_visible(volume_visible)
        ax2.get_yaxis().set_visible(volume_visible)
        button.config(text='Show Volume' if not volume_visible else 'Hide Volume')
        fig.canvas.draw_idle()

        # Disable the button for 3 seconds
        button.config(state=tk.DISABLED)
        root.after(3000, lambda: button.config(state=tk.NORMAL))

    # Create the button and keep it disabled initially
    button = tk.Button(root, text='Show Volume', command=toggle_volume, state=tk.DISABLED)
    button.pack(side=tk.TOP, pady=5)

    # Initially hide the volume bars
    for bar in volume_bars:
        for rect in bar:
            rect.set_visible(volume_visible)
    ax2.get_yaxis().set_visible(volume_visible)

    return button

def main():
    file_path = r'.\data\nq-aug-11-to-aug-16-2024-for-renko-parsed-m.csv'
    cleaned_data = load_and_clean_data(file_path)

    # Create a Tkinter window
    root = tk.Tk()
    root.title("Renko Chart with Volume Control")

    # Create the plot
    fig, ax1, ax2 = create_plot(cleaned_data)
    position, positions, volume_bars = plot_renko_and_volume(cleaned_data, ax1, ax2)
    plot_indicators(cleaned_data, ax1, ax2)
    set_axes_limits(ax1, ax2, cleaned_data, position)
    set_labels_and_titles(ax1, ax2)
    set_time_labels(ax1, positions, cleaned_data['Time_Start'].dt.strftime(DATE_FORMAT))

    # Embed the Matplotlib figure in the Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    # Add the Matplotlib toolbar for zoom, pan, etc.
    toolbar = NavigationToolbar2Tk(canvas, root)
    toolbar.update()
    toolbar.pack(side=tk.TOP, fill=tk.X)

    # Add the slider
    slider = add_slider(ax1, fig, positions)

    # Link the button with the volume bars after the plot is created
    button = add_button(root, ax2, fig, volume_bars)

    # Function to enable the button once the plot is drawn
    def enable_button(event):
        button.config(state=tk.NORMAL)

    # Connect the enable function to the canvas draw event
    fig.canvas.mpl_connect('draw_event', enable_button)

    # Start the Tkinter main loop
    root.mainloop()

if __name__ == "__main__":
    main()
