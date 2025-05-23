# Solar PV Forecasting & Dashboard Project

This project forecasts hourly solar PV energy production using meteorological data and visualizes results through charts and an HTML dashboard.

---

## 📁 Folder Structure

```
Prediction_model_hackaton/
├── app/
│   └── run_all.py                # FastAPI app for frontend integration
├── charts/                       # Automatically saved charts (PNG files)
├── data/                         # Input Excel files: meteo_data.xlsx, PV_charac.xlsx
├── model/
│   └── pred_model.py             # Main training + forecasting script
├── reports/
│   ├── generate_charts.py        # Generates and saves charts
│   └── generate_html_report.py   # Generates an HTML report with interpretation
├── output.html                   # Final dashboard combining metrics + charts
├── predicted_aug_forecast.xlsx   # August forecast output
├── test_vs_prediction.xlsx       # Evaluation file for test period (July 22–31)
├── requirements.txt              # Python package dependencies
└── README.md                     # Project documentation
```

---

## 🚀 How to Run

1. Place your input files in `/data/`:
   - `meteo_data.xlsx`
   - `PV_charac.xlsx`

2. Run the main script:
```bash
python model/pred_model.py
```

3. Outputs:
   - Predictions: `predicted_aug_forecast.xlsx`, `test_vs_prediction.xlsx`
   - Charts: saved in `/charts/`
   - Report: `output.html`

---

## 🌐 API (FastAPI)

Launch the API from project root:
```bash
uvicorn app.run_all:app --reload
```

### 📡 API Endpoints

| Endpoint              | Description                             |
|-----------------------|-----------------------------------------|
| `/`                   | Health check                            |
| `/metrics`            | Returns MAE, RMSE, and data count       |
| `/forecast`           | Returns August forecast as JSON         |
| `/report`             | Serves the full `output.html` dashboard |
| `/charts/{filename}`  | Serves individual chart PNG files       |

---

## 🛠 Dependencies

Install dependencies:
```bash
pip install -r requirements.txt
```

---

## 📈 Features

- Forecasts PV output using `HistGradientBoostingRegressor`
- Dynamic metric interpretation (MAE, RMSE, R²)
- Chart generation using `matplotlib` and `seaborn`
- HTML report ready for frontend use
- FastAPI endpoints for web integration

---

## 📌 Notes

- Code is modular and extendable.
- FE devs can use the API to build a landing page with real-time data.

