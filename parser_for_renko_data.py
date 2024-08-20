import pandas as pd
import numpy as np
from statsmodels.regression.linear_model import OLS
from statsmodels.tools import add_constant

# Load the data
file_path = r'.\data\nq-aug-for-renko-m.csv'
data = pd.read_csv(file_path)

# Calculate moving average and median for the 'Volume_Total' column over a specified window
window_size = 5  # Adjust as necessary
data['Moving Average'] = data['Renko_Close'].rolling(window=window_size).mean().fillna(0).round(0).astype(int)
data['Median'] = data['Renko_Close'].rolling(window=window_size).median().fillna(0).round(0).astype(int)

# Prepare data for Linear Regression (predicting 'Volume_Total' using 'Renko_Close' and 'Renko_Open') , with the stock data (Volume_Total, Renko_Open, Renko_Close), linear regression helps to understand how changes in the Renko values might predict the volume of trades
data['Intercept'] = 1  # Adding an intercept for OLS regression
X = data[['Intercept', 'Renko_Open', 'Renko_Close']]
y = data['Volume_Total']

# Perform linear regression
model = OLS(y, X, missing='drop')  # 'drop' option ignores rows with NaN values
results = model.fit()

# Store the predicted values in the DataFrame
data['Linear Regression'] = results.predict(X).fillna(0).round(0).astype(int)

# Remove the intercept column after regression to clean up the DataFrame
data.drop(columns=['Intercept'], inplace=True)

# Save the updated DataFrame back to csv (or Excel)
output_file_path = r'.\data\nq-aug-for-renko-parsed-m.csv'
data.to_csv(output_file_path, index=False)  # Save as CSV
# data.to_excel(output_file_path.replace('.csv', '.xlsx'), index=False)  # Save as Excel if preferred

print("Updated file has been saved to:", output_file_path)
