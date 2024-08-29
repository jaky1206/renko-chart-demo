import numpy as np
import pandas as pd
import dash
from dash import Dash, dcc, html, Input, Output
from sqlalchemy import create_engine
import plotly.express as px

# Constants
BRICK_SIZE = 10  
SHOW_LEGENDS = False  
CURRENT_WEEK = 1  # Starting week number

MSSQL_AUTHENTICATION_TYPE = "SQL"  # Set to "SQL" or "WINDOWS"
MSSQL_SERVER_ADDRESS = "localhost"
MSSQL_DATABASE = "TradingDB"
MSSQL_USER_NAME = "sa"
MSSQL_DATABASE_PASSWORD = "nopass"
MSSQL_ODBC_DRIVER = "ODBC Driver 18 for SQL Server"
MSSQL_USE_TRUST_SERVER_CERTIFICATE = "yes"
MSSQL_ENCRYPTION = "no"

# Database URI Based on MSSQL_AUTHENTICATION_TYPE
if MSSQL_AUTHENTICATION_TYPE == "SQL":
    DATABASE_URI = (
        f"mssql+pyodbc://{MSSQL_USER_NAME}:{MSSQL_DATABASE_PASSWORD}@"
        f"{MSSQL_SERVER_ADDRESS}/{MSSQL_DATABASE}?"
        f"driver={MSSQL_ODBC_DRIVER}&"
        f"Trusted_Connection={MSSQL_USE_TRUST_SERVER_CERTIFICATE}&"
        f"Encrypt={MSSQL_ENCRYPTION}"
    )
else:
    DATABASE_URI = (
        f"mssql+pyodbc://"
        f"{MSSQL_SERVER_ADDRESS}/{MSSQL_DATABASE}?"
        f"driver={MSSQL_ODBC_DRIVER}&"
        f"Trusted_Connection={MSSQL_USE_TRUST_SERVER_CERTIFICATE}&"
        f"Encrypt={MSSQL_ENCRYPTION}"
    )

engine = create_engine(DATABASE_URI)

# Initialize Dash app
app = Dash(__name__)

def load_data_for_week(engine, week_no):
    query = f"""
    SELECT Time_Start, Time_End, Renko_Open, Renko_Close, Volume, 
           Indicator_1 AS Moving_Average, Indicator_2 AS Median,
           WeekStartDate, WeekEndDate
    FROM NQ_Weekly_Data
    WHERE WeekNo = {week_no}
    """
    df = pd.read_sql(query, engine)

    # Ensure numeric columns are correctly interpreted as numbers
    df["Renko_Open"] = pd.to_numeric(df["Renko_Open"], errors='coerce')
    df["Renko_Close"] = pd.to_numeric(df["Renko_Close"], errors='coerce')
    df["Volume"] = pd.to_numeric(df["Volume"], errors='coerce')
    df["Moving_Average"] = pd.to_numeric(df["Moving_Average"], errors='coerce')
    df["Median"] = pd.to_numeric(df["Median"], errors='coerce')

    # Handle missing values (optional)
    df = df.dropna()  # or df.fillna(0)

    return df

def plot_data_for_week(week_no):
    df = load_data_for_week(engine, week_no)
    week_start_date = df["WeekStartDate"].iloc[0]  # Get the first start date from the data
    week_end_date = df["WeekEndDate"].iloc[0]      # Get the first end date from the data

    # Replace 0 values in Renko_Open and Renko_Close with NaN
    df["Renko_Open"] = df["Renko_Open"].replace(0, np.nan)
    df["Renko_Close"] = df["Renko_Close"].replace(0, np.nan)

    # Replace 0 values in Moving Average and Median with NaN
    moving_average = df["Moving_Average"].replace(0, np.nan)
    median = df["Median"].replace(0, np.nan)

    # Create scatter plot
    fig = px.scatter(
        df,
        x="Time_Start",
        y=["Renko_Open", "Renko_Close", "Moving_Average", "Median"],
        labels={"value": "Values", "variable": "Legend"},
        color_discrete_map={
            "Renko_Open": "lightgray",
            "Renko_Close": "red",
            "Moving_Average": "blue",
            "Median": "orange",
        },
    )

    # Update layout for better visualization
    fig.update_layout(
        xaxis_title="Time Start",
        yaxis_title="",
        showlegend=SHOW_LEGENDS,  # it is been set to False for now
        legend=dict(
            orientation="h",  # Horizontal legend
            yanchor="top",
            y=1.2,
            xanchor="left",
            x=0,
        ),
        margin=dict(l=0, r=0, t=0, b=0),  # Remove or reduce margins
        xaxis_tickangle=-45,
        autosize=True,
        title={
            "text": f"Renko Chart for Week {week_no} ({week_start_date} to {week_end_date})",
            "x": 0.5,
            "xanchor": "center",
            "y": 0.98,  # Adjust this value to move the title higher
            "yanchor": "bottom",
            "font": {"size": 14},  # Adjust font size as needed
        },
        yaxis=dict(
            tickformat=",",
            tickmode="auto",
            range=[
                df["Renko_Open"].min() * 0.98,
                df["Renko_Close"].max() * 1.02,
            ],  # Dynamically set y-axis range
        ),
        xaxis=dict(
            rangemode="normal",  # This will ensure the axis fits the data points
            autorange=True,
        ),
    )

    return fig

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
    global CURRENT_WEEK
    ctx = dash.callback_context

    if not ctx.triggered:
        button_id = 'None'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'prev-button':
        CURRENT_WEEK = max(1, CURRENT_WEEK - 1)  # Ensure week number doesn't go below 1
    elif button_id == 'next-button':
        CURRENT_WEEK += 1  # Increment week number

    fig = plot_data_for_week(CURRENT_WEEK)
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
