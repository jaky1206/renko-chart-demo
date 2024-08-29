import os
import re
import pandas as pd
import plotly.express as px

import dash

from dash import Dash, dcc, html, Input, Output

DATA_DIRECTORY = r'./data/custom-format/renko-parsed'
SHOW_LEGENDS = False

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

    dataframes = []

    for path in file_paths:
        df = pd.read_csv(path, usecols=['Time_Start', 'Time_End', 'Renko_Open', 'Renko_Close', 'Volume', 'Moving_Average', 'Median'])
        dataframes.append(df)
    return dataframes

def plot_data(index):
    df = dataframes[index]
    file_name = os.path.basename(file_paths[index])
    
    fig = px.scatter(
        df,
        x="Time_Start",
        y=["Renko_Open", "Renko_Close", "Moving_Average", "Median"],
        labels={"value": "Values", "variable": "Legend"},
        title=f"File: {file_name}",
        color_discrete_map={
            "Renko_Open": "lightgray",
            "Renko_Close": "red",
            "Moving_Average": "blue",
            "Median": "orange"
        },
    )

    fig.update_layout(
        xaxis_title="Time Start",
        yaxis_title="",
        showlegend=SHOW_LEGENDS,  # Disable the legend
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(
            orientation="h",  # Horizontal legend
            yanchor="top",
            y=1.2,
            xanchor="left",
            x=0,
        ),
        xaxis_tickangle=-45,
        autosize=True,
        title={
            'text': f'Renko Chart of {file_name}',
            'x': 0.5,
            'xanchor': 'center',
            'y': 0.98,  # Adjust this value to move the title higher
            'yanchor': 'bottom',
            'font': {'size': 14}  # Adjust font size as needed
            },
        yaxis=dict(
        tickformat=',',
        tickmode='auto',
        range=[df['Renko_Open'].min() * 0.98, df['Renko_Close'].max() * 1.02]  # Dynamically set y-axis range
    )
    )

    return fig

######## END OF FUNCTIONS >>>>>>

change_working_directory()

# Get the file paths from the "DATA" subdirectory
file_paths = get_file_paths(DATA_DIRECTORY)

# Load all the data
dataframes = load_data(file_paths)

print("loading graph")

# Define Dash layout with CSS for centering and resizing
app.layout = html.Div([
    html.Div([
        html.Button('Previous', id='prev-button', n_clicks=0, style={'marginRight': '10px'}),
        html.Button('Next', id='next-button', n_clicks=0)
    ], style={'display': 'flex', 'justifyContent': 'center', 'marginTop': '20px'}),

    dcc.Graph(
        id='renko-plot',
        style={'width': '100%', 'height': '100vh'}  # Adjust height as needed to use the remaining screen space
    )
], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'height': '100vh'})

# Define callback to update the graph based on button clicks
@app.callback(
    Output('renko-plot', 'figure'),
    [Input('prev-button', 'n_clicks'), Input('next-button', 'n_clicks')]
)
def update_plot(prev_clicks, next_clicks):
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
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)

# NEW: Modified for Renko plotting >> End