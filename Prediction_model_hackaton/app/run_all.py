import sys
import os
from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
import pandas as pd

# Import your model pipeline

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from model.pred_model import main as run_prediction_pipeline  # 🟢 This will run everything

app = FastAPI()

# Run prediction + chart generation when API starts
@app.on_event("startup")
def startup_event():
    run_prediction_pipeline()

# Load forecasts and metrics
forecast_path = "predicted_aug_forecast.xlsx"
test_results_path = "test_vs_prediction.xlsx"
report_path = "output.html"

@app.get("/")
def root():
    return {"message": "Solar PV Forecasting API is live!"}

@app.get("/metrics")
def get_metrics():
    try:
        df = pd.read_excel(test_results_path)
        mae = round((df["Real Prod(mwh)"] - df["Forecast (mwh)"]).abs().mean(), 3)
        rmse = round(((df["Real Prod(mwh)"] - df["Forecast (mwh)"]) ** 2).mean() ** 0.5, 3)
        return {
            "Mean Absolute Error (MAE)": mae,
            "Root Mean Squared Error (RMSE)": rmse,
            "Data Points": len(df)
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/forecast")
def get_forecast():
    if os.path.exists(forecast_path):
        df = pd.read_excel(forecast_path)
        return df.to_dict(orient="records")
    return {"error": "Forecast file not found"}

@app.get("/report")
def get_report():
    if os.path.exists(report_path):
        return HTMLResponse(content=open(report_path, encoding="utf-8").read(), status_code=200)
    return {"error": "Report not found"}

@app.get("/charts/{filename}")
def get_chart(filename: str):
    file_path = f"charts/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "Chart not found"}
