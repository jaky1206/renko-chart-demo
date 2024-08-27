import os
import re
import pandas as pd
import matplotlib.pyplot as plt

from matplotlib.widgets import Button

dataframes = []
current_index = 0

def change_working_directory():
    script_directory = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_directory)

def get_file_paths(directory):
    # Get all CSV files in the specified directory
    all_files = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith('.csv')]

    # Custom sorting logic
    def sort_key(filename):
        # Check if "2023" is in the filename
        is_2023 = "2023" in filename

        # Extract the digit following "M"
        match = re.search(r'M(\d+)', filename)
        month_digit = int(match.group(1)) if match else float('inf')  # Use infinity as a fallback for unmatched cases

        # Return tuple for sorting: (-is_2023 ensures 2023 files come first), then by month digit
        return (-is_2023, month_digit)

    # Sort the files based on the custom key
    sorted_files = sorted(all_files, key=sort_key)
    return sorted_files

def load_data(file_paths):
    for path in file_paths:
        df = pd.read_csv(path, usecols=['Time_Start', 'Renko_Open', 'Renko_Close', 'Volume', 'Indicator_1'])
        dataframes.append(df)
    return dataframes

# NEW: Modified for Renko plotting >> Start
def plot_data(index):
    df = dataframes[index]

    ax.clear()  # Clear the previous plot

    # Plot Renko_Close as crosses
    ax.scatter(df['Time_Start'], df['Renko_Open'], color='lightgrey', marker='o', label='Renko Open')

    # Plot Renko_Close as crosses
    ax.scatter(df['Time_Start'], df['Renko_Close'], color='red', marker='x', label='Renko Close')

    # Plot Indicator_1 as dots
    ax.scatter(df['Time_Start'], df['Indicator_1'], color='blue', marker='o', label='Indicator 1')

    # Adding labels, title, and legend
    ax.set_xlabel('Time Start')
    ax.set_ylabel('Values')

    ax.set_title(f'File: {os.path.basename(file_paths[index])}')

    ax.legend()

    # Rotate x-axis labels
    plt.setp(ax.get_xticklabels(), rotation=45)

    # Adjust layout and display the plot
    plt.tight_layout()

    fig.canvas.draw_idle()
# NEW: Modified for Renko plotting >> Start

def next_plot(event):
    global current_index
    current_index = (current_index + 1) % len(dataframes)  # Loop back to the start
    plot_data(current_index)

def prev_plot(event):
    global current_index
    current_index = (current_index - 1) % len(dataframes)  # Loop back to the end
    plot_data(current_index)

######## END OF FUNCTIONS >>>>>>

change_working_directory()

# Get the file paths from the "DATA" subdirectory
file_paths = get_file_paths('./data/custom-format/renko')

# Load all the data
dataframes = load_data(file_paths)

print("loading graph")

# Initialize the plot and index tracking
fig, ax = plt.subplots(figsize=(12, 6))

# Plot the first dataset initially
plot_data(current_index)

# Create Next and Previous buttons

axprev = plt.axes([0.7, 0.9, 0.05, 0.0375])  # Positioned at the top
axnext = plt.axes([0.81, 0.9, 0.05, 0.0375])  # Positioned at the top

bnext = Button(axnext, 'Next')
bprev = Button(axprev, 'Previous')
bnext.on_clicked(next_plot)
bprev.on_clicked(prev_plot)

# Show the plot with interactive buttons
plt.show()
