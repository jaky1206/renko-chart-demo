import os
import re
import pandas as pd

# NEW: Modified for Renko plotting >> Start
import plotly.graph_objects as go
import dash

from dash import Dash, dcc, html, Input, Output, State

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
        df = pd.read_csv(path, usecols=['Time_Start', 'Renko_Open', 'Renko_Close', 'Volume', 'Moving_Average', 'Median'])
        dataframes.append(df)
    return dataframes

# NEW: Modified for Renko plotting >> Start
def plot_data(index):
    df = dataframes[index]
    file_name = os.path.basename(file_paths[index])

    # Create a figure
    fig = go.Figure()

    # Generate colors for each bar
    colors = ["green" if close >= open_ else "red" for close, open_ in zip(df["Renko_Close"], df["Renko_Open"])]

    # Add Renko bars using Bar trace
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
        yaxis='y1'  # Primary y-axis for Renko bars
    ))

    # Add Median line (secondary y-axis)
    fig.add_trace(go.Scatter(
        x=df["Time_Start"],
        y=df["Median"],
        mode='lines',
        name='Median',
        line=dict(color='blue', width=2),
        yaxis='y2'  # Secondary y-axis
    ))

    # Add Moving Average line (secondary y-axis)
    fig.add_trace(go.Scatter(
        x=df["Time_Start"],
        y=df["Moving_Average"],
        mode='lines',
        name='Moving Average',
        line=dict(color='orange', width=2),
        yaxis='y2'  # Secondary y-axis
    ))

    # Update layout to ensure all traces are visible without affecting the Renko bars
    fig.update_layout(
        xaxis_title="Time Start",
        yaxis=dict(
            title="Renko Values",
            side='left'
        ),
        yaxis2=dict(
            title="",
            overlaying='y',  # Overlay y-axis 2 on y-axis 1
            side='right',
            showgrid=False,  # Hide gridlines for the secondary axis
            zeroline=False,
            showticklabels=False  # Hide tick labels for the secondary axis
        ),
        legend=dict(
            x=1,  # Adjust the position of the legend
            y=1,
            xanchor='left'
        ),
        xaxis_tickangle=-45,
        autosize=True,
        title={
            'text': "Renko Chart with Median and Moving Average",
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
file_paths = get_file_paths(r'./data/custom-format/renko-parsed')

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