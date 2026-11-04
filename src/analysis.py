"""Week 5: apparel retail trend analysis and forecasting.

Downloads monthly U.S. clothing and clothing-accessory retail sales from FRED,
compares forecasting methods on a chronological 12-month holdout, and creates
a 12-month forecast plus reproducible CSV/PNG outputs.
"""
from __future__ import annotations

from pathlib import Path
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

SERIES_ID = "MRTSSM448USS"
DATA_URL = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={SERIES_ID}"
OUTPUT_DIR = Path("outputs")
HOLDOUT_MONTHS = 12
FORECAST_MONTHS = 12


def load_data() -> pd.Series:
    """Download and validate the FRED monthly series."""
    print(f"Downloading {SERIES_ID} from FRED...")
    frame = pd.read_csv(DATA_URL)
    if not {"observation_date", SERIES_ID}.issubset(frame.columns):
        # FRED may return a differently named date column in alternate formats.
        date_col = next((c for c in frame.columns if c.lower() in {"observation_date", "date"}), None)
        value_col = SERIES_ID if SERIES_ID in frame.columns else next(
            (c for c in frame.columns if c != date_col), None
        )
        if date_col is None or value_col is None:
            raise ValueError(f"Unexpected data columns: {list(frame.columns)}")
    else:
        date_col, value_col = "observation_date", SERIES_ID

    dates = pd.to_datetime(frame[date_col], errors="coerce")
    values = pd.to_numeric(frame[value_col], errors="coerce")
    data = pd.Series(values.to_numpy(), index=dates, name="sales_millions")
    data = data[~data.index.isna()].dropna().sort_index()
    data = data[~data.index.duplicated(keep="last")]
    data = data.asfreq("MS").interpolate(method="time", limit=1)
    data = data.dropna()
    if len(data) < 48:
        raise ValueError("At least 48 monthly observations are needed for seasonal forecasting.")
    if (data <= 0).any():
        warnings.warn("Non-positive sales values found; MAPE will ignore zero actuals.")
    return data


def calculate_metrics(actual: pd.Series, predicted: pd.Series) -> dict[str, float]:
    aligned = pd.concat([actual.rename("actual"), predicted.rename("predicted")], axis=1).dropna()
    error = aligned["actual"] - aligned["predicted"]
    nonzero = aligned["actual"].abs() > 1e-9
    mape = (error[nonzero].abs() / aligned.loc[nonzero, "actual"].abs()).mean() * 100
    return {
        "MAE": float(error.abs().mean()),
        "RMSE": float(np.sqrt(np.mean(np.square(error)))),
        "MAPE_percent": float(mape) if pd.notna(mape) else float("nan"),
    }


def moving_average_forecast(train: pd.Series, horizon: int, window: int = 12) -> pd.Series:
    """Recursive forecast: each future point uses the latest window, including prior predictions."""
    history = list(train.astype(float))
    forecasts = []
    for _ in range(horizon):
        value = float(np.mean(history[-window:]))
        forecasts.append(value)
        history.append(value)
    index = pd.date_range(train.index[-1] + pd.offsets.MonthBegin(1), periods=horizon, freq="MS")
    return pd.Series(forecasts, index=index, name="moving_average_12m")


def seasonal_naive_forecast(train: pd.Series, horizon: int = 12) -> pd.Series:
    """Repeat the most recent observed seasonal cycle."""
    values = [float(train.iloc[-12 + (i % 12)]) for i in range(horizon)]
    index = pd.date_range(train.index[-1] + pd.offsets.MonthBegin(1), periods=horizon, freq="MS")
    return pd.Series(values, index=index, name="seasonal_naive")


def holt_winters_forecast(train: pd.Series, horizon: int) -> pd.Series:
    """Fit additive trend and additive 12-month seasonality."""
    model = ExponentialSmoothing(
        train.astype(float),
        trend="add",
        seasonal="add",
        seasonal_periods=12,
        initialization_method="estimated",
    )
    fitted = model.fit(optimized=True)
    forecast = fitted.forecast(horizon)
    forecast.name = "holt_winters"
    return forecast


def save_historical_outputs(data: pd.Series) -> None:
    historical = data.to_frame()
    historical["month_over_month_percent"] = historical["sales_millions"].pct_change() * 100
    historical["year_over_year_percent"] = historical["sales_millions"].pct_change(12) * 100
    historical["12_month_moving_average"] = historical["sales_millions"].rolling(12).mean()
    historical.to_csv(OUTPUT_DIR / "historical_sales.csv", index_label="date")

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(data.index, data.values, label="Monthly sales", linewidth=1.4)
    ax.plot(data.index, data.rolling(12).mean(), label="12-month moving average", linewidth=2)
    ax.set(title="U.S. Clothing and Clothing Accessory Retail Sales", xlabel="Month",
           ylabel="Millions of dollars (seasonally adjusted)")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "historical_trend.png", dpi=160)
    plt.close(fig)


def evaluate_models(data: pd.Series) -> tuple[pd.DataFrame, pd.DataFrame]:
    train, test = data.iloc[:-HOLDOUT_MONTHS], data.iloc[-HOLDOUT_MONTHS:]
    predictions = pd.DataFrame(index=test.index)
    predictions["actual"] = test
    predictions["seasonal_naive"] = seasonal_naive_forecast(train, len(test)).to_numpy()
    predictions["moving_average_12m"] = moving_average_forecast(train, len(test)).to_numpy()
    predictions["holt_winters"] = holt_winters_forecast(train, len(test)).to_numpy()

    rows = []
    for model_name in ("seasonal_naive", "moving_average_12m", "holt_winters"):
        metrics = calculate_metrics(test, predictions[model_name])
        rows.append({"model": model_name, **metrics})
    comparison = pd.DataFrame(rows).sort_values("RMSE")
    comparison.to_csv(OUTPUT_DIR / "model_comparison.csv", index=False)
    predictions.to_csv(OUTPUT_DIR / "holdout_forecasts.csv", index_label="date")

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(predictions.index, predictions["actual"], marker="o", label="Actual")
    for col in ("seasonal_naive", "moving_average_12m", "holt_winters"):
        ax.plot(predictions.index, predictions[col], marker=".", label=col.replace("_", " ").title())
    ax.set(title="12-Month Holdout: Actual vs Forecast", xlabel="Month",
           ylabel="Millions of dollars (seasonally adjusted)")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "holdout_comparison.png", dpi=160)
    plt.close(fig)
    return comparison, predictions


def make_future_forecasts(data: pd.Series, comparison: pd.DataFrame) -> pd.DataFrame:
    horizon = FORECAST_MONTHS
    forecasts = pd.DataFrame(index=pd.date_range(
        data.index[-1] + pd.offsets.MonthBegin(1), periods=horizon, freq="MS"
    ))
    forecasts.index.name = "date"
    forecasts["seasonal_naive"] = seasonal_naive_forecast(data, horizon).to_numpy()
    forecasts["moving_average_12m"] = moving_average_forecast(data, horizon).to_numpy()
    forecasts["holt_winters"] = holt_winters_forecast(data, horizon).to_numpy()
    best_model = str(comparison.iloc[0]["model"])
    forecasts["lowest_holdout_RMSE_model"] = best_model
    forecasts["selected_by_holdout_RMSE_forecast"] = forecasts[best_model]
    forecasts.to_csv(OUTPUT_DIR / "12_month_forecasts.csv")

    fig, ax = plt.subplots(figsize=(12, 6))
    recent = data.iloc[-36:]
    ax.plot(recent.index, recent.values, label="Historical sales", linewidth=2)
    for col in ("seasonal_naive", "moving_average_12m", "holt_winters"):
        ax.plot(forecasts.index, forecasts[col], linestyle="--", marker=".", label=col.replace("_", " ").title())
    ax.axvline(data.index[-1], linestyle=":", linewidth=1)
    ax.set(title="12-Month Apparel Retail Sales Forecast Scenarios", xlabel="Month",
           ylabel="Millions of dollars (seasonally adjusted)")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "12_month_forecasts.png", dpi=160)
    plt.close(fig)
    return forecasts


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    data = load_data()
    save_historical_outputs(data)
    comparison, _ = evaluate_models(data)
    forecasts = make_future_forecasts(data, comparison)

    print("\nData coverage:", data.index.min().date(), "to", data.index.max().date())
    print("Observations:", len(data))
    print("\nHoldout model comparison (lower errors are better):")
    print(comparison.to_string(index=False, float_format=lambda x: f"{x:,.3f}"))
    print("\n12-month forecast preview:")
    print(forecasts.head().to_string())
    print(f"\nOutputs saved to: {OUTPUT_DIR.resolve()}")
    print("Interpret results cautiously; these are aggregate U.S. nominal retail sales.")


if __name__ == "__main__":
    main()
