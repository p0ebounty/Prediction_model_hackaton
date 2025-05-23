import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from reports.generate_html_report import generate_html_report, generate_interpretation
from reports.generate_charts import generate_time_series_charts

import pandas as pd
import numpy as np
import statsmodels.api as sm
from sklearn import metrics
import seaborn as sns
from lightgbm import LGBMRegressor
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt


os.environ["LOKY_MAX_CPU_COUNT"] = "4"  # or your preferred core count

def main():
    import pandas as pd
    # Load the two Excel file
    meteo_path = "data/meteo_data.xlsx"
    pv_path = "data/PV_charac.xlsx"

    # Load Excel files
    meteo_xls = pd.ExcelFile(meteo_path)
    pv_xls = pd.ExcelFile(pv_path)

    # Parse first few rows of each sheet
    meteo_data = {sheet: meteo_xls.parse(sheet).head(3) for sheet in meteo_xls.sheet_names}
    pv_data = {sheet: pv_xls.parse(sheet).head(3) for sheet in pv_xls.sheet_names}

    # Load full sheets
    meteo_df = meteo_xls.parse('0 hourly')
    pv_df = pv_xls.parse('Sheet1')

    # Sort meteo_df by Timestamp
    meteo_df = meteo_df.sort_values('Timestamp').reset_index(drop=True)

    # Ensure Timestamp in pv_df is in datetime format
    pv_df['Timestamp'] = pd.to_datetime(pv_df['From Year'].astype(str) + ' ' + pv_df['From Time'].astype(str), errors='coerce')

    # Subset meteo data from Jan 1 to Aug 31
    meteo_subset = meteo_df[
       (meteo_df['Timestamp'] >= '2022-01-01') &
       (meteo_df['Timestamp'] <= '2023-08-31')
       ].copy()

    # Merge PV and meteo data
    combined_df = pd.merge(meteo_subset, pv_df[['Timestamp', 'Real Prod(mwh)']], on='Timestamp', how='left')

    # Fill missing 'Real Prod(mwh)' with 0
    combined_df['Real Prod(mwh)'] = combined_df['Real Prod(mwh)'].fillna(0)

    # Split the data
    train_df = combined_df[combined_df['Timestamp'] <= '2023-07-21 23:00:00'].copy()
    test_df = combined_df[
    (combined_df['Timestamp'] > '2023-07-21 23:00:00') &
    (combined_df['Timestamp'] <= '2023-07-31 23:00:00')
    ].copy()

    forecast_df = combined_df[combined_df['Timestamp'] >= '2023-08-01 00:00:00'].copy()

    # Define features for training
    exclude_cols = [
    'Timestamp', 'From Year', 'From Time', 'To Year', 'To Time',
    'UTC offset(HHmm)', 'Forecast (mwh)', 'PVSolarPlant(Name)',
    'InsCap(MW)', 'Tracker type', 'Orientation', 'Real Prod(mwh)'
    ]

    # Extract numeric columns from training and forecast/test datasets
    X_train = train_df.drop(columns=exclude_cols, errors='ignore').select_dtypes(include='number')
    y_train = train_df['Real Prod(mwh)']

    X_test = test_df[X_train.columns]
    y_test = test_df['Real Prod(mwh)']

    X_forecast = forecast_df[X_train.columns]

    # Fit model
    model = HistGradientBoostingRegressor(max_iter=100, learning_rate=0.1, random_state=42)
    model.fit(X_train, y_train)

    # Predict and apply abs()
    y_test_pred = np.abs(model.predict(X_test))
    y_forecast_pred = np.abs(model.predict(X_forecast))

    # Add predictions
    test_df['Forecast (mwh)'] = y_test_pred
    forecast_df['Forecast (mwh)'] = y_forecast_pred

    # Save or display forecast
    forecast_df[['Timestamp', 'Forecast (mwh)']].to_excel("predicted_aug_forecast.xlsx", index=False)
    test_df[['Timestamp', 'Real Prod(mwh)', 'Forecast (mwh)']].to_excel("test_vs_prediction.xlsx", index=False)

    print('Mean Absolute Error:', metrics.mean_absolute_error(y_test, y_test_pred))
    print('Mean Squared Error:', metrics.mean_squared_error(y_test, y_test_pred))
    print('Root Mean Squared Error:', np.sqrt(metrics.mean_squared_error(y_test, y_test_pred)))
    print('R_adjusted:', metrics.r2_score(y_test, y_test_pred))

    # Define acceptable error threshold, e.g. ±0.05 MWh
    threshold = 0.05
    correct = np.abs(y_test - y_test_pred) <= threshold
    accuracy_within_threshold = np.mean(correct)

    print('Accuracy within ±0.05 MWh:', accuracy_within_threshold)

    # After predictions
    mae = metrics.mean_absolute_error(y_test, y_test_pred)
    mse = metrics.mean_squared_error(y_test, y_test_pred)
    rmse = np.sqrt(mse)
    r2 = metrics.r2_score(y_test, y_test_pred)

    print("\n🔍 Model Performance Metrics:")
    print("Mean Absolute Error (MAE):", mae)
    print("Mean Squared Error (MSE):", mse)
    print("Root Mean Squared Error (RMSE):", rmse)
    print("R² Score:", r2)
    print("Accuracy within ±0.05 MWh:", accuracy_within_threshold)

    print(generate_interpretation(mae, mse, rmse, r2, accuracy_within_threshold))
   
    # Save HTML report with charts (requires you to have saved .pngs in /charts)
    generate_html_report(mae, mse, rmse, r2, accuracy_within_threshold)
    generate_time_series_charts(combined_df, test_df)

    pass
if __name__ == "__main__":
    main()
