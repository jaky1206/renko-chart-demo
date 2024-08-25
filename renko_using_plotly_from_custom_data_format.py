import os
import re

import pandas as pd
import plotly.express as px

dataframes = []
file_paths = []
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
                "Indicator_1",
            ],
        )
        dataframes.append(df)
    return dataframes


'''
The current button definitions in the plot_data function use the "method": "update" parameter incorrectly.
The "update" method modifies only certain aspects of the plot, but in this case, we need to change the entire dataset being visualized.
To achieve this, we should use the "method": "relayout" and also add a callback function to handle the dynamic update correctly.
'''
def plot_data(index):
    df = dataframes[index]
    fig = px.scatter(
        df,
        x="Time_Start",
        y=["Renko_Open", "Renko_Close", "Indicator_1"],
        labels={"value": "Values", "variable": "Legend"},
        title=f"File: {os.path.basename(file_paths[index])}",
        color_discrete_map={
            "Renko_Open": "lightgray",
            "Renko_Close": "red",
            "Indicator_1": "blue",
        },
    )

    # Define buttons for navigation
    buttons = [
        {
            "label": "Previous",
            "method": "update",
            "args": [
                {
                    "x": [dataframes[(index - 1) % len(dataframes)]["Time_Start"]] * 3,
                    "y": [
                        dataframes[(index - 1) % len(dataframes)]["Renko_Open"],
                        dataframes[(index - 1) % len(dataframes)]["Renko_Close"],
                        dataframes[(index - 1) % len(dataframes)]["Indicator_1"]
                    ]
                },
                {
                    "title": f"File: {os.path.basename(file_paths[(index - 1) % len(dataframes)])}"
                }
            ]
        },
        {
            "label": "Next",
            "method": "update",
            "args": [
                {
                    "x": [dataframes[(index + 1) % len(dataframes)]["Time_Start"]] * 3,
                    "y": [
                        dataframes[(index + 1) % len(dataframes)]["Renko_Open"],
                        dataframes[(index + 1) % len(dataframes)]["Renko_Close"],
                        dataframes[(index + 1) % len(dataframes)]["Indicator_1"]
                    ]
                },
                {
                    "title": f"File: {os.path.basename(file_paths[(index + 1) % len(dataframes)])}"
                }
            ]
        },
    ]

    fig.update_layout(
        updatemenus=[
            {
                "type": "buttons",
                "direction": "left",
                "buttons": buttons,
                "showactive": False,
                "x": 0.1,
                "y": 1.15,
                "xanchor": "left",
                "yanchor": "top",
            }
        ],
        xaxis_title="Time Start",
        yaxis_title="Values",
        legend_title="",
        xaxis_tickangle=-45,
    )

    fig.show()


######## END OF FUNCTIONS >>>>>>

change_working_directory()

# Get the file paths from the "DATA" subdirectory
file_paths = get_file_paths(r".\data\custom-format\renko")

# Load all the data
dataframes = load_data(file_paths)

print("loading graph")

# Plot the first dataset initially
plot_data(current_index)
