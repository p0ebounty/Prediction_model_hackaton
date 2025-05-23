import os

def generate_interpretation(mae, mse, rmse, r2, acc_within_threshold):
    return f"""
    <h2>Model Performance Interpretation</h2>
    <pre>
    1. Mean Absolute Error (MAE): {mae:.3f} MWh
      → On average, the model misses the actual production by ~{mae*1000:.0f} kWh per hour.
      → {'Good' if mae < 0.1 else 'Needs improvement'} result based on typical hourly PV output.

    2. Mean Squared Error (MSE): {mse:.3f}

    3. Root Mean Squared Error (RMSE): {rmse:.3f} MWh
      → {'Small errors dominate' if rmse - mae < 0.05 else 'Larger errors are present, outliers exist.'}

    4. R² (Coefficient of Determination): {r2:.3f}
     → Model explains ~{r2*100:.1f}% of the variance in the actual PV production values.
     → {'Strong' if r2 >= 0.7 else 'Moderate' if r2 >= 0.5 else 'Weak'} model fit.

    5. Accuracy Within ±0.05 MWh: {acc_within_threshold:.1%}
   → {round(acc_within_threshold*100)}% of hourly predictions fall within ±50 kWh —
     {'very usable' if acc_within_threshold >= 0.7 else 'acceptable' if acc_within_threshold >= 0.5 else 'needs refinement'} in operational contexts.
    </pre>
    """

def generate_html_report(mae, mse, rmse, r2, acc_within_threshold):
        os.makedirs("charts", exist_ok=True)
        interpretation_html = generate_interpretation(mae, mse, rmse, r2, acc_within_threshold)
    
        charts = sorted(os.listdir("charts"))
        html_body = interpretation_html + "<h2>Charts</h2>\\n"
        for chart in charts:
            html_body += f'<div><img src="charts/{chart}" style="max-width: 100%; height: auto;"></div><br>\\n'

        with open("output.html", "w", encoding="utf-8") as f:
            f.write("<html><body>" + html_body + "</body></html>")

