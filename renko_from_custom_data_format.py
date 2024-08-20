import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.widgets import Slider

# Load data from the file
file_path = r'.\data\nq-for-renko-m.csv'
data = pd.read_csv(file_path)

# Drop any rows with NaT values in Time_Start
cleaned_data = data.dropna(subset=['Time_Start'])

# Convert Time_Start to datetime
cleaned_data['Time_Start'] = pd.to_datetime(cleaned_data['Time_Start'], format='%H:%M:%S')

# Set up the plot
fig, ax = plt.subplots(figsize=(14, 7))
plt.subplots_adjust(bottom=0.25)  # Adjust bottom for the slider

# Define the brick size
brick_size = 5  # 5 points per brick

# Continuous position tracker
position = 0
positions = []

# Plot the Renko bricks
for index, row in cleaned_data.iterrows():
    color = 'green' if row['Renko_Open'] < row['Renko_Close'] else 'red'
    
    if row['Volume_Total'] != 0 : 
        # Store position for labeling
        positions.append(position)
        
        # Create the brick
        rect = patches.Rectangle(
            (position, min(row['Renko_Open'], row['Renko_Close'])),  # Bottom-left corner
            1,  # Uniform width
            abs(row['Renko_Close'] - row['Renko_Open']),  # Height (price movement)
            linewidth=1,
            edgecolor='black',
            facecolor=color
        )
        ax.add_patch(rect)
        
        # Increment position for the next brick
        position += 1
    else:
        positions.append(position-1)
        
        # Create the brick
        rect = patches.Rectangle(
            (position-1, min(row['Renko_Open'], row['Renko_Close'])),  # Bottom-left corner
            1,  # Uniform width
            abs(row['Renko_Close'] - row['Renko_Open']),  # Height (price movement)
            linewidth=1,
            edgecolor='black',
            facecolor=color
        )
        ax.add_patch(rect)

# Set the limits for the axes
ax.set_xlim(0, position)
ax.set_ylim(cleaned_data[['Renko_Open', 'Renko_Close']].min().min() - brick_size, 
            cleaned_data[['Renko_Open', 'Renko_Close']].max().max() + brick_size)

# Set labels and title
ax.set_xlabel('Index')
ax.set_ylabel('Price')
ax.set_title('Renko Chart')

# Adjust x-axis to show time labels
ax.set_xticks(positions)
ax.set_xticklabels(cleaned_data['Time_Start'].dt.strftime('%H:%M:%S'), rotation=45, ha='right')

# Add a slider for scrolling through the chart
ax_slider = plt.axes([0.1, 0.1, 0.8, 0.03], facecolor='lightgoldenrodyellow')
slider = Slider(ax_slider, 'Scroll', 0, max(positions) - 10, valinit=0, valstep=1)

# Update function to control the visible range of the Renko chart
def update(val):
    pos = int(slider.val)
    ax.set_xlim(pos, pos + 10)
    fig.canvas.draw_idle()

slider.on_changed(update)

# Show grid
ax.grid(True)

# Show the plot
plt.show()
