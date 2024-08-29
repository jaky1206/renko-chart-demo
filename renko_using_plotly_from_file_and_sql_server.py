import os
import re
import pandas as pd

# NEW: Modified for Renko plotting >> Start
import plotly.graph_objects as go
import dash
import pyodbc

from dash import Dash, dcc, html, Input, Output, State
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# make a static class
class DATASOURCE():
    FILE = 1
    SQL_SERVER = 2

# Constants
BRICK_SIZE = 10  # Define the brick size
SHOW_LEGENDS = False  # Set to True to show the legend
DATA_SROUCE = DATASOURCE.SQL_SERVER
COLUMN_LIST = ['Time_Start', 'Renko_Open', 'Renko_Close', 'Volume', 'Moving_Average', 'Median']

MSSQL_SERVER_ADDRESS = "localhost"
MSSQL_DATABASE = "TradingDB"
MSSQL_USER_NAME = "sa"
MSSQL_DATABASE_PASSWORD = "nopass"
MSSQL_ODBC_DRIVER = "ODBC Driver 18 for SQL Server"
MSSQL_USE_TRUST_SERVER_CERTIFICATE = "yes"
MSSQL_ENCRYPTION = "no"

# Initialize Dash app
app = Dash(__name__)
# NEW: Modified for Renko plotting >> End

file_paths = []
current_index = 0


# NEW: Modified for Renko plotting >> Start
def get_sql_server_connection_string():
    return (
            f"mssql+pyodbc://{MSSQL_USER_NAME}:{MSSQL_DATABASE_PASSWORD}@"
                f"{MSSQL_SERVER_ADDRESS}/{MSSQL_DATABASE}?"
                f"driver={MSSQL_ODBC_DRIVER}&"
                f"Trusted_Connection={MSSQL_USE_TRUST_SERVER_CERTIFICATE}&"
                f"Encrypt={MSSQL_ENCRYPTION}"
        )

def execute_query(query):
    """
    Connects to SQL Server using SQLAlchemy, executes the given query, and returns the results.

    Parameters:
    - query: SQL query string to be executed

    Returns:
    - results: List of tuples containing the query results
    """
    engine = None
    connection = None

    try:
        # Create an SQLAlchemy engine
        connection_string = get_sql_server_connection_string()  # Update this to your SQLAlchemy connection string
        engine = create_engine(connection_string)

        # Connect to SQL Server
        connection = engine.connect()

        # Execute the provided SQL query
        result_proxy = connection.execute(text(query))

        # Fetch data
        results = result_proxy.fetchall()

        return results

    except SQLAlchemyError as e:
        print(f"Error: {e}")
        return None

    finally:
        # Clean up and close the connection
        if connection:
            connection.close()
        if engine:
            engine.dispose()


def get_list_from_database():
    # Define the query
    query = """
    SELECT DISTINCT
        [WeekStartDate],
        [WeekEndDate],
        [WeekNo]
    FROM [TradingDB].[dbo].[NQ_Weekly_Data]
    """

    # Execute the query and fetch data
    results = execute_query(query)

    # Print results if data was fetched successfully
    if results is not None:
        # create an array of strings
        result = []
        for row in results:
            #print('Week No: ',row[2], ' From: ', row[0], ' To: ', row[1])
            result.append('Week No: ' + str(row[2]) + ' From: ' + str(row[0]) + ' To: ' + str(row[1]))

        return result
    else:
        # reutrn None
        return None
    
def extract_week_info(week_str):
    # Define a regular expression pattern to match the week information
    pattern = r"Week No: (\d+) From: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) To: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})"
    
    # Search for the pattern in the input string
    match = re.search(pattern, week_str)
    
    if match:
        week_no = int(match.group(1))
        start_str = match.group(2)
        end_str = match.group(3)
        
        # Parse the date strings into datetime objects
        start_date = datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(end_str, "%Y-%m-%d %H:%M:%S")
        
        return week_no, start_date, end_date
    else:
        # raise ValueError("The input string does not match the expected format")
        return None, None, None

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd

def get_dataframe_from_sql_server(file_path):
    """
    Fetches data from SQL Server using SQLAlchemy and returns it as a pandas DataFrame.

    Parameters:
    - file_path: Path to the CSV file to extract week information.

    Returns:
    - DataFrame: A pandas DataFrame containing the query results.
    """
    # Read week start and week end dates from the CSV file
    week_no, week_start_date, week_end_date = extract_week_info(file_path)
    
    # Define the query
    query = f"""
    SELECT
        [Time_Start],
        [Renko_Open],
        [Renko_Close],
        [Volume],
        [Indicator_1] AS [Moving_Average],
        [Indicator_2] AS [Median]
    FROM [TradingDB].[dbo].[NQ_Weekly_Data]
    WHERE [WeekStartDate] = '{week_start_date}'
      AND [WeekEndDate] = '{week_end_date}'
      AND [WeekNo] = {week_no}
    """

    try:
        # Create an SQLAlchemy engine
        connection_string = get_sql_server_connection_string()
        engine = create_engine(connection_string)
        
        # Fetch data into a DataFrame
        df = pd.read_sql(query, engine)
        
        return df

    except SQLAlchemyError as e:
        print(f"Error: {e}")
        return None

    finally:
        # Clean up and close the engine
        if engine:
            engine.dispose()

# NEW: Modified for Renko plotting >> End

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

# NEW: Modified for Renko plotting >> Start
def load_data(file_path):
    if DATA_SROUCE == DATASOURCE.SQL_SERVER:
        df = get_dataframe_from_sql_server(file_path)
    else:
        # Load a single DataFrame from the specified file path
        df = pd.read_csv(file_path, usecols=COLUMN_LIST)
    return df

def plot_data(index):
    file_path = file_paths[index]
    df = load_data(file_path)  # Load data on demand
    
    if DATA_SROUCE == DATASOURCE.SQL_SERVER:
        file_name = file_path
    else:
        file_name = os.path.basename(file_path)
    
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
        difference = pd.to_numeric(close_price) - pd.to_numeric(open_price)
        
        # Determine the color of the brick
        color = 'green' if close_price >= open_price else 'red'
        
        # Adjust current_y_position based on previous color if it changes
        if i > 0 and color != prev_row_renko_color:
            if color == 'green':
                current_y_position += brick_size
            elif color == 'red':
                current_y_position -= brick_size

        # Convert close_price to numeric type
        close_price_numeric = pd.to_numeric(close_price)

        while abs(difference) >= brick_size:
            y_start = float(current_y_position)
            brick_size = float(BRICK_SIZE)  # Define the brick size
            y_end = y_start + (brick_size if difference > 0 else -brick_size)

            colors.append(color)
            x_positions.append(df["Time_Start"].iloc[i])
            y_starts.append(min(y_start, y_end))
            y_ends.append(max(y_start, y_end))

            current_y_position = y_end  # Update the y-position for the next brick
            difference = close_price_numeric - current_y_position

            # Draw the remaining part of the brick, if any
            if abs(difference) > 0:
                y_start = current_y_position
                y_end = close_price_numeric

                colors.append(color)
                x_positions.append(df["Time_Start"].iloc[i])
                y_starts.append(min(y_start, y_end))
                y_ends.append(max(y_start, y_end))

                current_y_position = y_end  # Update the y-position for the next brick
                difference = 0
        
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
    ))

    # Plot Moving Average and Median
    fig.add_trace(go.Scatter(
        x=df["Time_Start"],
        y=df["Moving_Average"],
        mode='lines',  # Ensure it's lines-only
        line=dict(color='blue', width=2),
        name='Moving Average',
    ))

    fig.add_trace(go.Scatter(
        x=df["Time_Start"],
        y=df["Median"],
        mode='lines',  # Ensure it's lines-only
        line=dict(color='orange', width=2),
        name='Median',
    ))

    fig.update_layout(
    xaxis_title="Time Start",
    yaxis_title="",
    showlegend=SHOW_LEGENDS,  # Disable the legend
    legend=dict(
            orientation="h",  # Horizontal legend
            yanchor="top",
            y=1.2,
            xanchor="left",
            x=0,
        ),
    margin=dict(l=0, r=0, t=0, b=0),  # Remove margins
    xaxis_tickangle=-45,
    autosize=True,
    title={
        'text': f'Renko Chart of {file_name}',
        'x': 0.5,
        'xanchor': 'center',
        'y': 0.98,  # Adjust this value to move the title higher
        'yanchor': 'bottom',
        'font': {'size': 13}  # Adjust font size as needed
    },
    yaxis=dict(
            tickformat=',',  
            tickmode='auto'  
        )
)

    return fig

# NEW: Modified for Renko plotting >> End

######## END OF FUNCTIONS >>>>>>

change_working_directory()

# NEW: Modified for Renko plotting >> Start

# Get the file paths from the "DATA" subdirectory
if DATA_SROUCE == DATASOURCE.SQL_SERVER:
    file_paths = get_list_from_database()
else:
    file_paths = get_file_paths(r'./data/custom-format/renko-parsed')

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
