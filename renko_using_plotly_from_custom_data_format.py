import os
import re
import pandas as pd

# NEW: Modified for Renko plotting >> Start
import plotly.graph_objects as go
import dash

from dash import Dash, dcc, html, Input, Output, State

# Constants
DATAFRAME_COLUMN_NAMES = ['Time_Start', 'Renko_Open', 'Renko_Close', 'Volume', 'Moving_Average', 'Median']
BRICK_SIZE = 10  # Define the brick size
SHOW_LEGENDS = False  # Set to True to show the legend

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
        # NEW: Modified for Renko plotting >> Start
        df = pd.read_csv(path, usecols=DATAFRAME_COLUMN_NAMES)
        # NEW: Modified for Renko plotting >> End
        dataframes.append(df)
    return dataframes

# NEW: Modified for Renko plotting >> Start
def plot_data(index):
    df = dataframes[index]
    file_name = os.path.basename(file_paths[index])
    
    fig = go.Figure()

    # Generate colors and positions for each bar
    colors = []
    x_positions = []
    y_starts = []
    y_ends = []
    brick_size = BRICK_SIZE  # Define the brick size
    current_y_position = df["Renko_Open"].iloc[0]  # Start at the first Renko open price
    prev_row_renko_color = None
    x_position = 0  # Initialize x-axis position
    
    # Loop through dataframe to create stacked rectangles
    for i in range(len(df)):
        open_price = df["Renko_Open"].iloc[i]
        close_price = df["Renko_Close"].iloc[i]
        difference = close_price - open_price
        
        # Determine the color of the brick
        color = 'green' if close_price >= open_price else 'red'
        
        # Adjust current_y_position based on previous color if it changes
        if i > 0 and color != prev_row_renko_color:
            if color == 'green':
                current_y_position += brick_size
            elif color == 'red':
                current_y_position -= brick_size
        
        while abs(difference) >= brick_size:
            y_start = current_y_position
            y_end = y_start + (brick_size if difference > 0 else -brick_size)
            
            colors.append(color)
            x_positions.append(df["Time_Start"].iloc[i])
            y_starts.append(min(y_start, y_end))
            y_ends.append(max(y_start, y_end))
            
            current_y_position = y_end  # Update the y-position for the next brick
            difference = close_price - current_y_position
        
        # Draw the remaining part of the brick, if any
        if abs(difference) > 0:
            y_start = current_y_position
            y_end = close_price
            
            colors.append(color)
            x_positions.append(df["Time_Start"].iloc[i])
            y_starts.append(min(y_start, y_end))
            y_ends.append(max(y_start, y_end))
            
            current_y_position = y_end  # Update the y-position for the next brick
        
        prev_row_renko_color = color
        x_position += 1  # Move to the next x position for the next time interval
    
    # Add bars for Renko bricks
    fig.add_trace(go.Bar(
        x=x_positions,
        y=[y_end - y_start for y_start, y_end in zip(y_starts, y_ends)],
        base=y_starts,
        marker=dict(
            color=colors,
            line=dict(color='black', width=1)
        ),
        width=1,
        name="Renko Bricks",
        showlegend=SHOW_LEGENDS
    ))

    # Plot Moving Average and Median
    fig.add_trace(go.Scatter(
        x=df["Time_Start"],
        y=df["Moving_Average"],
        mode='lines',
        line=dict(color='blue', width=2),
        name='Moving Average',
        showlegend=SHOW_LEGENDS
    ))

    fig.add_trace(go.Scatter(
        x=df["Time_Start"],
        y=df["Median"],
        mode='lines',
        line=dict(color='orange', width=2),
        name='Median',
        showlegend=SHOW_LEGENDS
    ))

    fig.update_layout(
        xaxis_title="Time Start",
        yaxis_title="Values",
        yaxis=dict(
            tickformat=',',  # Ensures thousands separator is displayed
        ),
        legend=dict(
            orientation="h",  # Horizontal legend
            yanchor="top",
            y=1.2,
            xanchor="left",
            x=0,
            # bgcolor='rgba(255, 255, 255, 0)',  # Optional: Transparent background for the legend
        ),
        xaxis_tickangle=-45,
        autosize=True,
        title={
            'text': f'Renko Chart of {file_name}',
            'x': 0.5,
            'xanchor': 'center',
            'y': 0.95,
            'yanchor': 'top',
            'font': {'size': 15}
        },
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
