import sys
import os
from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
import pandas as pd
import threading

# Import your model pipeline

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from model.pred_model import main as run_prediction_pipeline  # 🟢 This will run everything

app = FastAPI()

# --- Глобальная переменная для отслеживания состояния пайплайна ---
pipeline_finished_processing = False
pipeline_error = None

def run_pipeline_in_background():
    global pipeline_finished_processing, pipeline_error
    try:
        print("Background thread: Starting prediction pipeline...")
        run_prediction_pipeline()
        pipeline_finished_processing = True
        print("Background thread: Prediction pipeline finished successfully.")
    except Exception as e:
        pipeline_error = str(e)
        print(f"Background thread: Error during prediction pipeline: {e}")
# --------------------------------------------------------------------

# Run prediction + chart generation when API starts
@app.on_event("startup")
def startup_event():
    print("FastAPI startup event: Triggering prediction pipeline in background.")
    # Запускаем пайплайн в отдельном потоке
    thread = threading.Thread(target=run_pipeline_in_background)
    thread.start()
    # Этот обработчик завершится быстро, позволяя FastAPI запуститься
    print("FastAPI startup event: Background pipeline initiated. FastAPI will now start.")


# Load forecasts and metrics
forecast_path = "predicted_aug_forecast.xlsx"
test_results_path = "test_vs_prediction.xlsx"
report_path = "output.html"

@app.get("/")
def root():
    if pipeline_error:
        return {"message": "Solar PV Forecasting API is live, but an error occurred during data processing.", "error_details": pipeline_error}
    if not pipeline_finished_processing:
        return {"message": "Solar PV Forecasting API is live! Data is currently being processed. Please try again in a few moments."}
    return {"message": "Solar PV Forecasting API is live! Data processed."}

@app.get("/metrics")
def get_metrics():
    if pipeline_error:
        return JSONResponse(status_code=500, content={"error": "Data processing failed.", "details": pipeline_error})
    if not pipeline_finished_processing or not os.path.exists(test_results_path):
        return JSONResponse(status_code=202, content={"message": "Metrics are being generated. Please try again later."})
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
        return JSONResponse(status_code=500, content={"error": f"Could not read or process test results: {str(e)}"})

@app.get("/forecast")
def get_forecast():
    if pipeline_error:
        return JSONResponse(status_code=500, content={"error": "Data processing failed.", "details": pipeline_error})
    if not pipeline_finished_processing or not os.path.exists(forecast_path):
        return JSONResponse(status_code=202, content={"message": "Forecast is being generated. Please try again later."})
    
    try:
        df = pd.read_excel(forecast_path)
        return df.to_dict(orient="records")
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Could not read or process forecast file: {str(e)}"})

@app.get("/report")
def get_report():
    if pipeline_error:
        return HTMLResponse(content=f"<h1>Error during data processing</h1><p>{pipeline_error}</p>", status_code=500)
    if not pipeline_finished_processing or not os.path.exists(report_path):
        return HTMLResponse(content="<h1>Report is being generated</h1><p>Please try again in a few moments.</p>", status_code=202)
        
    try:
        with open(report_path, encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content, status_code=200)
    except Exception as e:
        return HTMLResponse(content=f"<h1>Could not load report</h1><p>{str(e)}</p>", status_code=500)

@app.get("/charts/{filename}")
def get_chart(filename: str):
    if pipeline_error:
        return JSONResponse(status_code=500, content={"error": "Data processing failed, charts may not be available.", "details": pipeline_error})
    
    file_path = f"charts/{filename}"
    # Проверяем pipeline_finished_processing, т.к. папка charts может существовать, но быть пустой до окончания пайплайна
    if not pipeline_finished_processing or not os.path.exists(file_path):
        return JSONResponse(status_code=202, content={"message": "Chart is being generated or not found. Please try again later."})
        
    try:
        return FileResponse(file_path)
    except Exception as e:
        # Это может случиться, если файл ожидается, но что-то пошло не так с его созданием или доступом
        return JSONResponse(status_code=500, content={"error": f"Could not serve chart: {str(e)}"})

# This part is for local development, Render will use the CMD in Dockerfile
if __name__ == "__main__":
    import uvicorn
    print("Starting Uvicorn for local development...")
    # Для локального запуска, запустим пайплайн в основном потоке до старта uvicorn,
    # чтобы поведение было предсказуемым и данные были готовы.
    # Если хочешь имитировать поведение Render (пайплайн в фоне), закомментируй run_prediction_pipeline() здесь
    # и раскомментируй блок startup_event как он был для Render.
    
    # run_prediction_pipeline() # <<< Запускаем синхронно для локальной разработки, если нужно
    
    # Или, чтобы локально было больше похоже на Render, запускаем также в потоке:
    print("Local dev: Triggering prediction pipeline in background.")
    thread = threading.Thread(target=run_pipeline_in_background)
    thread.start()
    
    port = int(os.environ.get("PORT", 8000)) # Default to 8000 if PORT not set
    uvicorn.run(app, host="0.0.0.0", port=port)
