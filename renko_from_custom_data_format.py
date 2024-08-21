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

# Load data from the file
file_path = r'.\data\nq-aug-for-renko-parsed-m.csv'
data = pd.read_csv(file_path)

# Drop any rows with NaT values in Time_Start
cleaned_data = data.dropna(subset=['Time_Start'])

# Convert Time_Start to datetime
cleaned_data['Time_Start'] = pd.to_datetime(cleaned_data['Time_Start'], format='%H:%M:%S')

# Set up the plot with two y-axes
fig, ax1 = plt.subplots(figsize=(14, 7))
plt.subplots_adjust(left=0.052, bottom=0.164, right=0.94, top=0.929, wspace=0.2, hspace=0.2)  # Adjust plot configuration to match the screenshot

ax2 = ax1.twinx()  # Create a second y-axis to plot volume and indicators

# Apply formatter to the volume axis
ax2.yaxis.set_major_formatter(FuncFormatter(format_volume))

# Define the brick size
brick_size = 5  # 5 points per brick

# Continuous position tracker
position = 0
positions = []
volume_bars = []  # List to hold volume bar containers for easy toggling

# Plot the Renko bricks and volume bars
for index, row in cleaned_data.iterrows():
    color = 'green' if row['Renko_Open'] < row['Renko_Close'] else 'red'
    positions.append(position)

    if row['Volume_Total'] != 0 : 
        # Create the Renko brick
        rect = patches.Rectangle(
            (position, min(row['Renko_Open'], row['Renko_Close'])),  # Bottom-left corner
            1,  # Uniform width
            abs(row['Renko_Close'] - row['Renko_Open']),  # Height (price movement)
            linewidth=1,
            edgecolor='black',
            facecolor=color
        )
        ax1.add_patch(rect)

        # Plot volume bars directly under each brick
        bar = ax2.bar(position, row['Volume_Total'], color=color, edgecolor='black', alpha=0.5, width=1, align='edge')  # Slightly less width for padding
        volume_bars.append(bar)  # Store the volume bar

        # Increment position for the next brick
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

        # Plot volume bars directly under each brick
        bar = ax2.bar(position-1, row['Volume_Total'], color=color, edgecolor='black', alpha=0.5, width=1, align='edge')  # Slightly less width for padding
        volume_bars.append(bar)  # Store the volume bar

# Plot additional indicators
ax1.plot(data.index, data['Moving Average'], label='Moving Average', color='blue', linewidth=1)
ax1.plot(data.index, data['Median'], label='Median', color='orange', linewidth=1)
ax2.plot(data.index, data['Linear Regression'], label='Linear Regression on Volume', color='purple', linewidth=1)

# Set the limits for the axes
ax1.set_xlim(0, position)
ax1.set_ylim(cleaned_data[['Renko_Open', 'Renko_Close']].min().min() - brick_size, 
             cleaned_data[['Renko_Open', 'Renko_Close']].max().max() + brick_size)
ax2.set_ylim(0, cleaned_data['Volume_Total'].max() * 1.5)  # Adjust volume axis limit


# Set labels and titles
ax1.set_xlabel('Index')
ax1.set_ylabel('Price')
ax2.set_ylabel('Volume')
ax1.set_title('Renko Chart')
ax2.set_ylabel('Volume')
ax1.legend(loc='upper left')
ax2.legend(loc='upper right')
ax1.grid(False)

# Adjust x-axis to show time labels
ax1.set_xticks(positions)
ax1.set_xticklabels(cleaned_data['Time_Start'].dt.strftime('%H:%M:%S'), rotation=45, ha='right')

# Add a slider for scrolling through the chart
ax_slider = plt.axes([0.1, 0.02, 0.8, 0.03], facecolor='lightgoldenrodyellow')
slider = Slider(ax_slider, 'Scroll', 0, max(positions) - 10, valinit=0, valstep=1)

# Update function to control the visible range of the Renko chart
def update(val):
    pos = int(slider.val)
    ax1.set_xlim(pos, pos + 10)
    fig.canvas.draw_idle()

slider.on_changed(update)

# Show grid
# ax1.grid(True)

# Add a button for showing/hiding the volume bars
ax_button = plt.axes([0.8, 0.95, 0.1, 0.05])  # Move button a bit upward
button = Button(ax_button, 'Show Volume', color='lightgoldenrodyellow')

# Button click event handler
volume_visible = False  # Track the visibility of the volume bars, start with hidden
def toggle_volume(event):
    global volume_visible
    volume_visible = not volume_visible
    
    # Toggle visibility of the volume bars
    for bar in volume_bars:
        for rect in bar:
            rect.set_visible(volume_visible)
    
    # Toggle visibility of the right-side y-axis labels
    ax2.get_yaxis().set_visible(volume_visible)
    
    # Update button label
    button.label.set_text('Show Volume' if not volume_visible else 'Hide Volume')
    fig.canvas.draw_idle()

# Hide the volume bars and the right-side labels initially
for bar in volume_bars:
    for rect in bar:
        rect.set_visible(volume_visible)
ax2.get_yaxis().set_visible(volume_visible)

button.on_clicked(toggle_volume)

# Update function to control the visible range of the Renko chart
def update(val):
    pos = int(slider.val)
    ax1.set_xlim(pos, pos + 10)
    fig.canvas.draw_idle()

slider.on_changed(update)

# Show the plot
plt.show()
