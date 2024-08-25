import os
import re
import pandas as pd
import matplotlib.pyplot as plt

from matplotlib.widgets import Button
from matplotlib.patches import Rectangle

dataframes = []
current_index = 0

def change_working_directory():
    script_directory = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_directory)

def get_file_paths(directory):
    # Get all CSV files in the specified directory
    all_files = [
        os.path.join(directory, file)
        for file in os.listdir(directory)
        if file.endswith(".csv")
    ]

    # Custom sorting logic
    def sort_key(filename):
        # Check if "2023" is in the filename
        is_2023 = "2023" in filename

        # Extract the digit following "M"
        match = re.search(r"M(\d+)", filename)
        month_digit = (
            int(match.group(1)) if match else float("inf")
        )  # Use infinity as a fallback for unmatched cases

        # Return tuple for sorting: (-is_2023 ensures 2023 files come first), then by month digit
        return (-is_2023, month_digit)

    # Sort the files based on the custom key
    sorted_files = sorted(all_files, key=sort_key)
    return sorted_files

def load_data(file_paths):
    for path in file_paths:
        df = pd.read_csv(
            path,
            usecols=[
                "Time_Start",
                "Renko_Open",
                "Renko_Close",
                "Volume",
            ],
        )
        dataframes.append(df)
    return dataframes

def plot_data(index):
    df = dataframes[index]

    ax.clear()  # Clear the previous plot

    x_position = 0  # Initialize x-axis position
    brick_size = 10  # Define the brick size
    current_y_position = df["Renko_Open"].iloc[0]  # Start at the first Renko open price
    x_positions = []  # To track x positions for labeling
    time_labels = []  # To track time labels for the x-axis
    prev_row_renko_color = None
    for i in range(len(df)):
        open_price = df["Renko_Open"].iloc[i]
        close_price = df["Renko_Close"].iloc[i]
        difference = close_price - open_price

        # Store the x_position and corresponding time label
        if i == 0 or df["Time_Start"].iloc[i] != df["Time_Start"].iloc[i - 1]:
            x_positions.append(x_position)
            time_labels.append(df["Time_Start"].iloc[i])

        # Determine the color of the brick
        color = 'green' if close_price >= open_price else 'red'

        # Handle larger movements by drawing multiple stacked bricks
        if(i >0 and color != prev_row_renko_color):
            if color == 'green':
                current_y_position += brick_size
            elif color == 'red':
                current_y_position -= brick_size
        while abs(difference) >= brick_size:
            y_start = current_y_position
            y_end = y_start + (brick_size if difference > 0 else -brick_size)
            rect = Rectangle(
                (x_position - 0.4, min(y_start, y_end)),
                1,  # Width of the rectangle
                brick_size,  # Height of the rectangle
                color=color,
                alpha=0.7,
                edgecolor='black'
            )
            ax.add_patch(rect)
            current_y_position = y_end  # Update the y-position for the next brick
            difference = close_price - current_y_position

        # Draw the remaining part of the brick, if any
        if abs(difference) > 0:
            y_start = current_y_position
            y_end = close_price
            rect = Rectangle(
                (x_position - 0.4, min(y_start, y_end)),
                1,  # Width of the rectangle
                abs(y_end - y_start),  # Height of the rectangle
                color=color,
                alpha=0.7,
                edgecolor='black'
            )
            ax.add_patch(rect)
            current_y_position = y_end  # Update the y-position for the next brick
        prev_row_renko_color = color
        x_position += 1  # Move to the next x position for the next time interval

    # Set x-axis and y-axis labels
    ax.set_xticks(x_positions)
    ax.set_xticklabels(time_labels, rotation=45, ha='right')
    ax.set_xlabel("Time Start")
    ax.set_ylabel("Values")
    ax.set_title(f"File: {os.path.basename(file_paths[index])}")

    # Adjust layout and display the plot
    ax.set_xlim(-0.5, x_position - 0.5)  # Ensure all rectangles fit within the plot area
    ax.set_ylim(df[["Renko_Open", "Renko_Close"]].min().min() - brick_size,
                df[["Renko_Open", "Renko_Close"]].max().max() + brick_size)  # Ensure all values fit within the plot area

    plt.tight_layout()
    fig.canvas.draw_idle()

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
file_paths = get_file_paths(r"data\custom-format\renko")

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

bnext = Button(axnext, "Next")
bprev = Button(axprev, "Previous")
bnext.on_clicked(next_plot)
bprev.on_clicked(prev_plot)

# Show the plot with interactive buttons
plt.show()
