import os
import re
import pandas as pd
import plotly.express as px

# NEW: Modified for Renko plotting >> Start
import dash

from dash import Dash, dcc, html, Input, Output, State
# NEW: Modified for Renko plotting >> End

# Initialize Dash app
app = Dash(__name__)
# NEW: Modified for Renko plotting >> End

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
    # NEW: Modified for Renko plotting >> Start
    dataframes = []
    # NEW: Modified for Renko plotting >> End
    for path in file_paths:
        df = pd.read_csv(path, usecols=['Time_Start', 'Renko_Open', 'Renko_Close', 'Volume', 'Indicator_1'])
        dataframes.append(df)
    return dataframes

# NEW: Modified for Renko plotting >> Start
def plot_data(index):
    df = dataframes[index]
    file_name = os.path.basename(file_paths[index])

    fig = px.scatter(
        df,
        x="Time_Start",
        y=["Renko_Open", "Renko_Close", "Indicator_1"],
        labels={"value": "Values", "variable": "Legend"},
        color_discrete_map={
            "Renko_Open": "lightgray",
            "Renko_Close": "red",
            "Indicator_1": "blue",
        },
    )

    fig.update_layout(
        xaxis_title="Time Start",
        yaxis_title="Values",
        legend_title="",
        xaxis_tickangle=-45,
        autosize=True,
        title={
            'text': f"Scatter Plot",
            'x': 0.5,  # Center the title horizontally
            'xanchor': 'center',
            'y': 0.95,  # Adjust the vertical position as needed
            'yanchor': 'top'
        }
    )

    return fig

# NEW: Modified for Renko plotting >> End

######## END OF FUNCTIONS >>>>>>

change_working_directory()

# Get the file paths from the "DATA" subdirectory
file_paths = get_file_paths('./data/custom-format/renko')

# Load all the data
dataframes = load_data(file_paths)

# NEW: Modified for Renko plotting >> Start

# Define Dash layout with CSS for centering and resizing
app.layout = html.Div([
    html.Div([
        dcc.Graph(
            id='renko-plot',
            style={'width': '100%', 'height': '100%'}
        ),
        html.Div(id='file-info', style={'textAlign': 'center', 'marginTop': '10px'})
    ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'width': '100%', 'height': '90vh'}),
    
    html.Div([
        html.Button('Previous', id='prev-button', n_clicks=0),
        html.Button('Next', id='next-button', n_clicks=0)
    ], style={'display': 'flex', 'justifyContent': 'center', 'marginTop': '20px'})
], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'height': '100vh'})

# Define callback to update the graph based on button clicks
@app.callback(
    Output('renko-plot', 'figure'),
    Output('file-info', 'children'),
    Input('prev-button', 'n_clicks'),
    Input('next-button', 'n_clicks'),
    State('file-info', 'children')
)
def update_plot(prev_clicks, next_clicks, file_info):
    global current_index
    
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = 'None'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'prev-button':
        current_index = (current_index - 1) % len(file_paths)
    elif button_id == 'next-button':
        current_index = (current_index + 1) % len(file_paths)

    fig = plot_data(current_index)
    file_name = os.path.basename(file_paths[current_index])
    return fig, f"Current file: {file_name}"

if __name__ == '__main__':
    app.run_server(debug=True)

# NEW: Modified for Renko plotting >> End