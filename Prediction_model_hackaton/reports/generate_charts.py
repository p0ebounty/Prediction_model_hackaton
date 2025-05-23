import os
import matplotlib.pyplot as plt
import seaborn as sns


def generate_time_series_charts(combined_df, test_df):
    os.makedirs("charts", exist_ok=True)

    # Ensure Timestamp is datetime and set as index
    combined_df['Timestamp'] = pd.to_datetime(combined_df['Timestamp'])
    combined_df.set_index('Timestamp', inplace=True)

    # Resample to daily averages
    daily_df = combined_df.resample('D').mean(numeric_only=True)

    # Create individual plots for each selected feature
    features_to_plot = {
        'Temperature °C [2 m elevation corrected]': 'Daily Avg Temperature [2 m]',
        'Relative Humidity [%]': 'Daily Avg Relative Humidity',
        'Precipitation Total [mm]': 'Daily Total Precipitation',
        'Soil Moisture [0-7 cm down][m³/m³]': 'Daily Avg Soil Moisture [0-7 cm]'
    }

    for i, (col, title) in enumerate(features_to_plot.items(), start=1):
        if col in daily_df.columns:
            fig = plt.figure(figsize=(14, 4))
            plt.plot(daily_df.index, daily_df[col], label=title)
            plt.title(title)
            plt.xlabel('Date')
            plt.ylabel('Value')
            plt.grid(True)
            plt.tight_layout()
            filename = f"charts/plot_{i}_{title.replace(' ', '_').replace('[','').replace(']','')}.png"
            fig.savefig(filename)
            plt.close(fig)

    # Filter PV production only for rows with actual values (non-zero, originally non-null)
    pv_production_df = combined_df[combined_df['Real Prod(mwh)'] > 0]
    daily_pv = pv_production_df['Real Prod(mwh)'].resample('D').sum()

    fig = plt.figure(figsize=(14, 4))
    plt.plot(daily_pv.index, daily_pv.values, label='Real PV Production', color='green')
    plt.title('Daily PV Production (Only Non-Zero Values)')
    plt.xlabel('Date')
    plt.ylabel('MWh')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    fig.savefig("charts/plot_PV_Production.png")
    plt.close(fig)

    # Reset index for plotting
    test_df = test_df.copy().reset_index()
    combined_df_reset = combined_df.reset_index()

    # Histogram/KDE: Real PV Production (non-zero only)
    fig = plt.figure(figsize=(10, 4))
    sns.histplot(test_df[test_df['Real Prod(mwh)'] > 0]['Real Prod(mwh)'], kde=True, color='green')
    plt.title('Distribution of Real PV Production (July 22–31)')
    plt.xlabel('Real Prod (mWh)')
    plt.ylabel('Frequency')
    plt.tight_layout()
    fig.savefig("charts/plot_PV_Distribution.png")
    plt.close(fig)

    # KDE: Forecasted vs Actual
    fig = plt.figure(figsize=(10, 4))
    sns.kdeplot(test_df['Real Prod(mwh)'], label='Actual', color='blue')
    sns.kdeplot(test_df['Forecast (mwh)'], label='Forecast', color='red')
    plt.title('KDE of Forecasted vs Actual Production (July 22–31)')
    plt.xlabel('mWh')
    plt.ylabel('Density')
    plt.legend()
    plt.tight_layout()
    fig.savefig("charts/plot_KDE_Forecast_vs_Actual.png")
    plt.close(fig)

    # Histogram/KDE: Temperature Distribution
    fig = plt.figure(figsize=(10, 4))
    sns.histplot(
        combined_df_reset['Temperature °C [2 m elevation corrected]'],
        kde=True, color='orange'
    )
    plt.title('Distribution of Daily Temperature (All Data)')
    plt.xlabel('Temperature (°C)')
    plt.ylabel('Frequency')
    plt.tight_layout()
    fig.savefig("charts/plot_Temperature_Distribution.png")
    plt.close(fig)




