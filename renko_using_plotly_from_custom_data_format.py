import os
import re
import pandas as pd
# NEW: Lib added >> Start
import plotly.graph_objects as go
# NEW: Lib added >> End
dataframes = []
file_paths = []
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
    global current_index
    current_index = index
    df = dataframes[index]
    file_name = os.path.basename(file_paths[index])
    
    # Create a figure
    fig = go.Figure()

    # Generate colors for each bar
    colors = ["green" if close >= open_ else "red" for close, open_ in zip(df["Renko_Close"], df["Renko_Open"])]

    # Add rectangles for Renko_Close and Renko_Open
    fig.add_trace(go.Bar(
        x=df["Time_Start"],
        y=df["Renko_Close"] - df["Renko_Open"],
        base=df["Renko_Open"],
        name="Renko Close/Open",
        marker=dict(
            color=colors,
            line=dict(color='black', width=1)
        ),
        width=1,
    ))

    # Define buttons for navigation
    buttons = [
        {
            "label": "Previous",
            "method": "update",
            "args": [
                {
                    "x": [dataframes[(current_index - 1) % len(file_paths)]["Time_Start"]],
                    "y": [dataframes[(current_index - 1) % len(file_paths)]["Renko_Close"] - dataframes[(current_index - 1) % len(file_paths)]["Renko_Open"]],
                    "base": [dataframes[(current_index - 1) % len(file_paths)]["Renko_Open"]]
                },
                {
                    "title": f"File: {os.path.basename(file_paths[(current_index - 1) % len(file_paths)])}"
                }
            ]
        },
        {
            "label": "Next",
            "method": "update",
            "args": [
                {
                    "x": [dataframes[(current_index + 1) % len(file_paths)]["Time_Start"]],
                    "y": [dataframes[(current_index + 1) % len(file_paths)]["Renko_Close"] - dataframes[(current_index + 1) % len(file_paths)]["Renko_Open"]],
                    "base": [dataframes[(current_index + 1) % len(file_paths)]["Renko_Open"]]
                },
                {
                    "title": f"File: {os.path.basename(file_paths[(current_index + 1) % len(file_paths)])}"
                }
            ]
        }
    ]

    fig.update_layout(
        title=f"File: {file_name}",
        xaxis_title="Time Start",
        yaxis_title="Values",
        xaxis_tickangle=-45,
        updatemenus=[
            {
                "type": "buttons",
                "buttons": buttons,
                "direction": "down",
                "showactive": False,
                "x": -0.1,
                "y": 1,
                "xanchor": "left",
                "yanchor": "top",
            }
        ],
        annotations=[
            {
                "text": f"Renko Chart",
                "x": 0.5,
                "y": 1.1,
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {"size": 16},
                "align": "center"
            }
        ],
    )

    fig.show()
# NEW: Modified for Renko plotting >> End

######## END OF FUNCTIONS >>>>>>

change_working_directory()

# Get the file paths from the "DATA" subdirectory
file_paths = get_file_paths('./data/custom-format/renko')

# Load all the data
dataframes = load_data(file_paths)

print("loading graph")

# Plot the first dataset initially
plot_data(current_index)
